import os
import time
import datetime
import threading
from telegram.ext import Updater, CommandHandler

from monitor import ExchangeRateMonitor, WEBSITE

TOKEN = os.environ["EXC_RATE_TOKEN"]
CURRENT_VALUE = "No results found."


class MonitorThread(threading.Thread):
    def __init__(self, interval=300):
        threading.Thread.__init__(self)
        self.interval = interval
        self.exc_rate_monitor = ExchangeRateMonitor(WEBSITE)

    def run(self):
        global CURRENT_VALUE
        while True:
            gbp_eur = self.exc_rate_monitor.process_rates()

            if gbp_eur is None:
                CURRENT_VALUE = "[!] {} RATES NOT FOUND".format(datetime.datetime.now())
            else:
                CURRENT_VALUE = "GBP - EUR: {}".format(gbp_eur)

            time.sleep(self.interval)


class SenderThread(threading.Thread):
    def __init__(self, updater, interval=60):
        threading.Thread.__init__(self)
        self.interval = interval
        self.updater = updater
        self.running = False

    def run(self):
        self.running = True
        global CURRENT_VALUE
        while True:
            if not self.running:
                break

            self.updater.message.reply_text(CURRENT_VALUE)
            time.sleep(self.interval)

    def stop(self):
        self.running = False

    def send_message(self, msg):
        self.updater.message.reply_text(msg)


MAIN_THREAD = MonitorThread()
MAIN_THREAD.start()

sender_threads = {}


def get_one(update, context):
    global CURRENT_VALUE
    update.message.reply_text(CURRENT_VALUE)


def start(update, context):
    user_id = update.effective_user.id
    sender_thread = sender_threads.get(user_id, None)
    if sender_thread is not None and sender_thread.running:
        update.message.reply_text("Bot is running already.")
        return
    sender_thread = SenderThread(update)
    sender_thread.start()
    sender_threads[user_id] = sender_thread


def stop(update, context):
    user_id = update.effective_user.id
    sender_thread = sender_threads.get(user_id, None)
    if sender_thread is None or (sender_thread is not None and not sender_thread.running):
        update.message.reply_text("Bot is stopped already.")
        return
    sender_thread.stop()
    sender_threads[user_id] = None

    update.message.reply_text("Stopped.")


def set_interval(update, context):
    user_id = update.effective_user.id
    sender_thread = sender_threads.get(user_id, None)

    args = context.args
    if len(args) != 1:
        update.message.reply_text("One argument required.")
        return
    try:
        new_interval = int(args[0])
        if new_interval <= 0:
            update.message.reply_text("The new interval must be a number higher than 0.")

        run = False
        if sender_thread is not None and sender_thread.running:
            sender_thread.stop()
            run = True
        elif sender_thread is None or (sender_thread is not None and not sender_thread.running):
            update.message.reply_text("Bot must be running.")
            return

        sender_thread = SenderThread(update, interval=new_interval * 60)

        msg = "Interval updated to {}".format(new_interval)
        update.message.reply_text(msg)
        if run:
            update.message.reply_text("Retrieving...")
            sender_thread.start()

        sender_threads[user_id] = sender_thread
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
        for th in sender_threads.values():
            th.send_message(shutting_down)
        print(shutting_down)
