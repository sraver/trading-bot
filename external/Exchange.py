import config
import ccxt
import pandas as pd
from pandas import DataFrame

from external.Order import Order


class Exchange:

    def __init__(self):
        self.__exchange = ccxt.binanceusdm({
            "apiKey": config.BINANCE_API_KEY,
            "secret": config.BINANCE_SECRET_KEY
        })

    def free_balance(self) -> float:
        balance = self.__exchange.fetch_balance()
        return float(balance['free']['USDT'])

    def bars(self, pair, timeframe, limit=100) -> DataFrame:
        bars = self.__exchange.fetch_ohlcv(symbol=pair, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    def create_order(self, pair, type, side, size, params) -> Order:
        if not params:
            params = {}
        data = self.__exchange.create_order(symbol=pair, type=type, side=side, amount=size, params=params)
        return Order(data)
