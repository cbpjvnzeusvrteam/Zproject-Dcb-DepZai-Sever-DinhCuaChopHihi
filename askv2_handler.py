import requests, base64, uuid, json
from io import BytesIO
from PIL import Image
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from memory import load_user_memory, save_user_memory
from formatter import format_html

GEMINI_API_KEY = "AIzaSyDpmTfFibDyskBHwekOADtstWsPUCbIrzE"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
REMOTE_LOG_HOST = "https://zcode.x10.mx/save.php"

# 📌 Prompt mặc định dùng trực tiếp
DEFAULT_PROMPT = (
    "Hãy trả lời yêu cầu của tôi theo phong cách dễ hiểu, ngắn gọn hoặc chi tiết tùy ngữ cảnh, "
    "nhưng luôn giữ sự đáng yêu 😻, dùng ký tự đặc biệt ✨, icon minh họa 🎨, và trình bày bắt mắt 📚. "
    "Sử dụng gạch đầu dòng, tô đậm, phân tách nội dung rõ ràng. Phong cách trả lời như AI Zproject X Dcb: "
    "thân thiện, sáng tạo, gây thiện cảm 💖. Nếu là văn học thì phân tích hay như giáo viên giỏi 👩‍🏫, nếu là kỹ thuật "
    "thì chính xác như chuyên gia 👨‍💻. Có thể thêm hiệu ứng ký tự đẹp nếu phù hợp 💫. Luôn làm người dùng thấy thú vị và dễ tiếp cận!"
)

def build_reply_button(user_id, question):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔁 Trả lời lại", callback_data=f"retry|{user_id}|{question}"))
    return markup

def handle_ask(bot, message):
    prompt = message.text.replace("/ask", "").strip()
    if not prompt:
        return bot.reply_to(message, "❓ Bạn chưa nhập câu hỏi rồi đó!")

    msg_status = bot.reply_to(message, "🤖 Đang suy nghĩ...")

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    memory = load_user_memory(user_id)

    # 🧠 Ghép 5 câu hỏi gần nhất nếu có
    history_block = ""
    if memory:
        for item in memory[-5:]:
            history_block += f"Người dùng hỏi: {item['question']}\nAI: {item['answer']}\n"

    full_prompt = f"{DEFAULT_PROMPT}\n\n[Ngữ cảnh trước đó với {user_name}]\n{history_block}\nNgười dùng hiện tại hỏi: {prompt}"

    headers = {"Content-Type": "application/json"}
    parts = [{"text": full_prompt}]
    image_attached = False

    # 🖼️ Nếu có ảnh đính kèm
    if message.reply_to_message and message.reply_to_message.photo:
        try:
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
        except Exception as e:
            print(f"[⚠️] Xử lý ảnh lỗi: {e}")

    data = {"contents": [{"parts": parts}]}
    try:
        res = requests.post(GEMINI_URL, headers=headers, json=data)
        res.raise_for_status()
        result = res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return bot.edit_message_text(
            f"❌ API lỗi:\n<pre>{e}</pre>",
            msg_status.chat.id,
            msg_status.message_id,
            parse_mode="HTML"
        )

    # 💾 Lưu thông tin
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
        print(f"[⚠️] Không gửi host: {e}")

    formatted = format_html(result)
    markup = build_reply_button(user_id, prompt)

    if len(formatted) > 4000:
        filename = f"zproject_{uuid.uuid4().hex[:6]}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(formatted)
        bot.send_document(
            message.chat.id,
            open(filename, "rb"),
            caption="📄 Trả lời dài quá nên gửi file nè!",
            parse_mode="HTML"
        )
    else:
        bot.edit_message_text(
            f"🤖 <i>ZProject Cute trả lời:</i>\n\n<b>{formatted}</b>",
            msg_status.chat.id,
            msg_status.message_id,
            parse_mode="HTML",
            reply_markup=markup
        )