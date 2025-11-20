#!/usr/bin/env python3
"""
Script rápido para generar link EN INGLÉS para Sam
"""

import os
import sys
from dotenv import load_dotenv
from livekit import api
from datetime import timedelta
import time

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
NETLIFY_URL = "https://m4markets-voice-sales.netlify.app"

# Nombre del cliente (puedes cambiarlo)
client_name = sys.argv[1] if len(sys.argv) > 1 else "Sam Chaney"

# Room único
room_name = f"m4markets-{int(time.time())}"

# Token
token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
token.with_identity(client_name.lower().replace(" ", "-"))
token.with_name(client_name)
token.with_grants(
    api.VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True
    )
).with_ttl(timedelta(hours=2))

jwt_token = token.to_jwt()

# URL EN INGLÉS
client_url = f"{NETLIFY_URL}?room={room_name}&token={jwt_token}&lang=en&mode=full"

print("\n" + "="*80)
print("M4MARKETS VOICE AGENT - ENGLISH LINK FOR SAM")
print("="*80)
print(f"\nClient: {client_name}")
print(f"Room: {room_name}")
print(f"Language: ENGLISH")
print(f"\n>>> SEND THIS LINK TO SAM:\n")
print(f"   {client_url}")
print("\n" + "="*80)
print("\n>>> BEFORE SAM OPENS THE LINK, START THE AGENT:")
print("   cd C:\\Users\\maico\\voice-m4markets-agent")
print("   python voice_agent_simple.py dev")
print("\n" + "="*80 + "\n")
