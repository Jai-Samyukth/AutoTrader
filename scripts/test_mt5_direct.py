#!/usr/bin/env python3
"""Test direct MT5 connection using Python package."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from auto_trader.data.mt5_client import (
    mt5_get_account_info,
    mt5_get_positions,
    mt5_get_symbol_info,
)


def main():
    """Test MT5 connection."""
    print("=" * 60)
    print("Testing Direct MT5 Connection")
    print("=" * 60)
    print()
    
    try:
        # Test account info
        print("1. Testing account info...")
        account = mt5_get_account_info.invoke({})
        print(f"✓ Account Balance: ${account['balance']:.2f}")
        print(f"✓ Account Equity: ${account['equity']:.2f}")
        print(f"✓ Leverage: 1:{account['leverage']}")
        print()
        
        # Test positions
        print("2. Testing positions...")
        positions = mt5_get_positions.invoke({"symbol": ""})
        pos_count = len(positions.get("positions", []))
        print(f"✓ Open Positions: {pos_count}")
        print()
        
        # Test symbol info
        print("3. Testing symbol info (EURUSD.m)...")
        symbol_info = mt5_get_symbol_info.invoke({"symbol": "EURUSD.m"})
        print(f"✓ Symbol: {symbol_info['symbol']}")
        print(f"✓ Bid: {symbol_info['bid']:.5f}")
        print(f"✓ Ask: {symbol_info['ask']:.5f}")
        print(f"✓ Spread: {symbol_info['spread']} points")
        print()
        
        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Make sure MetaTrader 5 is installed and running")
        print("2. Make sure you're logged into your MT5 account")
        print("3. Check your .env file has correct MT5 credentials:")
        print("   MT5_LOGIN=your_login_id")
        print("   MT5_PASSWORD=your_password")
        print("   MT5_SERVER=your_broker_server")
        sys.exit(1)


if __name__ == "__main__":
    main()
