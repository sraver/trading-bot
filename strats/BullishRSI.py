import numpy as np
import talib

from strats.Strategy import Strategy


class BullishRSI(Strategy):

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
            main_tf='1m'
        )
        self.__entry_price = None
        self.__exit_price = None
        self.__stop_loss = 7

    def execute(self):
        self.notifier().log(f'\n{self.symbol()}')

        size = self.position_size()

        last_price = self.last_price('close')
        rsi = talib.RSI(self.prices(column='close'), timeperiod=14)
        current_rsi = np.round((rsi.iat[-1]), 3)

        self.notifier().log(f"Mark price: {last_price} / RSI: {current_rsi} / Position: {self.in_position()}")

        if current_rsi <= 30 and not self.in_position():
            self.buy(size)
            self.notifier().send(f'[{self.name()}] Buy @ {self.__entry_price}')

        if current_rsi >= 70 and self.in_position():
            self.sell(size)
            gains = self.pnl_percent(self.__entry_price, self.__exit_price)
            self.notifier().send(f'[{self.name()}] Sell @ {self.__exit_price} # PNL {gains}%')

        if self.in_position():
            gains = self.pnl_percent(self.__entry_price, last_price)
            self.__show_stats(last_price, gains)

            if gains <= -self.__stop_loss:
                self.sell(size)
                self.notifier().send(f'[{self.name()}] SL @ {self.__exit_price} # PNL {gains}')

    def __show_stats(self, last_price, gains):
        self.notifier().log(f"Bought at: {self.__entry_price} / Current: {last_price}")
        percent = self.price_difference(self.__entry_price, last_price)
        self.notifier().log(f'SL at {self.__stop_loss}%. Current PNL:  {gains}% / Price diff: {percent}')

    def buy(self, size):
        order = self.market_buy(size)
        self.open_position()
        self.__entry_price = order.avg_price()

    def sell(self, size):
        order = self.market_sell(size)
        self.close_position()
        self.__exit_price = order.avg_price()
