import telebot
from flask import Flask, request
import os, threading, datetime, json, time, base64, requests, uuid
from io import BytesIO
from PIL import Image

# --- Cấu hình ---
TOKEN = "7053031372:AAGGOnE72JbZat9IaXFqa-WRdv240vSYjms"
ADMIN_ID = 5819094246
GROUP_FILE = "groups.json"
APP_URL = "https://sever-zproject.onrender.com"
GEMINI_API_KEY = "AIzaSyBOsmZmvERr-BzIb8nfjyPd0EDsDCoCedQ"
GEMINI_VISION_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={GEMINI_API_KEY}"
GEMINI_TEXT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
START_TIME = datetime.datetime.now()

# --- AI Style Prompt ---
AI_PROMPT_STYLE = {
    "ai_name": "Zproject X Dcb",
    "style": "dễ thương, thông minh, trình bày bắt mắt",
    "prompt": "Hãy trả lời yêu cầu của tôi theo phong cách dễ hiểu, ngắn gọn hoặc chi tiết tùy ngữ cảnh, nhưng luôn giữ sự đáng yêu 😻, dùng ký tự đặc biệt ✨, icon minh họa 🎨, và trình bày bắt mắt 📚. Sử dụng gạch đầu dòng, tô đậm, phân tách nội dung rõ ràng. Phong cách trả lời như AI Zproject X Dcb: thân thiện, sáng tạo, gây thiện cảm 💖. Nếu là văn học thì phân tích hay như giáo viên giỏi 👩‍🏫, nếu là kỹ thuật thì chính xác như chuyên gia 👨‍💻. Có thể thêm hiệu ứng ký tự đẹp nếu phù hợp 💫. Luôn làm người dùng thấy thú vị và dễ tiếp cận!"
}

# --- Ghi nhớ người dùng ---
def load_user_memory(user_id):
    path = f"memory_{user_id}.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_user_memory(user_id, history):
    path = f"memory_{user_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history[-10:], f, ensure_ascii=False, indent=2)

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

# --- Trang chủ ---
@app.route("/")
def home():
    return "<h3>🤖 Bot ZProject đang hoạt động bằng Webhook!</h3>"

# --- Webhook nhận dữ liệu ---
@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# --- /start ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "🤖 Xin chào! Gõ /donggop <nội dung> để góp ý nha, chứ admin éo biet làm lệnh gì:v!")

# --- /donggop ---
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

# --- /time ---
@bot.message_handler(commands=['time'])
def uptime_cmd(message):
    uptime = datetime.datetime.now() - START_TIME
    bot.reply_to(message, f"⏳ Bot đã chạy được: {str(uptime).split('.')[0]}")

# --- /ask ---
@bot.message_handler(commands=['ask'])
def handle_ask(message):
    prompt = message.text.replace("/ask", "").strip()
    if not prompt:
        return bot.reply_to(message, "❓ Bạn chưa nhập câu hỏi. Hãy gõ /ask <câu hỏi>.")

    bot.reply_to(message, "⏳ Đang xử lý với Gemini...")

    user_id = message.from_user.id
    memory = load_user_memory(user_id)

    try:
        headers = {"Content-Type": "application/json"}
        full_prompt = f"{AI_PROMPT_STYLE['prompt']}\n\nNgười dùng hỏi: {prompt}"
        data = {"contents": [{"parts": [{"text": full_prompt}]}]}

        # Có ảnh → dùng Vision
        if message.reply_to_message and message.reply_to_message.photo:
            photo = message.reply_to_message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            image = Image.open(BytesIO(downloaded_file))
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

            data["contents"][0]["parts"].insert(0, {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": base64_image
                }
            })
            url = GEMINI_VISION_URL
        else:
            url = GEMINI_TEXT_URL

        # Gửi tới Gemini
        res = requests.post(url, headers=headers, json=data)

        if res.status_code != 200:
            return bot.reply_to(message, f"❌ Lỗi API Gemini: {res.status_code} - {res.text}")

        result = res.json()["candidates"][0]["content"]["parts"][0]["text"]
        memory.append({"question": prompt, "answer": result})
        save_user_memory(user_id, memory)

        # Nếu quá dài thì gửi file
        if len(result) > 4000:
            filename = f"zprojectxdcb_{uuid.uuid4().hex[:6]}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(result)
            bot.send_document(
                message.chat.id,
                open(filename, "rb"),
                caption=f"📚 <b>Phản hồi quá dài nên được lưu thành file</b>, @{message.from_user.username or message.from_user.first_name}!",
                parse_mode="HTML"
            )
            os.remove(filename)
        else:
            bot.reply_to(message, f"🤖 <b>{AI_PROMPT_STYLE['ai_name']} trả lời:</b>\n\n{result}", parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi xử lý: {str(e)}")

# --- Theo dõi group ---
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

# --- Khởi động Flask Webhook ---
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    print("🔗 Webhook info:", bot.get_webhook_info())
    threading.Thread(target=auto_group_greeting).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))