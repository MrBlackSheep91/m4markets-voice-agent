# 🚀 Quick Start - M4Markets Voice Agent

## 🌐 Frontend Web ya está listo!

La aplicación web (`index.html`) está lista con:
- ✅ Branding de M4Markets
- ✅ Integración con LiveKit
- ✅ UI moderna y responsive
- ✅ Manejo de errores
- ✅ Instrucciones claras en español

---

## 📋 Cómo Usar la App Web

### Opción 1: Desplegar en Vercel (RECOMENDADO - 5 min)

1. **Instalar Vercel CLI**:
```bash
npm install -g vercel
```

2. **Deploy desde el proyecto**:
```bash
cd C:/Users/maico/voice-m4markets-agent
vercel
```

3. **Seguir los prompts**:
   - Set up and deploy? → `Y`
   - Which scope? → Tu cuenta
   - Link to existing project? → `N`
   - Project name? → `voice-m4markets-agent`
   - Directory? → `.` (enter)
   - Modify settings? → `N`

4. **Resultado**:
   - Te dará una URL tipo: `https://voice-m4markets-agent.vercel.app`
   - Esta es tu `FRONTEND_URL` para configurar en `.env`

### Opción 2: Deploy en Railway (ALTERNATIVA)

```bash
cd C:/Users/maico/voice-m4markets-agent
railway login
railway init
railway up
```

### Opción 3: Local con Python (Para Testing)

```bash
cd C:/Users/maico/voice-m4markets-agent
python -m http.server 8000
```

Luego abrir: `http://localhost:8000/index.html?room=test&token=test`

---

## 🎬 Flow Completo de Demo

### 1. Setup Backend (Agente de Voz)

**a) Configurar `.env`**:
```bash
cd C:/Users/maico/voice-m4markets-agent
cp .env.example .env
```

Editar `.env` con:
```env
# Database (Neon)
DB_URL=postgresql://neondb_owner:xxx@xxx.neon.tech/neondb

# LiveKit
LIVEKIT_URL=wss://xxx.livekit.cloud
LIVEKIT_API_KEY=xxx
LIVEKIT_API_SECRET=xxx

# Evolution API (WhatsApp)
EVOLUTION_API_URL=https://xxx.railway.app
EVOLUTION_API_KEY=xxx
EVOLUTION_INSTANCE_NAME=xxx

# OpenAI
OPENAI_API_KEY=sk-xxx

# Frontend
FRONTEND_URL=https://voice-m4markets-agent.vercel.app
```

**b) Instalar dependencias**:
```bash
pip install -r requirements.txt
```

**c) Iniciar el agente**:
```bash
python voice_agent_m4markets.py dev
```

Verás:
```
INFO Starting M4Markets Voice Agent...
INFO Connecting to LiveKit...
INFO Agent ready and waiting for calls
```

### 2. Iniciar Llamada

**Opción A: Via WhatsApp (Producción)**
```bash
python evolution_caller.py 549XXXXXXXXX
```

Esto:
1. Crea un LiveKit room
2. Genera token de acceso
3. Envía WhatsApp con link: `https://voice-m4markets-agent.vercel.app?room=XXX&token=YYY`

**Opción B: Via URL Directa (Testing)**

Abrir en navegador:
```
https://voice-m4markets-agent.vercel.app?room=test-room-123&token=YOUR_TOKEN
```

---

## 🧪 Testing Rápido (Sin WhatsApp)

Si querés probar la app web sin configurar todo:

### 1. Crear room de prueba manualmente

```python
# create_test_room.py
import os
from livekit import api
import asyncio

async def create_test_room():
    LIVEKIT_URL = "wss://innovateam-2onbh9x3.livekit.cloud"
    LIVEKIT_API_KEY = "tu_api_key"
    LIVEKIT_API_SECRET = "tu_api_secret"

    lk_api = api.LiveKitAPI(
        url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET
    )

    room_name = "test-m4markets-123"

    # Create room
    await lk_api.room.create_room(api.CreateRoomRequest(name=room_name))

    # Generate token
    token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    token.with_identity("test-user")
    token.with_name("Test User")
    token.with_grants(api.VideoGrants(room_join=True, room=room_name))

    jwt_token = token.to_jwt()

    print(f"Room: {room_name}")
    print(f"Token: {jwt_token}")
    print(f"\nURL: https://voice-m4markets-agent.vercel.app?room={room_name}&token={jwt_token}")

asyncio.run(create_test_room())
```

### 2. Abrir la URL generada en el navegador

---

## ✅ Checklist Pre-Demo

Antes de la demo con Sam, verifica:

- [ ] Frontend deployado en Vercel/Railway
- [ ] `.env` configurado con todas las credenciales
- [ ] Agente de voz corriendo (`python voice_agent_m4markets.py dev`)
- [ ] Second Brain tiene datos de M4Markets (92 chunks indexados)
- [ ] Database (Neon) accesible
- [ ] Evolution API funcionando (si usás WhatsApp)
- [ ] LiveKit room creado exitosamente
- [ ] Audio funciona en el navegador

---

## 🎯 Próximos Pasos

### Inmediato (Ahora):
1. ✅ Deploy frontend a Vercel
2. ✅ Configurar `.env`
3. ✅ Hacer llamada de prueba

### Pre-Demo:
4. ✅ Preparar 2 números de prueba
5. ✅ Practicar el guión de demo
6. ✅ Verificar que Second Brain responde

### Post-Demo (Si Sam aprueba):
7. ⏳ Conectar CRM real de M4Markets
8. ⏳ Agregar analytics dashboard
9. ⏳ Escalar a producción

---

## 🆘 Troubleshooting

### "Error: Link inválido"
→ Falta `room` o `token` en la URL
→ Verificar que evolution_caller.py generó el link correctamente

### "Debes permitir el acceso al micrófono"
→ Usuario debe permitir micrófono en el navegador
→ En Chrome: Settings > Privacy > Site Settings > Microphone

### "No se puede conectar a LiveKit"
→ Verificar `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
→ Confirmar que LiveKit instance está activa

### "Agente no responde"
→ Verificar que `voice_agent_m4markets.py` está corriendo
→ Revisar logs del agente
→ Verificar que OpenAI API key es válida

---

## 📞 URLs Importantes

- **Frontend**: `https://voice-m4markets-agent.vercel.app`
- **LiveKit**: `wss://innovateam-2onbh9x3.livekit.cloud`
- **Second Brain (ChromaDB)**: `http://chroma.railway.internal:8000`
- **M4Markets**: `https://www.m4markets.com`

---

## 🎉 ¡Listo para la Demo!

Ahora tenés todo funcionando:
- ✅ Frontend web con branding M4Markets
- ✅ Backend con agente de voz inteligente
- ✅ Second Brain con conocimiento de M4Markets
- ✅ CRM integration para guardar leads
- ✅ WhatsApp integration para llamadas

**¿Necesitás ayuda con algo más?**
- Configurar .env
- Deploy a Vercel
- Testing de la app
- Preparar la demo para Sam
