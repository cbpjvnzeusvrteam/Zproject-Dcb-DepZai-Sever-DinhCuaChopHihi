import requests, base64, uuid, json
from io import BytesIO
from PIL import Image
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from memory import load_user_memory, save_user_memory
from formatter import format_html

# ✨ Cấu hình endpoint
GEMINI_API_KEY = "AIzaSyDpmTfFibDyskBHwekOADtstWsPUCbIrzE"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
REMOTE_PROMPT_URL = "https://zcode.x10.mx/prompt.json"
REMOTE_LOG_HOST = "https://zcode.x10.mx/save.php"

def build_reply_button(user_id, question):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔁 Trả lời lại", callback_data=f"retry|{user_id}|{question}"))
    return markup

def handle_ask(bot, message):
    prompt = message.text.replace("/ask", "").strip()
    if not prompt:
        return bot.reply_to(message, "❓ Bạn chưa nhập câu hỏi rồi đó!")

    msg_status = bot.reply_to(message, "🤖")

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    memory = load_user_memory(user_id)

    try:
        # 📥 Tải prompt từ host
        prompt_data = requests.get(REMOTE_PROMPT_URL, timeout=5).json()
        system_prompt = prompt_data.get("prompt", "Bạn là AI thông minh vui vẻ.")

        # 🧠 Ghép kèm 5 câu cũ gần nhất
        history_block = ""
        if memory:
            for item in memory[-5:]:
                history_block += f"Người dùng hỏi: {item['question']}\nAI: {item['answer']}\n"

        full_prompt = f"{system_prompt}\n\n[Ngữ cảnh trước đó với {user_name}]\n{history_block}\nNgười dùng hiện tại hỏi: {prompt}"

        headers = {"Content-Type": "application/json"}
        parts = [{"text": full_prompt}]
        image_attached = False

        # 🖼️ Gửi ảnh nếu có
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

        # ✅ Lưu kèm user info
        entry = {
            "question": prompt,
            "answer": result,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "with_image": image_attached,
            "name": user_name
        }
        memory.append(entry)
        save_user_memory(user_id, memory)

        try:
            requests.post(
                f"{REMOTE_LOG_HOST}?uid={user_id}",
                data=json.dumps(memory, ensure_ascii=False),
                headers={"Content-Type": "application/json"},
                timeout=5
            )
        except Exception as e:
            print(f"[⚠️] Gửi host thất bại: {e}")

        formatted = format_html(result)
        markup = build_reply_button(user_id, prompt)

        if len(formatted) > 4000:
            filename = f"zproject_{uuid.uuid4().hex[:6]}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(formatted)
            bot.send_document(
                message.chat.id,
                open(filename, "rb"),
                caption="📄 Trả lời dài quá nên gửi file nha!",
                parse_mode="HTML"
            )
        else:
            bot.edit_message_text(
                f"🤖 <i>ZProject [ WORMGPT ] trả lời:</i>\n\n<b>{formatted}</b>",
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