import schedule
import time

from strats.BullishRSI import BullishRSI

# TODO : check for config.py existence

strats = [
    BullishRSI(symbol="ETH/USDT", budget_percent=5, leverage=10, name='BullishEth')
]

for strat in strats:
    schedule.every(5).seconds.do(strat.run)

while True:
    schedule.run_pending()
    time.sleep(1)


