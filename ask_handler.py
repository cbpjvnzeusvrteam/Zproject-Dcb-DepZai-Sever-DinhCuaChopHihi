import requests, base64, uuid
from io import BytesIO
from PIL import Image
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from memory import load_user_memory, save_user_memory
from formatter import format_html

# 🔑 API Key và Endpoint Gemini
GEMINI_API_KEY = "AIzaSyDpmTfFibDyskBHwekOADtstWsPUCbIrzE"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# 🎨 Phong cách AI
AI_PROMPT_STYLE = {
    "ai_name": "Zproject X Dcb",
    "prompt": "Hãy trả lời yêu cầu của tôi theo phong cách dễ thương, thông minh ✨"
}

# 🔁 Tạo InlineButton để người dùng trả lời lại
def build_reply_button(user_id, question):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔁 Trả lời lại", callback_data=f"retry|{user_id}|{question}"))
    return markup

# 🚀 Hàm chính xử lý lệnh /ask
def handle_ask(bot, message):
    prompt = message.text.replace("/ask", "").strip()
    if not prompt:
        return bot.reply_to(message, "❓ Bạn chưa nhập câu hỏi rồi kìa!")

    msg_status = bot.reply_to(message, "⏳ Đang hỏi Gemini...")

    user_id = message.from_user.id
    memory = load_user_memory(user_id)

    try:
        headers = {"Content-Type": "application/json"}
        full_prompt = f"{AI_PROMPT_STYLE['prompt']}\n\nNgười dùng hỏi: {prompt}"
        parts = [{"text": full_prompt}]
        image_attached = False

        # 🖼️ Nếu có ảnh
        if message.reply_to_message and message.reply_to_message.photo:
            photo = message.reply_to_message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded = bot.download_file(file_info.file_path)

            image = Image.open(BytesIO(downloaded))
            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            base64_img = base64.b64encode(buffer.getvalue()).decode()

            parts.insert(0, {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": base64_img
                }
            })
            image_attached = True

        # 🧠 Gửi tới Gemini
        data = {"contents": [{"parts": parts}]}
        res = requests.post(GEMINI_URL, headers=headers, json=data)

        if res.status_code != 200:
            return bot.edit_message_text(
                f"❌ API lỗi:\n<pre>{res.text}</pre>",
                msg_status.chat.id,
                msg_status.message_id,
                parse_mode="HTML"
            )

        result = res.json()["candidates"][0]["content"]["parts"][0]["text"]

        # 💾 Ghi lại bộ nhớ user
        memory.append({
            "question": prompt,
            "answer": result,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "with_image": image_attached
        })
        save_user_memory(user_id, memory)

        formatted = format_html(result)
        markup = build_reply_button(user_id, prompt)

        if len(formatted) > 4000:
            filename = f"zproject_{uuid.uuid4().hex[:6]}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(formatted)
            bot.send_document(
                message.chat.id,
                open(filename, "rb"),
                caption="📄 Phản hồi dài quá nên gửi file nè!",
                parse_mode="HTML"
            )
        else:
            bot.edit_message_text(
                f"🤖 <b>{AI_PROMPT_STYLE['ai_name']} trả lời:</b>\n\n{formatted}",
                msg_status.chat.id,
                msg_status.message_id,
                parse_mode="HTML",
                reply_markup=markup
            )

    except Exception as e:
        bot.edit_message_text(
            f"⚠️ Lỗi xử lý:\n<code>{e}</code>",
            msg_status.chat.id,
            msg_status.message_id,
            parse_mode="HTML"
        )