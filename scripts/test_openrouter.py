#!/usr/bin/env python3
"""Test OpenRouter API connection."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from auto_trader.decision.llm import get_llm

def main():
    """Test OpenRouter connection."""
    print("=" * 60)
    print("Testing OpenRouter API Connection")
    print("=" * 60)
    print()
    
    try:
        # Get LLM instance
        llm = get_llm()
        print(f"✓ LLM initialized: {llm}")
        print()
        
        # Test simple query
        print("Testing simple query...")
        response = llm.invoke("Say 'Hello, I am working!' in exactly 5 words.")
        print(f"✓ Response: {response.content}")
        print()
        
        print("=" * 60)
        print("✓ OpenRouter connection working!")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check OPENAI_API_KEY in .env")
        print("2. Check LLM_BASE_URL is https://openrouter.ai/api/v1")
        print("3. Check LLM_PROVIDER is 'openai'")
        print("4. Verify API key is valid at https://openrouter.ai")
        sys.exit(1)

if __name__ == "__main__":
    main()
