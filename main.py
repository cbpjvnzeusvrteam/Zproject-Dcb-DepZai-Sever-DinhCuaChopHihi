import telebot
from flask import Flask, request
import os, threading, datetime, json

# --- Cấu hình ---
TOKEN = "7411942861:AAH2yZqA5yL3oy1wEmunhFPrT8ftXDXJDWs"
ADMIN_ID = 5819094246
GROUP_FILE = "groups.json"
APP_URL = "https://severdcb-1709.onrender.com"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
START_TIME = datetime.datetime.now()

# --- Ghi / Đọc nhóm ---
def load_groups():
    if os.path.exists(GROUP_FILE):
        with open(GROUP_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_groups(groups):
    with open(GROUP_FILE, "w") as f:
        json.dump(list(groups), f)

GROUPS = load_groups()

@app.route("/")
def home():
    return "<h3>🤖 Bot ZProject đang hoạt động qua webhook!</h3>"

@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# --- /start ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "🤖 Bot hiện chưa có lệnh vì admin chưa suy nghĩ ra:v, bạn có thể hợp tác bot với admin liên hệ @zproject2")

# --- /donggop ---
@bot.message_handler(commands=['donggop'])
def dong_gop(message):
    content = message.text.replace("/donggop", "").strip()
    if not content:
        return bot.reply_to(message, "✏️ Vui lòng nhập nội dung sau lệnh /donggop")

    sender = f"👤 Góp ý từ @{message.from_user.username or 'Không có username'} (ID: {message.from_user.id}):\n"
    full_text = sender + content

    try:
        bot.send_message(ADMIN_ID, full_text)
        bot.reply_to(message, "✅ Cảm ơn bạn đã góp ý! Admin sẽ xem xét sớm.")
    except:
        bot.reply_to(message, "❌ Lỗi khi gửi góp ý đến admin.")

# --- /time ---
@bot.message_handler(commands=['time'])
def uptime_cmd(message):
    uptime = datetime.datetime.now() - START_TIME
    bot.reply_to(message, f"⏳ Bot đã hoạt động được: {str(uptime).split('.')[0]}")

# --- Theo dõi nhóm ---
@bot.message_handler(func=lambda msg: True)
def track_groups(msg):
    if msg.chat.type in ['group', 'supergroup']:
        GROUPS.add(msg.chat.id)
        save_groups(GROUPS)

# --- Tự động gửi tin nhắn chào ---
def auto_group_greeting():
    while True:
        import time
        time.sleep(1800)
        for group_id in GROUPS:
            try:
                bot.send_message(group_id, "👋 Xin chào các bạn! ZProject đây nè :v , Có Ý Kiến Hay Gì Để Admin Cập Nhật Cho Bot Hong Chứ Bot Chưa Có Lệnh Gi Het a:( , ghi lệnh /donggop và ý kiến đóng góp lệnh của bạn nhé :>>\n Bot ZProject Hoạt Động 24/7 🌍")
            except:
                pass

# --- Khởi tạo ---
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    threading.Thread(target=auto_group_greeting).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))