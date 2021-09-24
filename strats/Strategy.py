from abc import abstractmethod

import numpy as np
from pandas import Series

from external.Exchange import Exchange
from external.Notifier import Notifier
from external.Order import Order


class Strategy:
    def __init__(self,
                 name: str,
                 budget_percent: int,
                 leverage: int,
                 symbol: str,
                 timeframes,
                 stop_loss: int = 5
                 ):
        self.__name = name
        self.__symbol = symbol
        self.__exchange = Exchange()
        self.__notifier = Notifier()
        self.__budget_percent = self.__valid_budget_percent(budget_percent)
        self.__leverage = self.__valid_leverage(leverage)
        self.__timeframes = self.__valid_timeframes(timeframes)
        self.__prices = {}
        self.__in_position = False
        self.__order = None
        self.__entry_price = None
        self.__exit_price = None
        self.__stop_loss = stop_loss

    @staticmethod
    def __valid_budget_percent(value) -> int:
        if value <= 0 or value > 100:
            raise Exception("Budget level must be (0, 100]")
        return int(value)

    @staticmethod
    def __valid_leverage(value) -> int:
        if value < 1 or value > 100:
            raise Exception("Leverage must be [1, 100]")
        return int(value)

    @staticmethod
    def __valid_timeframes(value):
        if len(value) == 0:
            raise Exception("Timeframe required")
        return value

    def exchange(self) -> Exchange:
        return self.__exchange

    def notifier(self) -> Notifier:
        return self.__notifier

    def leverage(self) -> int:
        return self.__leverage

    def in_position(self) -> bool:
        return self.__in_position

    def open_position(self) -> None:
        self.__in_position = True

    def close_position(self) -> None:
        self.__in_position = False

    def symbol(self):
        return self.__symbol

    def name(self):
        return self.__name

    def order(self) -> Order:
        return self.__order

    def run(self) -> None:
        """Entry point"""
        for tf in self.__timeframes:
            self.fetch_prices(timeframe=tf)
        self.execute()

    def execute(self) -> None:
        last_price = self.last_price('close')
        self.notify(f'Mark price: {last_price} / In position: {self.in_position()}')
        if self.in_position():
            if self.is_opportunity_to_exit():
                self.exit()
                gains = self.pnl_percent(self.__entry_price, self.__exit_price)
                self.notify(f'Sell @ {self.__exit_price} # PNL {gains} %')
            else:
                gains = self.pnl_percent(self.__entry_price, last_price)
                if gains <= -self.__stop_loss:
                    self.exit()
                    self.notify(f'SL @ {self.__exit_price} # PNL {gains} %')
                self.__show_stats(last_price, gains)
        elif self.is_opportunity_to_enter():
            self.enter()
            self.notify(f'Buy @ {self.__entry_price}')

    @abstractmethod
    def is_opportunity_to_enter(self) -> bool:
        pass

    @abstractmethod
    def is_opportunity_to_exit(self) -> bool:
        pass

    @abstractmethod
    def enter(self) -> None:
        pass

    @abstractmethod
    def exit(self) -> None:
        pass

    def fetch_prices(self, timeframe=None) -> None:
        """Fetches and stores the bars data for the specified timeframe.

        By default uses the main timeframe specified on strategy creation,
        but it can be given a different one to store extra data.
        """
        tf = self.__select_timeframe(timeframe)
        self.__prices[tf] = self.__exchange.bars(pair=self.symbol(), timeframe=tf)

    def prices(self, column, timeframe=None) -> Series:
        tf = self.__select_timeframe(timeframe)
        return self.__prices[tf][column]

    def last_price(self, column, timeframe=None) -> float:
        return self.prices(column, timeframe).iat[-1]

    def position_size(self) -> float:
        """Computes the size in play

        Take into account:
        - Available balance
        - Percentage of balance to use
        - Leverage
        """
        free_usdt = self.__exchange.free_balance()
        last_close = self.last_price('close')
        balance_to_use = np.round(free_usdt * self.__budget_percent / 100, 4)
        asset_amount = np.round((balance_to_use / last_close) * self.__leverage, 3)
        self.__notifier.log(f"free usdt: {free_usdt} / Cost: {balance_to_use} / Position size: {asset_amount}")
        return asset_amount

    def market_in(self, side, params=None):
        size = self.position_size()
        self.__order = self.__exchange.create_order(pair=self.symbol(), type='market', side=side, size=size,
                                                    params=params)
        self.__notifier.log(self.__order.__str__())
        self.open_position()
        self.__entry_price = self.__order.avg_price()

    def market_out(self, side, params=None):
        size = self.order().asset_amount()
        self.__order = self.__exchange.create_order(pair=self.symbol(), type='market', side=side, size=size,
                                                    params=params)
        self.__notifier.log(self.__order.__str__())
        self.close_position()
        self.__exit_price = self.__order.avg_price()

    def price_difference(self, entry_price, mark_price) -> float:
        difference = (mark_price / entry_price - 1) * 100
        return np.round(difference, 3)

    def pnl_percent(self, entry_price, mark_price) -> float:
        return np.round(self.price_difference(entry_price, mark_price) * self.__leverage, 3)

    def notify(self, msg):
        self.__notifier.send(f'\n{self.symbol()} -- [{self.name()}] {msg}')

    def __select_timeframe(self, timeframe) -> str:
        if not timeframe:
            return self.__timeframes[0]
        return timeframe

    def __show_stats(self, last_price, gains):
        self.__notifier.log(f"Bought at: {self.__entry_price} / Current: {last_price}")
        percent = self.price_difference(self.__entry_price, last_price)
        self.__notifier.log(f'SL at {self.__stop_loss}%. Current PNL:  {gains}% / Price diff: {percent}')
