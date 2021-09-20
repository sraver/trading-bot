class Order:
    def __init__(self, order):
        self.__order = order

    def avg_price(self) -> float:
        return float(self.__order['info']['avgPrice'])

    def __str__(self):
        return self.__order
