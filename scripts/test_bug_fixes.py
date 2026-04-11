#!/usr/bin/env python3
"""Test script to verify bug fixes."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from auto_trader.data.market_data import mt5_to_tradingview
from auto_trader.decision.workflow import parse_llm_response


def test_symbol_conversion():
    """Test MT5 to TradingView symbol conversion."""
    print("=" * 60)
    print("TEST 1: Symbol Conversion")
    print("=" * 60)
    
    test_cases = [
        ("EURUSD.m", "FX:EURUSD"),
        ("GBPUSD.m", "FX:GBPUSD"),
        ("EURUSD.M", "FX:EURUSD"),
        ("XAUUSD.m", "FX:XAUUSD"),
    ]
    
    for mt5_symbol, expected in test_cases:
        result = mt5_to_tradingview(mt5_symbol)
        status = "✅" if result == expected else "❌"
        print(f"{status} {mt5_symbol} -> {result} (expected: {expected})")
    
    print()


def test_json_parsing():
    """Test LLM response JSON parsing."""
    print("=" * 60)
    print("TEST 2: JSON Parsing")
    print("=" * 60)
    
    # Test case 1: Clean JSON
    clean_json = '{"decision": "SKIP", "pair": "EURUSD.m"}'
    try:
        result = parse_llm_response(clean_json)
        print(f"✅ Clean JSON: {result}")
    except Exception as e:
        print(f"❌ Clean JSON failed: {e}")
    
    # Test case 2: Markdown wrapped JSON
    markdown_json = '''```json
{
    "decision": "SKIP",
    "pair": "EURUSD.m"
}
```'''
    try:
        result = parse_llm_response(markdown_json)
        print(f"✅ Markdown JSON: {result}")
    except Exception as e:
        print(f"❌ Markdown JSON failed: {e}")
    
    # Test case 3: JSON with extra text
    mixed_text = '''Here is the analysis:
{
    "decision": "SKIP",
    "pair": "EURUSD.m"
}
Hope this helps!'''
    try:
        result = parse_llm_response(mixed_text)
        print(f"✅ Mixed text JSON: {result}")
    except Exception as e:
        print(f"❌ Mixed text JSON failed: {e}")
    
    # Test case 4: Invalid JSON (should fail)
    invalid_json = "This is not JSON at all"
    try:
        result = parse_llm_response(invalid_json)
        print(f"❌ Invalid JSON should have failed but got: {result}")
    except ValueError as e:
        print(f"✅ Invalid JSON correctly rejected: {str(e)[:50]}...")
    
    print()


def test_model_config():
    """Test that model is configured correctly."""
    print("=" * 60)
    print("TEST 3: Model Configuration")
    print("=" * 60)
    
    from auto_trader.config import config
    
    print(f"LLM Provider: {config.llm_provider}")
    print(f"LLM Model: {config.llm_model}")
    print(f"LLM Base URL: {config.llm_base_url}")
    
    if config.llm_model == "google/gemini-2.0-flash-001":
        print("✅ Model updated to Gemini 2.0 Flash")
    else:
        print(f"⚠️  Model is still: {config.llm_model}")
    
    print()


if __name__ == "__main__":
    print("\n🧪 Testing Bug Fixes\n")
    
    test_symbol_conversion()
    test_json_parsing()
    test_model_config()
    
    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
