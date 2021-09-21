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
                 main_tf='1m'
                 ):
        self.__name = name
        self.__symbol = symbol
        self.__exchange = Exchange()
        self.__notifier = Notifier()
        self.__budget_percent = self.__valid_budget_percent(budget_percent)
        self.__leverage = self.__valid_leverage(leverage)
        self.__main_tf = main_tf
        self.__prices = {}
        self.__in_position = False

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

    @abstractmethod
    def execute(self) -> None:
        """Execute the strategy's logic.

        Different strategies can be done by overriding this method"""
        pass

    def run(self) -> None:
        """Entry point"""
        self.fetch_prices()
        self.execute()

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

    def market_sell(self, size, params=None) -> Order:
        order = self.__exchange.create_order(pair=self.symbol(), type='market', side='sell', size=size, params=params)
        self.__notifier.log(order.__str__())
        return order

    def market_buy(self, size, params=None) -> Order:
        order = self.__exchange.create_order(pair=self.symbol(), type='market', side='buy', size=size, params=params)
        self.__notifier.log(order.__str__())
        return order

    def price_difference(self, entry_price, mark_price) -> float:
        difference = (mark_price / entry_price - 1) * 100
        return np.round(difference, 3)

    def pnl_percent(self, entry_price, mark_price) -> float:
        return np.round(self.price_difference(entry_price, mark_price) * self.__leverage, 3)

    def __select_timeframe(self, timeframe) -> str:
        if not timeframe:
            return self.__main_tf
        return timeframe
