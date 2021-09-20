import numpy as np
from abc import abstractmethod
import talib

from external.Exchange import Exchange
from external.Notifier import Notifier
from strats.Strategy import Strategy


class BearishRSI(Strategy):

    def __init__(self,
                 name: str,
                 exchange: Exchange,
                 symbol: str,
                 budget_percent: int,
                 leverage: int,
                 notifier: Notifier,
                 ):
        super().__init__(
            name=name,
            exchange=exchange,
            budget_percent=budget_percent,
            leverage=leverage,
            notifier=notifier,
            symbol=symbol,
            main_tf='1m'
        )
        self.__entry_price = None
        self.__exit_price = None
        self.__stop_loss = 10

    @abstractmethod
    def execute(self):
        """
        Already have prices of main_tf on
        > super().prices('close')

        Alternatively we could fetch more with
        > super().fetch_prices('1d')
        and then do something with that
        > super().prices('close', timeframe='1d')
        """
        pass
