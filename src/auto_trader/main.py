from auto_trader.core.meta_trader.life_cycle import (
    initialize_mt5,
    login_mt5,
    shutdown_mt5,
)


def main():
    import MetaTrader5 as mt5

    # display data on the MetaTrader 5 package
    print("MetaTrader5 package author: ", mt5.__author__)
    print("MetaTrader5 package version: ", mt5.__version__)

    # establish connection to the MetaTrader 5 terminal
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        quit()

    # attempt to enable the display of the GBPUSD in MarketWatch
    selected = mt5.symbol_select("GBPUSD.m", True)
    if not selected:
        print("Failed to select GBPUSD")
        mt5.shutdown()
        quit()

    # display the last GBPUSD tick
    lasttick = mt5.symbol_info_tick("GBPUSD")
    print(lasttick)
    # display tick field values in the form of a list
    print('Show symbol_info_tick("GBPUSD")._asdict():')
    symbol_info_tick_dict = mt5.symbol_info_tick("GBPUSD")._asdict()
    for prop in symbol_info_tick_dict:
        print("  {}={}".format(prop, symbol_info_tick_dict[prop]))

    # shut down connection to the MetaTrader 5 terminal
    mt5.shutdown()
