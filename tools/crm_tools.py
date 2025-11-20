"""
CRM Tools for M4Markets Voice Agent
Manages leads, conversations, and callbacks in Neon PostgreSQL
"""

import asyncpg
import os
from datetime import datetime
from typing import Dict, Optional, List
import logging
from livekit.agents import function_tool

logger = logging.getLogger(__name__)

# Database connection
DB_URL = os.getenv("DB_URL")


async def get_db_connection():
    """Create database connection"""
    return await asyncpg.connect(DB_URL)


@function_tool
async def get_lead_history(phone: str) -> Dict:
    """
    Retrieve lead history from CRM

    Args:
        phone: Phone number of the lead

    Returns:
        Dict with lead information, previous conversations, and notes
    """
    try:
        conn = await get_db_connection()

        # Get lead info
        lead = await conn.fetchrow("""
            SELECT * FROM leads
            WHERE phone = $1
            ORDER BY last_contact_at DESC NULLS LAST
            LIMIT 1
        """, phone)

        if not lead:
            await conn.close()
            return {
                "found": False,
                "phone": phone,
                "is_new_lead": True,
                "message": "Nuevo prospecto - primera interacción"
            }

        # Get previous conversations
        conversations = await conn.fetch("""
            SELECT id, room_name, duration_seconds, outcome, notes, created_at
            FROM conversations
            WHERE lead_id = $1
            ORDER BY created_at DESC
            LIMIT 5
        """, lead['id'])

        # Get conversation notes
        notes = await conn.fetch("""
            SELECT note_type, content, created_at
            FROM conversation_notes
            WHERE lead_id = $1
            ORDER BY created_at DESC
            LIMIT 10
        """, lead['id'])

        await conn.close()

        return {
            "found": True,
            "is_new_lead": False,
            "lead_id": str(lead['id']),
            "name": lead.get('name'),
            "email": lead.get('email'),
            "trading_experience": lead.get('trading_experience'),  # New field for forex
            "risk_tolerance": lead.get('risk_tolerance'),  # New field
            "preferred_account_type": lead.get('preferred_account_type'),  # New field
            "capital_range": f"${lead.get('investment_amount_min')} - ${lead.get('investment_amount_max')}",
            "qualification": lead.get('qualification'),
            "score": lead.get('score', 0),
            "status": lead.get('status'),
            "last_contact": str(lead.get('last_contact_at')),
            "conversations_count": len(conversations),
            "previous_pain_points": [n['content'] for n in notes if n['note_type'] == 'pain_point'],
            "previous_objections": [n['content'] for n in notes if n['note_type'] == 'objection'],
            "interests": [n['content'] for n in notes if n['note_type'] == 'interest']
        }

    except Exception as e:
        logger.error(f"Error getting lead history: {e}")
        return {
            "found": False,
            "error": str(e),
            "phone": phone
        }


@function_tool
async def save_conversation_note(
    phone: str,
    note_type: str,
    content: str
) -> Dict:
    """
    Save a note from the conversation

    Args:
        phone: Lead phone number
        note_type: Type of note (pain_point, objection, interest, budget, timeline, trading_preference)
        content: Note content

    Returns:
        Success status
    """
    try:
        conn = await get_db_connection()

        # Get or create lead
        lead = await conn.fetchrow("SELECT id FROM leads WHERE phone = $1", phone)

        if not lead:
            # Create basic lead record
            lead_id = await conn.fetchval("""
                INSERT INTO leads (phone, status, source, created_at)
                VALUES ($1, 'new', 'voice_call', NOW())
                RETURNING id
            """, phone)
        else:
            lead_id = lead['id']

        # Insert note
        await conn.execute("""
            INSERT INTO conversation_notes (lead_id, note_type, content, created_at)
            VALUES ($1, $2, $3, NOW())
        """, lead_id, note_type, content)

        await conn.close()

        return {
            "success": True,
            "lead_id": str(lead_id),
            "note_type": note_type,
            "message": f"Nota guardada: {note_type}"
        }

    except Exception as e:
        logger.error(f"Error saving note: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@function_tool
async def qualify_and_save_lead(
    phone: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    trading_experience: Optional[str] = None,  # principiante, intermedio, avanzado
    capital_available: Optional[int] = None,  # USD
    risk_tolerance: Optional[str] = None,  # bajo, medio, alto
    preferred_account_type: Optional[str] = None,  # Standard, Raw, Premium, Dynamic
    urgency: Optional[str] = None,  # baja, media, alta
    broker_actual: Optional[str] = None,
    pain_points: Optional[List[str]] = None
) -> Dict:
    """
    Qualify and save lead with forex-specific fields

    Args:
        phone: Lead phone number
        name: Lead name
        email: Email address
        trading_experience: Trading experience level
        capital_available: Capital in USD
        risk_tolerance: Risk tolerance level
        preferred_account_type: Preferred M4Markets account type
        urgency: Urgency level
        broker_actual: Current broker they use
        pain_points: List of pain points identified

    Returns:
        Qualification result with score and recommended action
    """
    try:
        conn = await get_db_connection()

        # Calculate qualification score (0-100)
        score = 0

        # Capital scoring (40 points max)
        if capital_available:
            if capital_available >= 5000:
                score += 40
            elif capital_available >= 1000:
                score += 30
            elif capital_available >= 200:
                score += 20
            elif capital_available >= 5:
                score += 10

        # Experience scoring (20 points max)
        if trading_experience:
            exp_lower = trading_experience.lower()
            if "avanzado" in exp_lower:
                score += 20
            elif "intermedio" in exp_lower:
                score += 15
            elif "principiante" in exp_lower:
                score += 10

        # Urgency scoring (20 points max)
        if urgency:
            urg_lower = urgency.lower()
            if "alta" in urg_lower or "urgente" in urg_lower:
                score += 20
            elif "media" in urg_lower:
                score += 10
            elif "baja" in urg_lower:
                score += 5

        # Pain points scoring (20 points max)
        if pain_points and len(pain_points) >= 3:
            score += 20
        elif pain_points and len(pain_points) >= 1:
            score += 10

        # Determine qualification
        if score >= 70:
            qualification = "HOT"
            recommended_action = "immediate_handoff"
        elif score >= 40:
            qualification = "WARM"
            recommended_action = "schedule_callback"
        else:
            qualification = "COLD"
            recommended_action = "whatsapp_followup"

        # Upsert lead
        lead_id = await conn.fetchval("""
            INSERT INTO leads (
                phone, name, email,
                trading_experience, investment_amount_min, investment_amount_max,
                risk_tolerance, preferred_account_type,
                urgency, qualification, score, status,
                source, last_contact_at, updated_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, NOW(), NOW())
            ON CONFLICT (phone)
            DO UPDATE SET
                name = COALESCE(EXCLUDED.name, leads.name),
                email = COALESCE(EXCLUDED.email, leads.email),
                trading_experience = COALESCE(EXCLUDED.trading_experience, leads.trading_experience),
                investment_amount_min = COALESCE(EXCLUDED.investment_amount_min, leads.investment_amount_min),
                investment_amount_max = COALESCE(EXCLUDED.investment_amount_max, leads.investment_amount_max),
                risk_tolerance = COALESCE(EXCLUDED.risk_tolerance, leads.risk_tolerance),
                preferred_account_type = COALESCE(EXCLUDED.preferred_account_type, leads.preferred_account_type),
                urgency = COALESCE(EXCLUDED.urgency, leads.urgency),
                qualification = EXCLUDED.qualification,
                score = EXCLUDED.score,
                status = EXCLUDED.status,
                last_contact_at = NOW(),
                updated_at = NOW()
            RETURNING id
        """,
            phone, name, email,
            trading_experience, capital_available, capital_available,
            risk_tolerance, preferred_account_type,
            urgency, qualification, score, 'qualified',
            'voice_call'
        )

        # Save broker info as note if provided
        if broker_actual:
            await conn.execute("""
                INSERT INTO conversation_notes (lead_id, note_type, content, created_at)
                VALUES ($1, 'current_broker', $2, NOW())
            """, lead_id, broker_actual)

        await conn.close()

        return {
            "success": True,
            "lead_id": str(lead_id),
            "qualification": qualification,
            "score": score,
            "recommended_action": recommended_action,
            "message": f"Lead calificado como {qualification} con score {score}/100"
        }

    except Exception as e:
        logger.error(f"Error qualifying lead: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@function_tool
async def schedule_callback(
    phone: str,
    preferred_time: str,
    notes: Optional[str] = None,
    timezone: str = "America/Argentina/Buenos_Aires"
) -> Dict:
    """
    Schedule a callback for a lead

    Args:
        phone: Lead phone number
        preferred_time: Preferred callback time (natural language)
        notes: Additional notes
        timezone: Timezone for callback

    Returns:
        Callback confirmation
    """
    try:
        conn = await get_db_connection()

        # Get lead
        lead = await conn.fetchrow("SELECT id FROM leads WHERE phone = $1", phone)

        if not lead:
            await conn.close()
            return {
                "success": False,
                "error": "Lead not found"
            }

        # Create callback record
        callback_id = await conn.fetchval("""
            INSERT INTO callbacks (lead_id, preferred_time, timezone, status, notes, created_at)
            VALUES ($1, $2, $3, 'pending', $4, NOW())
            RETURNING id
        """, lead['id'], preferred_time, timezone, notes)

        await conn.close()

        return {
            "success": True,
            "callback_id": str(callback_id),
            "lead_id": str(lead['id']),
            "preferred_time": preferred_time,
            "message": f"Callback agendado para {preferred_time}"
        }

    except Exception as e:
        logger.error(f"Error scheduling callback: {e}")
        return {
            "success": False,
            "error": str(e)
        }


__all__ = [
    'get_lead_history',
    'save_conversation_note',
    'qualify_and_save_lead',
    'schedule_callback'
]
