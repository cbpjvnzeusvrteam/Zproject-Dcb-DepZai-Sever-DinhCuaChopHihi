import os, threading, datetime
from flask import Flask, request
import telebot

from ask_handler import handle_ask
from callback import handle_retry_button
from utils import auto_group_greeting
from memory import load_groups, save_groups

TOKEN = "7053031372:AAGGOnE72JbZat9IaXFqa-WRdv240vSYjms"
APP_URL = "https://sever-zproject.onrender.com"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
START_TIME = datetime.datetime.now()
GROUP_FILE = "groups.json"

# Ghi nhớ nhóm chat
GROUPS = load_groups()

# Trang chủ
@app.route("/")
def home():
    return "<h3>🤖 Bot ZProject đang hoạt động!</h3>"

# Webhook callback
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "!", 200

# Lệnh thời gian uptime
@bot.message_handler(commands=["time"])
def uptime(message):
    uptime = datetime.datetime.now() - START_TIME
    bot.reply_to(message, f"⏳ Bot đã chạy: {str(uptime).split('.')[0]}")

# Lệnh /ask -> gọi từ module riêng
@bot.message_handler(commands=["ask"])
def ask_command(message):
    handle_ask(bot, message)

# Xử lý callback nút "🔁 Trả lời lại"
@bot.callback_query_handler(func=lambda call: call.data.startswith("retry|"))
def callback_retry(call):
    handle_retry_button(bot, call)

# Theo dõi nhóm mới
@bot.message_handler(func=lambda msg: True)
def track_groups(msg):
    if msg.chat.type in ['group', 'supergroup']:
        GROUPS.add(msg.chat.id)
        save_groups(GROUPS)

# Bắt đầu webhook và luồng lời chào
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    threading.Thread(target=auto_group_greeting, args=(bot, GROUPS)).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))