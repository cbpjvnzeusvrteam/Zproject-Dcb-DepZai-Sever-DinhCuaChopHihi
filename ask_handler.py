import requests, base64, uuid
from io import BytesIO
from PIL import Image
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from memory import load_user_memory, save_user_memory
from formatter import format_html

# ✅ API cũ (v1beta) vẫn ổn định hơn nếu dùng key từ MakerSuite
GEMINI_API_KEY = "YOUR_API_KEY"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

AI_PROMPT_STYLE = {
    "ai_name": "Zproject X Dcb",
    "prompt": "Hãy trả lời yêu cầu của tôi theo phong cách dễ thương, thông minh ✨"
}

def build_reply_button(user_id, question):
    data = f"retry|{user_id}|{question}"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔁 Trả lời lại", callback_data=data))
    return markup

def handle_ask(bot, message):
    prompt = message.text.replace("/ask", "").strip()
    if not prompt:
        return bot.reply_to(message, "❓ Gõ /ask <câu hỏi> nhen!")

    msg_status = bot.reply_to(message, "⏳ Đang xử lý với Gemini...")

    user_id = message.from_user.id
    memory = load_user_memory(user_id)

    try:
        headers = {"Content-Type": "application/json"}
        full_prompt = f"{AI_PROMPT_STYLE['prompt']}\n\nNgười dùng hỏi: {prompt}"
        parts = [{"text": full_prompt}]

        # Nếu có ảnh đính kèm
        if message.reply_to_message and message.reply_to_message.photo:
            photo = message.reply_to_message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            image = Image.open(BytesIO(downloaded_file))
            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            base64_img = base64.b64encode(buffer.getvalue()).decode()

            parts.insert(0, {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": base64_img
                }
            })

        data = {"contents": [{"parts": parts}]}
        res = requests.post(GEMINI_URL, headers=headers, json=data)

        if res.status_code != 200:
            return bot.edit_message_text(f"❌ API lỗi:\n<pre>{res.text}</pre>", msg_status.chat.id, msg_status.message_id, parse_mode="HTML")

        result = res.json()["candidates"][0]["content"]["parts"][0]["text"]
        memory.append({"question": prompt, "answer": result})
        save_user_memory(user_id, memory)

        formatted = format_html(result)
        markup = build_reply_button(user_id, prompt)

        if len(formatted) > 4000:
            filename = f"zproject_{uuid.uuid4().hex[:6]}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(formatted)
            bot.send_document(message.chat.id, open(filename, "rb"), caption="📄 Phản hồi dài quá nên gửi file nè!", parse_mode="HTML")
        else:
            bot.edit_message_text(
                f"🤖 <b>{AI_PROMPT_STYLE['ai_name']} trả lời:</b><br><br>{formatted}",
                msg_status.chat.id,
                msg_status.message_id,
                parse_mode="HTML",
                reply_markup=markup
            )

    except Exception as e:
        bot.edit_message_text(f"⚠️ Lỗi xử lý: {str(e)}", msg_status.chat.id, msg_status.message_id)