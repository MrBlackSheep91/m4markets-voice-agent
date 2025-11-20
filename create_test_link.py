#!/usr/bin/env python3
"""
Genera un link de prueba para M4Markets Voice Agent
Usa las mismas credenciales de Break and Bounce
"""

import os
from dotenv import load_dotenv
from livekit import api
from datetime import timedelta

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8080")

def create_test_link():
    """Crea un link de prueba para testing local"""

    # Nombre del room
    room_name = "m4markets-test-demo"

    # Crear token
    token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    token.with_identity("test-user")
    token.with_name("Test User M4Markets")
    token.with_grants(
        api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True
        )
    ).with_ttl(timedelta(hours=2))

    jwt_token = token.to_jwt()

    # Generar URL
    test_url = f"{FRONTEND_URL}/index.html?room={room_name}&token={jwt_token}"

    print("\n" + "="*70)
    print("M4MARKETS VOICE AGENT - TEST LINK")
    print("="*70)
    print(f"\nRoom: {room_name}")
    print(f"LiveKit URL: {LIVEKIT_URL}")
    print(f"\nABRI ESTA URL EN TU NAVEGADOR:\n")
    print(f"   {test_url}")
    print("\n" + "="*70)
    print("\nINSTRUCCIONES:")
    print("   1. Abri la URL en Chrome/Firefox")
    print("   2. Permitir acceso al microfono")
    print("   3. Click en 'Unirse a la llamada'")
    print("   4. (Opcional) Inicia el agente: python voice_agent_m4markets.py dev")
    print("\n" + "="*70 + "\n")

    return test_url

if __name__ == "__main__":
    create_test_link()
