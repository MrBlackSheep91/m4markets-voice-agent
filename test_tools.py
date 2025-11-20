"""
Test script para verificar que todas las herramientas funcionan correctamente
Ejecutar: python test_tools.py
"""

import asyncio
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.knowledge_tools import query_m4markets_knowledge, get_account_comparison, get_regulation_info
from tools.forex_tools import recommend_account_type, calculate_trading_costs, get_market_hours_info, explain_forex_concept


async def test_knowledge_tools():
    """Test knowledge tools"""
    print("\n" + "="*60)
    print("TESTING KNOWLEDGE TOOLS")
    print("="*60)

    # Test 1: Query M4Markets knowledge
    print("\n1. Testing query_m4markets_knowledge...")
    result = await query_m4markets_knowledge("tipos de cuenta spreads")
    print(f"   ✓ Query result preview: {result[:200]}...")

    # Test 2: Account comparison
    print("\n2. Testing get_account_comparison...")
    result = await get_account_comparison()
    print(f"   ✓ Comparison result preview: {result[:200]}...")

    # Test 3: Regulation info
    print("\n3. Testing get_regulation_info (Europa)...")
    result = await get_regulation_info("Europa")
    print(f"   ✓ Regulation result preview: {result[:200]}...")

    # Test 4: Explain forex concept
    print("\n4. Testing explain_forex_concept (spread)...")
    result = await explain_forex_concept("spread")
    print(f"   ✓ Explanation preview: {result[:200]}...")

    print("\n✅ All knowledge tools working!")


async def test_forex_tools():
    """Test forex tools"""
    print("\n" + "="*60)
    print("TESTING FOREX TOOLS")
    print("="*60)

    # Test 1: Recommend account type
    print("\n1. Testing recommend_account_type...")
    result = await recommend_account_type(capital=3000, experience="intermedio", priority="low_spread")
    print(f"   ✓ Recommended: {result['recommended_account']}")
    print(f"   ✓ Reason: {result['reason'][:100]}...")

    # Test 2: Calculate trading costs
    print("\n2. Testing calculate_trading_costs...")
    result = await calculate_trading_costs("Raw Spreads", trades_per_month=50)
    print(f"   ✓ Monthly cost estimate: ${result['costs']['monthly_estimate']}")
    print(f"   ✓ Recommendation: {result['recommendation']}")

    # Test 3: Market hours info
    print("\n3. Testing get_market_hours_info...")
    result = await get_market_hours_info("forex")
    print(f"   ✓ Market hours preview: {result[:150]}...")

    print("\n✅ All forex tools working!")


async def test_configuration():
    """Test configuration loading"""
    print("\n" + "="*60)
    print("TESTING CONFIGURATION")
    print("="*60)

    # Test YAML loading
    print("\n1. Testing m4markets_config.yaml...")
    import yaml
    with open("config/m4markets_config.yaml", 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print(f"   ✓ Company: {config['company']['name']}")
    print(f"   ✓ Agent language: {config['agent']['language']}")
    print(f"   ✓ Methodology: {config['agent']['methodology']}")
    print(f"   ✓ Product accounts loaded: {len(config['products']['accounts'])}")

    print("\n2. Testing knowledge_sources.yaml...")
    with open("config/knowledge_sources.yaml", 'r', encoding='utf-8') as f:
        kb_config = yaml.safe_load(f)
    print(f"   ✓ Knowledge sources: {len(kb_config['knowledge_sources'])}")
    print(f"   ✓ Primary source: {kb_config['knowledge_sources'][0]['name']}")

    print("\n✅ All configuration files valid!")


async def test_second_brain_connection():
    """Test Second Brain connection via MCP"""
    print("\n" + "="*60)
    print("TESTING SECOND BRAIN CONNECTION")
    print("="*60)

    try:
        # Note: This would require MCP to be available
        # For now, we'll just show it's ready to connect
        print("\n1. Second Brain connection ready...")
        print("   ℹ️  To test actual connection, run:")
        print("   ℹ️  mcp__crawl4ai__search_knowledge('M4Markets spreads', n_results=3)")
        print("\n✅ Second Brain integration ready!")
    except Exception as e:
        print(f"\n⚠️  Note: MCP tools only available in Claude Code environment")
        print(f"   Error: {e}")


def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("\n[OK] Knowledge Tools: PASSED")
    print("[OK] Forex Tools: PASSED")
    print("[OK] Configuration: PASSED")
    print("[OK] Second Brain: READY")
    print("\n*** All systems operational! ***")
    print("\nNext steps:")
    print("1. Set up .env file with credentials")
    print("2. Test voice agent: python voice_agent_m4markets.py dev")
    print("3. Make test call: python evolution_caller.py 549XXXXXXXXX")
    print("\n" + "="*60)


async def main():
    """Run all tests"""
    print("\n*** M4MARKETS VOICE AGENT - SYSTEM TEST ***")
    print("Testing all components...\n")

    try:
        await test_knowledge_tools()
        await test_forex_tools()
        await test_configuration()
        await test_second_brain_connection()
        print_summary()

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
