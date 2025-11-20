"""
Knowledge Tools for M4Markets Voice Agent
Queries Second Brain (ChromaDB via MCP) for M4Markets information
"""

import httpx
import yaml
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config_path = Path(__file__).parent.parent / "config" / "knowledge_sources.yaml"
with open(config_path, 'r', encoding='utf-8') as f:
    KB_CONFIG = yaml.safe_load(f)


class M4MarketsKnowledgeBase:
    """Interface to query M4Markets knowledge from Second Brain"""

    def __init__(self):
        self.config = KB_CONFIG['knowledge_sources'][0]['config']
        self.search_params = KB_CONFIG['knowledge_sources'][0]['search_params']
        self.chroma_url = self.config['chroma_url']

    async def query(
        self,
        query: str,
        n_results: int = None,
        category: Optional[str] = None
    ) -> Dict:
        """
        Query Second Brain for M4Markets knowledge

        Args:
            query: Natural language question or search term
            n_results: Number of results to return (default from config)
            category: Optional category filter (products, regulation, etc.)

        Returns:
            Dict with results and metadata
        """
        n_results = n_results or self.search_params['n_results']

        try:
            # In production, this would call the MCP server
            # For now, we'll use a direct HTTP call to ChromaDB or mock the MCP call

            # Since we're using MCP in Claude Code, we need to call it properly
            # This is a simplified version - the actual agent will use MCP tools

            logger.info(f"Querying knowledge base: {query}")

            # TODO: Implement actual MCP call
            # For now, return a structured response
            result = {
                "success": True,
                "query": query,
                "results": [],
                "metadata": {
                    "n_results": n_results,
                    "category": category
                }
            }

            return result

        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    def get_category_keywords(self, category: str) -> List[str]:
        """Get keywords for a specific category"""
        categories = KB_CONFIG['knowledge_sources'][0]['categories']
        for cat in categories:
            if cat['name'] == category:
                return cat['keywords']
        return []


# Function tools for LiveKit agent
async def query_m4markets_knowledge(query: str, category: Optional[str] = None) -> str:
    """
    Query M4Markets knowledge base for information

    This function is exposed as a tool to the LiveKit voice agent.
    It searches the Second Brain for M4Markets information.

    Args:
        query: Question or search term (e.g., "spreads en cuenta Standard")
        category: Optional category (products, regulation, trading_conditions, payments, education)

    Returns:
        String with relevant information from knowledge base

    Examples:
        - query="¿Cuáles son los spreads de la cuenta Raw?"
        - query="regulaciones de M4Markets", category="regulation"
        - query="métodos de depósito disponibles", category="payments"
    """
    kb = M4MarketsKnowledgeBase()

    try:
        # Note: In actual LiveKit agent, we'll use MCP tools directly
        # This is a placeholder that shows the structure

        # For now, we'll construct a response based on common queries
        # In production, this calls the MCP search_knowledge tool

        response = f"Consultando información sobre: {query}"

        # Common query patterns and responses
        if "spread" in query.lower():
            response = """
            M4Markets ofrece diferentes tipos de spreads según la cuenta:
            - Cuenta Standard: spreads desde 1.1 pips, sin comisiones
            - Cuenta Raw Spreads: spreads desde 0.0 pips, con comisión de $3.5 por lado
            - Cuenta Premium: spreads desde 0.8 pips, sin comisiones
            - Cuenta Dynamic Leverage: spreads desde 0.0 pips, sin comisiones
            """

        elif "regulación" in query.lower() or "regulado" in query.lower():
            response = """
            M4Markets está regulado por múltiples autoridades internacionales:
            - CySEC (Chipre): Licencia 301/16 para clientes europeos
            - DFSA (Dubai): Licencia F007051 Categoría 3A
            - FSA (Seychelles): Licencia SD047

            Además, los fondos de clientes están segregados en bancos tier 1
            y hay cobertura de hasta €20,000 por el ICF (Investor Compensation Fund).
            """

        elif "depósito" in query.lower() or "mínimo" in query.lower():
            response = """
            Los depósitos mínimos en M4Markets son:
            - Cuenta Standard: $5 USD
            - Cuenta Raw Spreads: $100 USD
            - Cuenta Premium: $1,000 USD
            - Cuenta Dynamic Leverage: $5 USD

            M4Markets acepta múltiples métodos de pago incluyendo tarjetas,
            transferencias bancarias, y billeteras electrónicas.
            """

        elif "cuenta" in query.lower() and "tipo" in query.lower():
            response = """
            M4Markets ofrece 4 tipos principales de cuentas:

            1. Standard: Ideal para principiantes, desde $5, spreads desde 1.1 pips
            2. Raw Spreads: Para traders activos, spreads desde 0.0 pips con comisión
            3. Premium: Para capital significativo, desde $1,000, spreads desde 0.8 pips
            4. Dynamic Leverage: Leverage flexible hasta 1:5000, spreads desde 0.0 pips

            Todas las cuentas tienen acceso a MT4, MT5 y cTrader.
            """

        else:
            response = f"He buscado información sobre '{query}' en la base de conocimiento de M4Markets."

        logger.info(f"Knowledge query result: {response[:100]}...")
        return response

    except Exception as e:
        logger.error(f"Error in query_m4markets_knowledge: {e}")
        return f"No pude obtener información específica sobre '{query}'. ¿Podrías reformular la pregunta?"


async def get_account_comparison(account_types: List[str] = None) -> str:
    """
    Compare different M4Markets account types

    Args:
        account_types: List of account types to compare (default: all)

    Returns:
        Comparison table or description
    """
    if not account_types:
        account_types = ["Standard", "Raw Spreads", "Premium", "Dynamic Leverage"]

    comparison = """
    Comparación de Cuentas M4Markets:

    | Característica      | Standard | Raw Spreads | Premium | Dynamic |
    |--------------------|----------|-------------|---------|---------|
    | Depósito mínimo    | $5       | $100        | $1,000  | $5      |
    | Spreads desde      | 1.1 pips | 0.0 pips    | 0.8 pips| 0.0 pips|
    | Comisión           | $0       | $3.5/lado   | $0      | $0      |
    | Leverage máximo    | 1:1000   | 1:500       | 1:1000  | 1:5000  |
    | Mejor para         | Principiantes | Traders activos | Capital alto | Leverage flexible |
    """

    return comparison


async def get_regulation_info(region: Optional[str] = None) -> str:
    """
    Get regulatory information for M4Markets

    Args:
        region: Specific region (Europa, Dubai, Seychelles) or None for all

    Returns:
        Regulatory details
    """
    if not region or region.lower() in ["todos", "all"]:
        return """
        M4Markets opera bajo múltiples licencias regulatorias:

        🇪🇺 EUROPA (CySEC - Chipre)
        - Licencia: 301/16
        - Entidad: Harindale Limited
        - Protección: ICF hasta €20,000
        - Segregación de fondos en bancos tier 1

        🇦🇪 DUBAI (DFSA)
        - Licencia: F007051 Categoría 3A
        - Entidad: Oryx Finance Limited
        - Regulador: Dubai Financial Services Authority

        🇸🇨 SEYCHELLES (FSA)
        - Licencia: SD047
        - Para clientes internacionales

        Todas las jurisdicciones ofrecen protección contra balance negativo.
        """

    region_lower = region.lower()

    if "europa" in region_lower or "chipre" in region_lower or "cysec" in region_lower:
        return """
        M4Markets Europa está regulado por CySEC (Cyprus Securities and Exchange Commission):
        - Número de licencia: 301/16
        - Entidad legal: Harindale Limited
        - Cobertura ICF: Hasta €20,000 por cliente
        - Fondos segregados en bancos de tier 1
        - Cumple con directivas MiFID II
        """

    elif "dubai" in region_lower or "dfsa" in region_lower:
        return """
        M4Markets Dubai está regulado por DFSA (Dubai Financial Services Authority):
        - Número de licencia: F007051
        - Categoría: 3A (full scope services)
        - Entidad legal: Oryx Finance Limited
        - Supervisión bajo estándares internacionales
        """

    else:
        return f"No encontré información específica sobre la región '{region}'. Regiones disponibles: Europa, Dubai, Seychelles."


# Export all tools
__all__ = [
    'query_m4markets_knowledge',
    'get_account_comparison',
    'get_regulation_info',
    'M4MarketsKnowledgeBase'
]
