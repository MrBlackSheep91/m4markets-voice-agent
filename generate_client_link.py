#!/usr/bin/env python3
"""
Genera links de cliente para M4Markets Voice Agent
Con room y token válidos para evitar error "Link inválido"
"""

import os
import sys
from dotenv import load_dotenv
from livekit import api
from datetime import timedelta

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# URLs del frontend
NETLIFY_URL = "https://m4markets-voice-sales.netlify.app"
LOCALHOST_URL = "http://localhost:8080"

def generate_link(client_name: str, use_localhost: bool = False, language: str = "es", mode: str = "full"):
    """
    Genera un link para que un cliente se una a la llamada

    Args:
        client_name: Nombre del cliente (ej: "Juan Perez")
        use_localhost: Si True usa localhost, si False usa Netlify
        language: "es" o "en"
        mode: "full" (página completa) o "widget" (botón flotante)
    """

    # Generar room name único basado en timestamp
    import time
    room_name = f"m4markets-{int(time.time())}"

    # Crear token de acceso
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

    # Elegir URL base
    base_url = LOCALHOST_URL if use_localhost else NETLIFY_URL

    # Construir URL completa
    client_url = f"{base_url}?room={room_name}&token={jwt_token}&lang={language}&mode={mode}"

    print("\n" + "="*80)
    print("M4MARKETS VOICE AGENT - LINK DE CLIENTE")
    print("="*80)
    print(f"\nCliente: {client_name}")
    print(f"Room: {room_name}")
    print(f"Idioma: {language.upper()}")
    print(f"Modo: {mode.upper()}")
    print(f"LiveKit URL: {LIVEKIT_URL}")
    print(f"\n>>> ENVIA ESTE LINK AL CLIENTE:\n")
    print(f"   {client_url}")
    print("\n" + "="*80)
    print("\n>>> INSTRUCCIONES PARA EL CLIENTE:")
    print("   1. Abrir el link en Chrome, Firefox o Safari")
    print("   2. Permitir acceso al microfono cuando lo solicite")
    print("   3. Click en 'Unirse a la llamada'")
    print("   4. Esperar a que Maicol (el agente) se una")
    print("\n>>> PARA INICIAR EL AGENTE:")
    print("   cd voice-m4markets-agent")
    print("   python voice_agent_simple.py dev")
    print("\n" + "="*80 + "\n")

    return client_url


if __name__ == "__main__":
    # Ejemplos de uso:

    # Modo por defecto: Netlify, español, página completa
    if len(sys.argv) > 1:
        client_name = " ".join(sys.argv[1:])
    else:
        client_name = "Cliente Demo"

    # Link en español, página completa (producción)
    print("\n>>> LINK DE PRODUCCION (Netlify):")
    generate_link(client_name, use_localhost=False, language="es", mode="full")

    # Link en ingles para Sam
    # generate_link("Sam Johnson", use_localhost=False, language="en", mode="full")

    # Link con widget flotante
    # generate_link("Test User", use_localhost=False, language="es", mode="widget")

    # Link para desarrollo local
    # generate_link("Local Test", use_localhost=True, language="es", mode="full")
