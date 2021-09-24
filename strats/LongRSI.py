import talib
from pandas import Series

from strats.Strategy import Strategy


class LongRSI(Strategy):

    def __init__(self,
                 name: str,
                 symbol: str,
                 budget_percent: int,
                 leverage: int,
                 ):
        super().__init__(
            name=name,
            budget_percent=budget_percent,
            leverage=leverage,
            symbol=symbol,
            timeframes=['1m', '15m'],
            stop_loss=7
        )

    def is_opportunity_to_enter(self) -> bool:
        rsi_1m = self.__get_rsi('1m')
        rsi_15m = self.__get_rsi('15m')
        valid_rsi_1m = rsi_1m.iloc[-1] <= 30
        valid_rsi_15m = (rsi_15m.iloc[-3:] <= 30).all()
        return valid_rsi_1m and valid_rsi_15m

    def is_opportunity_to_exit(self) -> bool:
        rsi_1m = self.__get_rsi('1m')
        rsi_15m = self.__get_rsi('15m')
        valid_rsi_1m = rsi_1m.iloc[-1] >= 70
        valid_rsi_15m = rsi_15m.iloc[-1] >= 70
        return valid_rsi_1m and valid_rsi_15m

    def enter(self) -> None:
        self.market_in('buy')

    def exit(self) -> None:
        self.market_out('sell')

    def __get_rsi(self, tf) -> Series:
        return talib.RSI(self.prices(column='close', timeframe=tf), timeperiod=14)
