"""
Forex-specific tools for M4Markets Voice Agent
Provides trading-related utilities and information
"""

from typing import Dict, Optional, List
import logging
from livekit.agents import function_tool

logger = logging.getLogger(__name__)


@function_tool
async def recommend_account_type(
    capital: int,
    experience: str,
    trading_style: Optional[str] = None,
    priority: Optional[str] = None  # "low_cost", "low_spread", "high_leverage"
) -> Dict:
    """
    Recommend M4Markets account type based on trader profile

    Args:
        capital: Available capital in USD
        experience: Trading experience (principiante, intermedio, avanzado)
        trading_style: Optional trading style (scalping, day_trading, swing, position)
        priority: What matters most (low_cost, low_spread, high_leverage)

    Returns:
        Recommended account with reasoning
    """
    exp_lower = experience.lower()

    recommendations = []

    # Standard Account - Good for beginners
    if capital < 100 or "principiante" in exp_lower:
        recommendations.append({
            "account": "Standard",
            "score": 90 if "principiante" in exp_lower else 70,
            "reason": "Ideal para comenzar con bajo capital, sin comisiones y spreads competitivos desde 1.1 pips. Depósito mínimo de solo $5."
        })

    # Raw Spreads - Best for active traders
    if capital >= 100 and (
        trading_style in ["scalping", "day_trading"] or
        priority == "low_spread" or
        "intermedio" in exp_lower or "avanzado" in exp_lower
    ):
        recommendations.append({
            "account": "Raw Spreads",
            "score": 95 if trading_style == "scalping" else 85,
            "reason": "Spreads desde 0.0 pips ideales para scalping y day trading. Comisión de $3.5 por lado, pero costos totales más bajos en operaciones frecuentes."
        })

    # Premium Account - For higher capital
    if capital >= 1000:
        recommendations.append({
            "account": "Premium",
            "score": 90 if capital >= 5000 else 75,
            "reason": "Combina spreads bajos (desde 0.8 pips) sin comisiones. Ideal para capital significativo con beneficios adicionales."
        })

    # Dynamic Leverage - For flexibility
    if priority == "high_leverage" or "avanzado" in exp_lower:
        recommendations.append({
            "account": "Dynamic Leverage",
            "score": 85,
            "reason": "Leverage flexible hasta 1:5000 en pares mayores. Ajuste automático según volumen. Para traders experimentados que necesitan leverage alto."
        })

    # Sort by score and get top recommendation
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    top_recommendation = recommendations[0] if recommendations else None

    if not top_recommendation:
        # Fallback to Standard
        top_recommendation = {
            "account": "Standard",
            "score": 60,
            "reason": "Cuenta versátil que se adapta a la mayoría de traders."
        }

    return {
        "recommended_account": top_recommendation['account'],
        "reason": top_recommendation['reason'],
        "alternatives": recommendations[1:3] if len(recommendations) > 1 else [],
        "capital_analysis": _analyze_capital(capital),
        "experience_match": _match_experience(experience, top_recommendation['account'])
    }


def _analyze_capital(capital: int) -> str:
    """Analyze capital adequacy"""
    if capital < 100:
        return "Capital inicial bajo - recomendamos cuenta Standard o practicar con demo."
    elif capital < 1000:
        return "Capital moderado - puedes acceder a cuentas Standard o Raw Spreads."
    elif capital < 5000:
        return "Buen capital - tienes acceso a todas las cuentas incluyendo Premium."
    else:
        return "Capital excelente - califica para Premium con beneficios VIP."


def _match_experience(experience: str, account: str) -> str:
    """Match experience level with account type"""
    exp_lower = experience.lower()

    matches = {
        "Standard": ["principiante", "intermedio"],
        "Raw Spreads": ["intermedio", "avanzado"],
        "Premium": ["intermedio", "avanzado"],
        "Dynamic Leverage": ["avanzado"]
    }

    for level in matches.get(account, []):
        if level in exp_lower:
            return f"✓ Tu nivel de experiencia ({experience}) es perfecto para esta cuenta."

    return f"Esta cuenta puede requerir más/menos experiencia que tu nivel actual ({experience})."


@function_tool
async def calculate_trading_costs(
    account_type: str,
    instrument: str = "EURUSD",
    lot_size: float = 1.0,
    trades_per_month: int = 20
) -> Dict:
    """
    Calculate estimated trading costs for M4Markets accounts

    Args:
        account_type: Type of account (Standard, Raw Spreads, Premium, Dynamic)
        instrument: Trading instrument (default EURUSD)
        lot_size: Size of each trade in lots
        trades_per_month: Number of trades per month

    Returns:
        Cost breakdown and comparison
    """
    # Spread costs (in pips, converted to USD for 1 lot)
    spreads = {
        "Standard": {"EURUSD": 1.1, "GBPUSD": 1.5, "USDJPY": 1.2},
        "Raw Spreads": {"EURUSD": 0.0, "GBPUSD": 0.1, "USDJPY": 0.0},
        "Premium": {"EURUSD": 0.8, "GBPUSD": 1.2, "USDJPY": 0.9},
        "Dynamic Leverage": {"EURUSD": 0.0, "GBPUSD": 0.1, "USDJPY": 0.0}
    }

    # Commission per side
    commissions = {
        "Standard": 0,
        "Raw Spreads": 3.5,
        "Premium": 0,
        "Dynamic Leverage": 0
    }

    spread = spreads.get(account_type, {}).get(instrument, 1.0)
    commission = commissions.get(account_type, 0)

    # Calculate costs (simplified)
    # 1 pip in EURUSD = $10 per lot
    pip_value = 10 if "JPY" not in instrument else 9.12

    spread_cost_per_trade = spread * pip_value * lot_size
    commission_cost_per_trade = commission * 2 * lot_size  # Both sides

    total_cost_per_trade = spread_cost_per_trade + commission_cost_per_trade
    monthly_cost = total_cost_per_trade * trades_per_month

    return {
        "account_type": account_type,
        "instrument": instrument,
        "spread_pips": spread,
        "commission_per_side": commission,
        "costs": {
            "spread_per_trade": round(spread_cost_per_trade, 2),
            "commission_per_trade": round(commission_cost_per_trade, 2),
            "total_per_trade": round(total_cost_per_trade, 2),
            "monthly_estimate": round(monthly_cost, 2)
        },
        "analysis": f"Con {trades_per_month} operaciones/mes de {lot_size} lote(s), tus costos serían aproximadamente ${round(monthly_cost, 2)}/mes.",
        "recommendation": _cost_recommendation(account_type, trades_per_month)
    }


def _cost_recommendation(account_type: str, trades_per_month: int) -> str:
    """Provide cost optimization recommendation"""
    if trades_per_month > 50 and account_type != "Raw Spreads":
        return "⚠️ Con tantas operaciones mensuales, Raw Spreads podría reducir tus costos significativamente."
    elif trades_per_month < 10 and account_type == "Raw Spreads":
        return "💡 Con pocas operaciones, Standard o Premium sin comisiones podrían ser más convenientes."
    else:
        return "✓ Tu selección de cuenta es adecuada para tu volumen de trading."


@function_tool
async def explain_forex_concept(concept: str) -> str:
    """
    Explain forex/trading concepts in simple Spanish

    Args:
        concept: Concept to explain (spread, pip, leverage, etc.)

    Returns:
        Simple explanation
    """
    explanations = {
        "spread": """
        El **spread** es la diferencia entre el precio de compra (ask) y venta (bid).
        Es el costo de abrir una operación.

        Ejemplo: Si EUR/USD tiene spread de 1.1 pips y comprás 1 lote,
        pagas $11 como costo de entrada.

        En M4Markets:
        - Cuenta Standard: spreads desde 1.1 pips
        - Cuenta Raw: spreads desde 0.0 pips (pero con comisión)
        """,

        "pip": """
        Un **pip** (point in percentage) es la unidad mínima de cambio de precio.

        Ejemplo: Si EUR/USD pasa de 1.1000 a 1.1001, subió 1 pip.

        Valor de 1 pip:
        - En pares mayores: $10 por lote standard
        - En pares con JPY: ~$9 por lote

        Para calcular ganancia: Pips ganados × valor del pip × lotes
        """,

        "leverage": """
        El **leverage** (apalancamiento) te permite operar con más dinero del que tenés.

        Ejemplo: Con leverage 1:100 y $1,000 en tu cuenta,
        podés controlar posiciones de hasta $100,000.

        M4Markets ofrece:
        - Standard/Premium: hasta 1:1000
        - Dynamic Leverage: hasta 1:5000
        - Raw Spreads: hasta 1:500

        ⚠️ Mayor leverage = mayor riesgo. Usá con precaución.
        """,

        "margin": """
        El **margen** es el dinero que necesitás tener en tu cuenta
        para mantener una posición abierta.

        Ejemplo: Para operar 1 lote de EUR/USD con leverage 1:100,
        necesitás $1,000 de margen.

        M4Markets ofrece:
        - Margin call al 100%
        - Stop out al 20%
        - Protección contra balance negativo
        """,

        "cfd": """
        Un **CFD** (Contract for Difference) es un contrato que te permite
        especular sobre el precio de un activo sin poseerlo.

        En M4Markets operás CFDs sobre:
        - Forex (pares de divisas)
        - Índices (S&P 500, DAX, etc.)
        - Commodities (oro, petróleo)
        - Criptomonedas

        Ventajas: Podés ganar con precios subiendo o bajando (long/short).
        """,

        "swap": """
        El **swap** es el interés que se cobra o paga por mantener
        una posición abierta de un día para otro (overnight).

        Depende de las tasas de interés de las divisas.

        M4Markets ofrece:
        - Cuentas libres de swap (Islamic accounts)
        - Swap triple los miércoles
        - Consulta las tasas en la plataforma
        """,

        "scalping": """
        **Scalping** es una estrategia de trading donde hacés
        muchas operaciones rápidas para ganar pocos pips cada vez.

        Requiere:
        - Spreads muy bajos (ideal: cuenta Raw Spreads)
        - Ejecución rápida (M4Markets: milisegundos)
        - Experiencia y disciplina

        M4Markets permite scalping sin restricciones.
        """
    }

    concept_lower = concept.lower()

    for key, explanation in explanations.items():
        if key in concept_lower:
            return explanation.strip()

    return f"""
    No tengo una explicación detallada de '{concept}' en este momento.

    Conceptos que puedo explicar:
    - Spread
    - Pip
    - Leverage (apalancamiento)
    - Margin (margen)
    - CFD
    - Swap
    - Scalping

    ¿Te gustaría que te explique alguno de estos?
    """


@function_tool
async def get_market_hours_info(market: str = "forex") -> str:
    """
    Get information about market trading hours

    Args:
        market: Market type (forex, indices, crypto)

    Returns:
        Trading hours information
    """
    if market.lower() in ["forex", "divisas"]:
        return """
        **Horarios de Forex** (24/5)

        M4Markets opera Forex las 24 horas, 5 días a la semana:

        🕐 Sesiones principales (hora GMT):
        - Tokio: 00:00 - 09:00
        - Londres: 08:00 - 17:00
        - Nueva York: 13:00 - 22:00

        🔥 Mayor liquidez:
        - Overlap Londres-NY: 13:00-17:00 GMT (más volatilidad)

        ⏸️ Cierre semanal:
        - Viernes 22:00 GMT hasta Domingo 22:00 GMT

        💡 Tip: Los spreads pueden aumentar fuera de sesiones principales.
        """

    elif market.lower() in ["indices", "índices"]:
        return """
        **Horarios de Índices**

        Dependen del índice específico:

        - US30, SPX500, NAS100: Casi 24/5
        - DAX30, UK100: Horario europeo
        - JPN225: Horario asiático

        ⚠️ Los spreads aumentan fuera del horario principal del índice.

        Consulta horarios específicos en la plataforma MT4/MT5.
        """

    else:
        return """
        **Horarios de Trading en M4Markets**

        - **Forex**: 24 horas, 5 días (Domingo 22:00 - Viernes 22:00 GMT)
        - **Índices**: Según el índice (generalmente 23/5)
        - **Commodities**: Horarios variables
        - **Cripto**: 24/7 en algunos brokers

        Para horarios exactos de cada instrumento, consultá la plataforma MT4/MT5.
        """


__all__ = [
    'recommend_account_type',
    'calculate_trading_costs',
    'explain_forex_concept',
    'get_market_hours_info'
]
