# M4Markets Voice Agent - Optimization Guide

## 📊 Performance Metrics & Cost Tracking

El agente ahora incluye un sistema completo de métricas que trackea:

### Métricas Trackeadas
- ✅ **Costos en tiempo real** (STT, LLM, TTS)
- ✅ **Latencia de respuesta** (primera respuesta y promedio)
- ✅ **Uso de herramientas** (cuántas veces se llama cada tool)
- ✅ **Duración de calls**
- ✅ **Costo por minuto** y **costo total**

### Dónde Ver las Métricas

Las métricas se logean automáticamente en los logs de Railway:

```
📊 Call Metrics Summary - call_m4markets-1763670069
├─ Duration: 5.23 min
├─ Total Cost: $0.2145
├─ Cost/Minute: $0.0410
├─ STT: $0.0314 (52.4s)
├─ LLM: $0.1203 (2,450 in / 1,820 out)
├─ TTS: $0.0628 (4,189 chars)
├─ Tool Calls: 8
├─ First Response: 1.2s
└─ Avg Response: 1.8s
```

### Logs Detallados de Tool Calls

Cada vez que el agente usa una herramienta, verás:

```
🔧 Tool called: query_m4markets_knowledge | Call: call_xxx
✅ Tool COMPLETED: query_m4markets_knowledge (0.34s)

🔧 Tool called: qualify_and_save_lead | Call: call_xxx
✅ Tool COMPLETED: qualify_and_save_lead (1.12s)
```

---

## ⚡ Optimización de Latencia

### Configuración Actual (Optimizada)

```python
# Voice: "nova" - Clara y rápida
# Speed: 1.15x - 15% más rápido que normal
# Language: "es" - Optimizado para español
```

### Opciones de Voz Disponibles

#### 🚀 Ultra Baja Latencia (Fastest)
```env
AGENT_VOICE=echo
VOICE_SPEED=1.25
```
- **Latencia**: ⭐⭐⭐⭐⭐ (Excelente)
- **Realismo**: ⭐⭐⭐ (Bueno)
- **Uso recomendado**: High-volume calls, cost-sensitive

#### ⚖️ Balanceado (Recommended - DEFAULT)
```env
AGENT_VOICE=nova
VOICE_SPEED=1.15
```
- **Latencia**: ⭐⭐⭐⭐ (Muy Buena)
- **Realismo**: ⭐⭐⭐⭐ (Muy Bueno)
- **Uso recomendado**: General purpose, best balance

#### 🎭 Alta Calidad (More Realistic)
```env
AGENT_VOICE=fable
VOICE_SPEED=1.0
```
- **Latencia**: ⭐⭐⭐ (Buena)
- **Realismo**: ⭐⭐⭐⭐⭐ (Excelente)
- **Uso recomendado**: Premium leads, demos

#### 🌟 Natural (Most Human-Like)
```env
AGENT_VOICE=shimmer
VOICE_SPEED=0.95
```
- **Latencia**: ⭐⭐ (Aceptable)
- **Realismo**: ⭐⭐⭐⭐⭐ (Máximo)
- **Uso recomendado**: VIP clients, special cases

### Factores de Latencia

1. **Network RTT** (~100-300ms) - No controlable
2. **STT Processing** (~200-500ms) - Optimizado con `language="es"`
3. **LLM Processing** (~500-1500ms) - Usando gpt-4o-mini (fastest)
4. **TTS Generation** (~300-800ms) - Optimizado con `speed=1.15`
5. **Tool Calls** (~200-2000ms) - Depende de la herramienta

**Latencia Total Típica**: 1.5-3.5 segundos desde que el usuario termina de hablar hasta que escucha la respuesta del agente.

---

## 💰 Cost Analysis

### Pricing Breakdown (OpenAI - 2025)

| Service | Price | Notes |
|---------|-------|-------|
| Whisper STT | $0.006/minute | ~$0.36/hora |
| GPT-4o-mini Input | $0.15/1M tokens | ~600 tokens/min |
| GPT-4o-mini Output | $0.60/1M tokens | ~450 tokens/min |
| TTS Standard | $15/1M chars | ~800 chars/min |

### Cost Per Call Estimates

| Call Type | Duration | Estimated Cost | Tools Used |
|-----------|----------|----------------|------------|
| **Quick Inquiry** | 1-2 min | $0.03-0.06 | 1-2 |
| **Standard Qualification** | 5-8 min | $0.15-0.30 | 5-8 |
| **Hot Lead** | 10-15 min | $0.40-0.70 | 8-12 |
| **Complex Consultation** | 15-20 min | $0.70-1.10 | 12-15 |

### Cost Optimization Tips

1. **Use Faster Voice**: `echo` o `nova` reduce call duration by 10-15%
2. **Optimize System Instructions**: Shorter prompts = less LLM tokens
3. **Cache Common Responses**: Pre-generate FAQs
4. **Set Timeouts**: Auto-disconnect inactive calls after 2-3 min
5. **Tool Efficiency**: Optimize database queries in tools

### Monthly Cost Projections

**Assumptions**:
- Average call: 7 minutes
- Average cost per call: $0.25
- Conversion rate to qualified lead: 40%

| Calls/Day | Calls/Month | Total Cost | Cost/Qualified Lead |
|-----------|-------------|------------|---------------------|
| 50 | 1,500 | $375 | $0.63 |
| 100 | 3,000 | $750 | $0.63 |
| 200 | 6,000 | $1,500 | $0.63 |
| 500 | 15,000 | $3,750 | $0.63 |

---

## 🔍 Monitoring & Debugging

### Ver Logs en Railway

```bash
# From Railway CLI
railway logs --service m4markets-voice-agent

# Filter for metrics
railway logs | grep "📊 Call Metrics"

# Filter for tool calls
railway logs | grep "🔧 Tool"

# Filter for costs
railway logs | grep "💰 Cost"
```

### Interpretar las Métricas

```
💰 Cost: $0.2145 ($0.0410/min) | Tools: 8
```

- **$0.2145**: Costo total de la llamada
- **$0.0410/min**: Costo promedio por minuto
- **Tools: 8**: El agente usó 8 herramientas durante la llamada

### Event Timeline

Los logs muestran cada evento en tiempo real:

```
[timestamp] 🎤 User speaking: 3.2s
[timestamp] 🔧 Tool called: get_lead_history
[timestamp] ✅ Tool COMPLETED: get_lead_history (0.45s)
[timestamp] 🗣️ Agent speaking: 245 chars
[timestamp] 🎤 User speaking: 5.1s
...
```

---

## 🚀 Deployment Checklist

### Before Deploying

1. ✅ Set `AGENT_VOICE` and `VOICE_SPEED` in Railway
2. ✅ Verify all required env vars are set
3. ✅ Test locally with `python voice_agent_m4markets.py dev`
4. ✅ Check Railway logs for any errors

### After Deploying

1. ✅ Monitor first few calls carefully
2. ✅ Check latency metrics (`First Response` time)
3. ✅ Verify tool calls are working
4. ✅ Review cost per call
5. ✅ Adjust voice settings if needed

### Railway Environment Variables

```bash
# Set voice configuration
railway variables set AGENT_VOICE=nova
railway variables set VOICE_SPEED=1.15

# Verify
railway variables
```

---

## 📈 Performance Targets

### Latency Goals

- ⭐ **Excellent**: < 2s first response
- ✅ **Good**: 2-3s first response
- ⚠️ **Acceptable**: 3-4s first response
- ❌ **Poor**: > 4s first response

### Cost Goals

- ⭐ **Excellent**: < $0.20 per qualified lead
- ✅ **Good**: $0.20-0.40 per qualified lead
- ⚠️ **Acceptable**: $0.40-0.60 per qualified lead
- ❌ **High**: > $0.60 per qualified lead

### Tool Efficiency

- **Fast Tools** (< 500ms): `query_m4markets_knowledge`, `get_account_comparison`
- **Medium Tools** (500ms-1s): `save_conversation_note`, `recommend_account_type`
- **Slow Tools** (1-2s): `qualify_and_save_lead`, `schedule_callback` (database writes)

---

## 🛠️ Troubleshooting

### High Latency

1. Check `First Response` metric in logs
2. If consistently > 3s:
   - Increase `VOICE_SPEED` to 1.25
   - Switch to `AGENT_VOICE=echo`
   - Check network latency to LiveKit

### High Costs

1. Check `Cost/Minute` metric
2. If consistently > $0.05/min:
   - Reduce system instruction length
   - Cache common responses
   - Optimize tool SQL queries
   - Use faster voice to reduce call duration

### Tools Not Working

1. Check for errors in logs:
   ```
   ❌ Tool FAILED: qualify_and_save_lead (1.12s) - Database connection error
   ```
2. Verify database connection
3. Check tool parameter validation

---

## 📋 Next Steps

- [ ] Set up alerting for high-cost calls (> $1.00)
- [ ] Implement caching for FAQ responses
- [ ] Create dashboard for real-time metrics
- [ ] A/B test different voice configurations
- [ ] Optimize system instructions for token efficiency

---

**Last Updated**: 2025-11-20
**Version**: 1.1.0 (Optimized)
