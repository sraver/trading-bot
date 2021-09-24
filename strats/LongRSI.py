import talib

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
            main_tf='1m'
        )
        self.__entry_price = None
        self.__exit_price = None
        self.__stop_loss = 7

    def execute(self):
        secondary_tf = '15m'
        self.fetch_prices(secondary_tf)
        rsi_1m = talib.RSI(self.prices(column='close'), timeperiod=14)
        rsi_15m = talib.RSI(self.prices(column='close', timeframe=secondary_tf), timeperiod=14)

        last_price = self.last_price('close')
        self.notifier().log(f"\n{self.symbol()} -- Mark price: {last_price} / Position: {self.in_position()}")

        if not self.in_position() and self.is_buy_opportunity(rsi_1m, rsi_15m):
            self.buy()
            self.notifier().send(f'[{self.name()}] Buy @ {self.__entry_price}')

        if self.in_position() and self.is_sell_opportunity(rsi_1m, rsi_15m):
            self.sell()
            gains = self.pnl_percent(self.__entry_price, self.__exit_price)
            self.notifier().send(f'[{self.name()}] Sell @ {self.__exit_price} # PNL {gains}%')

        if self.in_position():
            gains = self.pnl_percent(self.__entry_price, last_price)
            self.__show_stats(last_price, gains)

            if gains <= -self.__stop_loss:
                self.sell()
                self.notifier().send(f'[{self.name()}] SL @ {self.__exit_price} # PNL {gains}')

    def __show_stats(self, last_price, gains):
        self.notifier().log(f"Bought at: {self.__entry_price} / Current: {last_price}")
        percent = self.price_difference(self.__entry_price, last_price)
        self.notifier().log(f'SL at {self.__stop_loss}%. Current PNL:  {gains}% / Price diff: {percent}')

    def is_buy_opportunity(self, rsi_1m, rsi_15m):
        valid_rsi_1m = rsi_1m.iloc[-1] <= 30
        valid_rsi_15m = (rsi_15m.iloc[-3:] <= 30).all()
        return valid_rsi_1m and valid_rsi_15m

    def is_sell_opportunity(self, rsi_1m, rsi_15m):
        valid_rsi_1m = rsi_1m.iloc[-1] >= 70
        valid_rsi_15m = rsi_15m.iloc[-1] >= 70
        return valid_rsi_1m and valid_rsi_15m

    def buy(self):
        self.market_in('buy')
        self.__entry_price = self.order().avg_price()

    def sell(self):
        self.market_out('sell')
        self.__exit_price = self.order().avg_price()
