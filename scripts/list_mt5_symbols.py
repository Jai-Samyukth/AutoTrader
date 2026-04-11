#!/usr/bin/env python3
"""List available MT5 symbols."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import MetaTrader5 as mt5
from auto_trader.config import config

def main():
    """List available symbols."""
    # Initialize
    if not mt5.initialize():
        print("MT5 initialization failed")
        return
    
    # Login
    if config.mt5_login and config.mt5_password and config.mt5_server:
        if not mt5.login(
            login=int(config.mt5_login),
            password=config.mt5_password,
            server=config.mt5_server
        ):
            print(f"Login failed: {mt5.last_error()}")
            return
    
    print("Available symbols:")
    print("=" * 60)
    
    symbols = mt5.symbols_get()
    if symbols:
        for s in symbols[:50]:  # First 50
            print(f"{s.name:15} - {s.description}")
    else:
        print("No symbols found")
    
    mt5.shutdown()

if __name__ == "__main__":
    main()
