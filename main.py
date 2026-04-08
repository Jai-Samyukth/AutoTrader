import MetaTrader5 as mt5
import time

if not mt5.initialize():
    print("Init failed")
    quit()

symbol = "EURUSD.m"
mt5.symbol_select(symbol, True)
print(mt5.terminal_info())
# Track the last millisecond timestamp to detect changes
last_time_msc = 0

print(f"Streaming {symbol} price changes...")

try:
    i = 0
    while i<1:
        tick = mt5.symbol_info_tick(symbol)
        
        if tick and tick.time_msc != last_time_msc:
            print(f"Time: {tick.time} | Bid: {tick.bid} | Ask: {tick.ask}")
            last_time_msc = tick.time_msc
            
        time.sleep(0.05) 
        i += 1
except KeyboardInterrupt:
    pass
finally:
    mt5.shutdown()