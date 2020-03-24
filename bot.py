import os
import time
import datetime
import threading
from telegram.ext import Updater, CommandHandler

from monitor import ExchangeRateMonitor, WEBSITE

TOKEN = os.environ["EXC_RATE_TOKEN"]
monitor_threads = {}


class MonitorThread(threading.Thread):
    def __init__(self, updater, interval=60):
        threading.Thread.__init__(self)
        self.exc_rate_monitor = ExchangeRateMonitor(WEBSITE)
        self.interval = interval
        self.updater = updater
        self.running = False

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
            time.sleep(self.interval)

    def stop(self):
        self.running = False

    def send_message(self, msg):
        self.updater.message.reply_text(msg)


def get_one(update, context):
    update.message.reply_text("Retrieving...")

    exc_rate_monitor = ExchangeRateMonitor(WEBSITE)

    gbp_eur = exc_rate_monitor.process_rates()

    if gbp_eur is None:
        msg = "[!] {} RATES NOT FOUND".format(datetime.datetime.now())
    else:
        msg = "GBP - EUR: {}".format(gbp_eur)

    update.message.reply_text(msg)


def start(update, context):
    update.message.reply_text("Retrieving...")

    user_id = update.effective_user.id
    monitor_thread = monitor_threads.get(user_id, None)
    if monitor_thread is not None and monitor_thread.running:
        update.message.reply_text("Bot is running already.")
        return
    monitor_thread = MonitorThread(update)
    monitor_thread.start()
    monitor_threads[user_id] = monitor_thread


def stop(update, context):
    user_id = update.effective_user.id
    monitor_thread = monitor_threads.get(user_id, None)
    if monitor_thread is None or (monitor_thread is not None and not monitor_thread.running):
        update.message.reply_text("Bot is stopped already.")
        return
    monitor_thread.stop()
    monitor_threads[user_id] = None

    update.message.reply_text("Retrieving...")


def set_interval(update, context):
    user_id = update.effective_user.id
    monitor_thread = monitor_threads.get(user_id, None)

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
        elif monitor_thread is None or (monitor_thread is not None and not monitor_thread.running):
            update.message.reply_text("Bot must be running.")
            return

        monitor_thread = MonitorThread(update, interval=new_interval * 60)

        msg = "Interval updated to {}".format(new_interval)
        update.message.reply_text(msg)
        if run:
            update.message.reply_text("Retrieving...")
            monitor_thread.start()

        monitor_threads[user_id] = monitor_thread
    except ValueError:
        update.message.reply_text("Impossible to convert argument to integer.")


def helper(update, context):
    msg = """Commands list:
    
/start - start to receive messages
/stop - stop to receive messages
/set_interval - update the interval between the messages (minutes)
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
        shutting_down = "Bot is shutting down."
        for th in monitor_threads.values():
            th.send_message(shutting_down)
            th.stop()
        print(shutting_down)
