import os
import time
import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from monitor import ExchangeRateMonitor, WEBSITE

TOKEN = os.environ["EXC_RATE_TOKEN"]
exc_rate_monitor = ExchangeRateMonitor(WEBSITE)

INTERVAL = 5


def start(update, context):
    # TODO: We might start a new process and save the pid, so we can kill it in the stop function
    while True:
        gbp_eur = exc_rate_monitor.process_rates()
        if gbp_eur is None:
            msg = "[!] {} RATES NOT FOUND".format(datetime.datetime.now())
        else:
            msg = "GBP - EUR: {}".format(gbp_eur)

        update.message.reply_text(msg)
        time.sleep(5)


def stop(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))

    # Start the Bot
    updater.start_polling()


if __name__ == "__main__":
    main()
