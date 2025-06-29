import os, threading, datetime
from flask import Flask, request
import telebot

from ask_handler import handle_ask
from callback import handle_retry_button
from utils import auto_group_greeting
from memory import load_groups, save_groups
from start_handler import handle_start
from dataall_handler import handle_dataall
from greeting_group_handler import handle_bot_added

TOKEN = "7053031372:AAGGOnE72JbZat9IaXFqa-WRdv240vSYjms"
APP_URL = "https://sever-zproject.onrender.com"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
START_TIME = datetime.datetime.now()
GROUP_FILE = "groups.json"

GROUPS = load_groups()

@app.route("/")
def home():
    return "<h3>🤖 ZProject đang hoạt động!</h3>"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "!", 200

@bot.message_handler(commands=["time"])
def uptime(message):
    uptime = datetime.datetime.now() - START_TIME
    bot.reply_to(message, f"⏳ Bot đã chạy: {str(uptime).split('.')[0]}")

@bot.message_handler(commands=["start"])
def start_cmd(message):
    handle_start(bot, message)
    
@bot.message_handler(commands=["ask"])
def ask_command(message):
    handle_ask(bot, message)

@bot.message_handler(commands=["dataall"])
def dataall_command(message):
    handle_dataall(bot, message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("retry|"))
def retry_button(call):
    handle_retry_button(bot, call)

@bot.callback_query_handler(func=lambda call: call.data == "export_stats")
def export_stats_txt(call):
    from dataall_handler import export_stats_txt
    export_stats_txt(bot, call)

@bot.message_handler(func=lambda msg: True)
def track_groups(msg):
    if msg.chat.type in ['group', 'supergroup']:
        GROUPS.add(msg.chat.id)
        save_groups(GROUPS)


@bot.message_handler(func=lambda m: m.new_chat_members)
def greet_group_joined(message):
    handle_bot_added(bot, message)
    
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    threading.Thread(target=auto_group_greeting, args=(bot, GROUPS)).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))