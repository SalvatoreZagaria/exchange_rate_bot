import os
import time
import datetime
import threading
from telegram.ext import Updater, CommandHandler

from monitor import ExchangeRateMonitor, WEBSITE

TOKEN = os.environ["EXC_RATE_TOKEN"]
monitor_thread = None
INTERVAL = 3600


class MonitorThread(threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.exc_rate_monitor = ExchangeRateMonitor(WEBSITE)
        self.id = id
        self.running = False
        self.updater = None

    def run(self):
        self.running = True
        while True:
            if not self.running:
                break
            gbp_eur = self.exc_rate_monitor.process_rates()

            if gbp_eur is None:
                msg = "[!] {} RATES NOT FOUND".format(datetime.datetime.now())
            else:
                msg = "GBP - EUR: {}".format(gbp_eur)

            self.updater.message.reply_text(msg)
            time.sleep(INTERVAL)

    def stop(self):
        self.running = False


def get_one(update, context):
    exc_rate_monitor = ExchangeRateMonitor(WEBSITE)

    gbp_eur = exc_rate_monitor.process_rates()

    if gbp_eur is None:
        msg = "[!] {} RATES NOT FOUND".format(datetime.datetime.now())
    else:
        msg = "GBP - EUR: {}".format(gbp_eur)

    update.message.reply_text(msg)


def start(update, context):
    global monitor_thread
    if monitor_thread is not None and monitor_thread.running:
        return
    monitor_thread = MonitorThread(0)
    monitor_thread.updater = update
    monitor_thread.start()


def stop(update, context):
    global monitor_thread
    if monitor_thread is not None and monitor_thread.running:
        monitor_thread.stop()
    monitor_thread = None


def set_interval(update, context):
    global monitor_thread, INTERVAL
    args = context.args
    if len(args) != 1:
        update.message.reply_text("One argument required.")
        return
    try:
        new_interval = int(args[0])
        if new_interval <= 0:
            update.message.reply_text("The new interval must be a number higher than 0.")

        run = False
        if monitor_thread is not None and monitor_thread.running:
            monitor_thread.stop()
            run = True

        INTERVAL = new_interval
        msg = "Interval updated to {}".format(INTERVAL)
        update.message.reply_text(msg)
        monitor_thread = MonitorThread(0)
        if run:
            monitor_thread.updater = update
            monitor_thread.start()
    except ValueError:
        update.message.reply_text("Impossible to convert argument to integer.")


def helper(update, context):
    msg = """Commands list:
    
/start - start to receive messages
/stop - stop to receive messages
/set_interval - update the interval between the messages
/get_one - get just one message now
/help - this helper"""

    update.message.reply_text(msg)


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("set_interval", set_interval))
    dp.add_handler(CommandHandler("get_one", get_one))
    dp.add_handler(CommandHandler("help", helper))

    # Start the Bot
    updater.start_polling()


if __name__ == "__main__":
    try:
        main()
        print("Bot is running...")
    except:
        monitor_thread.exc_rate_monitor.close()
