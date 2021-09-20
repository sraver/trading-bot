from discord_notify import Notifier as DiscordNotifier
import datetime


class Notifier:

    def __init__(self, handler: DiscordNotifier):
        self.__handler = handler

    def send(self, text):
        # self.__handler.send(message=text, print_message=False)
        self.__log_to_file(text)
        pass

    @staticmethod
    def __log_to_file(text):
        date = datetime.datetime.today()
        msg = f"{date} {text}\n"
        file = open('logs/trades.log', 'a')
        file.write(msg)

    @staticmethod
    def log(text):
        print(text)
