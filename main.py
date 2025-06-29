import telebot
from flask import Flask, request
import os, threading, datetime, json, time

# --- Cấu hình ---
TOKEN = "7411942861:AAH2yZqA5yL3oy1wEmunhFPrT8ftXDXJDWs"
ADMIN_ID = 5819094246
GROUP_FILE = "groups.json"
APP_URL = "https://sever-zproject.onrender.com"

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
    return "<h3>🤖 Bot ZProject đang hoạt động bằng Webhook!</h3>"

@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# --- Lệnh /start ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "🤖 Xin chào! Gõ /donggop <nội dung> để góp ý nha!")

# --- Lệnh /donggop ---
@bot.message_handler(commands=['donggop'])
def dong_gop(message):
    content = message.text.replace("/donggop", "").strip()
    if not content:
        return bot.reply_to(message, "✏️ Gõ nội dung sau lệnh /donggop để gửi góp ý nhé.")
    sender = f"👤 Góp ý từ @{message.from_user.username or 'Không có username'} (ID: {message.from_user.id}):\n"
    try:
        bot.send_message(ADMIN_ID, sender + content)
        bot.reply_to(message, "✅ Cảm ơn bạn đã góp ý!")
    except:
        bot.reply_to(message, "❌ Không gửi được góp ý. Admin ngủ quên rồi 😅")

# --- Lệnh /time ---
@bot.message_handler(commands=['time'])
def uptime_cmd(message):
    uptime = datetime.datetime.now() - START_TIME
    bot.reply_to(message, f"⏳ Bot đã chạy được: {str(uptime).split('.')[0]}")

# --- Lưu ID nhóm nếu được thêm vào group ---
@bot.message_handler(func=lambda msg: True)
def track_groups(msg):
    if msg.chat.type in ['group', 'supergroup']:
        GROUPS.add(msg.chat.id)
        save_groups(GROUPS)

# --- Gửi tin nhắn chào mỗi 30 phút ---
def auto_group_greeting():
    while True:
        time.sleep(1800)
        for group_id in GROUPS:
            try:
                bot.send_message(group_id, "👋 Chào mọi người! Góp ý lệnh mới bằng cách gõ /donggop <nội dung> nhé!")
            except:
                pass

# --- Khởi động Flask, webhook và gửi tin định kỳ ---
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    print("🔗 Webhook info:", bot.get_webhook_info())
    threading.Thread(target=auto_group_greeting).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))