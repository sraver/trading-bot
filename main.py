import schedule
import time
import ccxt
import config
import discord_notify as dn

from external.Exchange import Exchange
from external.Notifier import Notifier
from strats.BullishRSI import BullishRSI

notifier = Notifier(handler=dn.Notifier(config.DISCORD_WEBHOOK_URL))
ccxt_handler = ccxt.binanceusdm({
    "apiKey": config.BINANCE_API_KEY,
    "secret": config.BINANCE_SECRET_KEY
})

exchange = Exchange(exchange=ccxt_handler)

strats = [
    BullishRSI(exchange=exchange, notifier=notifier, symbol="ETH/USDT", budget_percent=5, leverage=10,
               name='BullishEth')
]

for strat in strats:
    schedule.every(5).seconds.do(strat.run)

while True:
    schedule.run_pending()
    time.sleep(1)
