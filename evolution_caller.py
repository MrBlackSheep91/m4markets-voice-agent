"""
Evolution API Caller for M4Markets Voice Agent
Initiates voice calls via WhatsApp using Evolution API + LiveKit
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv
from livekit import api
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evolution-caller")

# Environment variables
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME")

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://voice-m4markets-agent.vercel.app")


async def create_livekit_room(phone: str) -> dict:
    """
    Create LiveKit room and generate access token

    Args:
        phone: Phone number for the room (used as identifier)

    Returns:
        Dict with room_name and token
    """
    try:
        room_name = f"m4markets-{phone}-{int(asyncio.get_event_loop().time())}"

        # Create LiveKit API client
        lk_api = api.LiveKitAPI(
            url=LIVEKIT_URL,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET
        )

        # Create room
        await lk_api.room.create_room(api.CreateRoomRequest(name=room_name))

        # Generate token for participant
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        token.with_identity(f"lead-{phone}")
        token.with_name(f"Lead {phone}")
        token.with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
            )
        )

        jwt_token = token.to_jwt()

        logger.info(f"Created room: {room_name}")

        return {
            "success": True,
            "room_name": room_name,
            "token": jwt_token,
            "url": f"{FRONTEND_URL}?room={room_name}&token={jwt_token}"
        }

    except Exception as e:
        logger.error(f"Error creating LiveKit room: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def send_whatsapp_invitation(phone: str, room_url: str) -> dict:
    """
    Send WhatsApp message with room invitation link

    Args:
        phone: Destination phone number (with country code, e.g., 549XXXXXXXXX)
        room_url: LiveKit room URL to send

    Returns:
        Success status
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE_NAME}",
                headers={
                    "apikey": EVOLUTION_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "number": phone,
                    "text": f"""¡Hola! 👋

Te contacto de M4Markets, broker de Forex regulado internacionalmente.

Quería conversar contigo sobre nuestras cuentas de trading con spreads desde 0.0 pips y depósito mínimo de solo $5 USD.

¿Tenés unos minutos para una llamada rápida?

Hacé click acá para conectarnos por voz:
{room_url}

¡Gracias!
M4Markets Team
"""
                }
            )

            if response.status_code == 200:
                logger.info(f"WhatsApp invitation sent to {phone}")
                return {
                    "success": True,
                    "phone": phone,
                    "message": "Invitation sent"
                }
            else:
                logger.error(f"Error sending WhatsApp: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }

    except Exception as e:
        logger.error(f"Error sending WhatsApp invitation: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def initiate_call(phone: str) -> dict:
    """
    Initiate voice call to a phone number via WhatsApp

    Args:
        phone: Phone number with country code (e.g., 5491123456789)

    Returns:
        Result with room info and status
    """
    logger.info(f"Initiating call to {phone}")

    # Step 1: Create LiveKit room
    room_result = await create_livekit_room(phone)

    if not room_result["success"]:
        return room_result

    # Step 2: Send WhatsApp invitation
    whatsapp_result = await send_whatsapp_invitation(phone, room_result["url"])

    if not whatsapp_result["success"]:
        return {
            "success": False,
            "error": "Room created but WhatsApp invitation failed",
            "room_info": room_result,
            "whatsapp_error": whatsapp_result["error"]
        }

    return {
        "success": True,
        "phone": phone,
        "room_name": room_result["room_name"],
        "room_url": room_result["url"],
        "message": f"Call invitation sent to {phone}"
    }


async def batch_call(phone_numbers: list[str]) -> list[dict]:
    """
    Initiate calls to multiple phone numbers

    Args:
        phone_numbers: List of phone numbers

    Returns:
        List of results for each call
    """
    tasks = [initiate_call(phone) for phone in phone_numbers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return [
        r if not isinstance(r, Exception) else {"success": False, "error": str(r)}
        for r in results
    ]


# CLI Usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python evolution_caller.py <phone_number> [phone_number2] [phone_number3]...")
        print("Example: python evolution_caller.py 5491123456789")
        print("Example (batch): python evolution_caller.py 5491123456789 5491198765432")
        sys.exit(1)

    phones = sys.argv[1:]

    async def main():
        if len(phones) == 1:
            result = await initiate_call(phones[0])
            print(f"\nResult: {result}")
        else:
            results = await batch_call(phones)
            print(f"\nBatch results:")
            for i, result in enumerate(results):
                print(f"{i+1}. {phones[i]}: {result}")

    asyncio.run(main())
