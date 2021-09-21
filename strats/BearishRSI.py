import talib

from strats.Strategy import Strategy


class BearishRSI(Strategy):

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
        self.__stop_loss = 10

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
