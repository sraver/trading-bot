from discord_notify import Notifier as DiscordNotifier
import datetime
import config


class Notifier:

    def __init__(self):
        self.__handler = DiscordNotifier(config.DISCORD_WEBHOOK_URL)

    def send(self, text):
        try:
            self.__handler.send(message=text, print_message=False)
        except:
            # If no Webhook was set or it fails, show must go on
            pass
        self.__log_to_file(text)

    @staticmethod
    def __log_to_file(text):
        date = datetime.datetime.today()
        msg = f"{date} {text}\n"
        file = open('logs/trades.log', 'a')
        file.write(msg)

    @staticmethod
    def log(text):
        print(text)
