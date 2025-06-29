import os, threading, datetime
from flask import Flask, request
import telebot

from ask_handler import handle_ask
from callback import handle_retry_button
from utils import auto_group_greeting
from memory import load_groups, save_groups
from start_handler import handle_start
from dataall_handler import handle_dataall

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

@bot.message_handler(commands=["dataall"])
def admin_data(message):
    handle_dataall(bot, message)
    
@bot.message_handler(commands=["start"])
def start_cmd(message):
    handle_start(bot, message)
    
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

@bot.callback_query_handler(func=lambda call: call.data == "export_stats")
def export_stats_txt(call):
    if call.from_user.id != ADMIN_ID:
        return bot.answer_callback_query(call.id, "🚫 Không đủ quyền.")

    stats_files = [f for f in os.listdir() if f.startswith("zprojectxdcb_thongke_lanthu_") and f.endswith(".txt")]
    index = len(stats_files)
    file_name = f"zprojectxdcb_thongke_lanthu_{index}.txt"

    content = f"""📊 Thống kê ZPROJECT lần {index}\n
Tổng user: {len([f for f in os.listdir() if f.startswith("memory_")])}
Tổng group: {len(json.load(open("groups.json")) if os.path.exists("groups.json") else [])}
Lượt dùng /ask hôm nay: Tính toán ở file dataall_handler.py nha 😉
"""

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(content)

    bot.send_document(call.message.chat.id, open(file_name, "rb"), caption=f"📄 ZProject Thống kê #{index}")
    os.remove(file_name)
    bot.answer_callback_query(call.id, "✅ Đã xuất xong thống kê!")
    
# Bắt đầu webhook và luồng lời chào
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    threading.Thread(target=auto_group_greeting, args=(bot, GROUPS)).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))