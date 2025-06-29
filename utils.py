import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🧠 Gửi tin nhắn chào nhóm mỗi 30 phút (tuỳ chọn)
def auto_group_greeting(bot, groups):
    while True:
        time.sleep(1800)  # 30 phút
        for group_id in groups:
            try:
                bot.send_message(group_id, "👋 Hello cả nhà! Dùng /ask hoặc /worm để hỏi AI ZProject nha!")
            except:
                pass

# ➕ Gửi nút mời bot vào nhóm
def send_add_bot_button(bot, chat_id, bot_username):
    url = f"https://t.me/{bot_username}?startgroup=true"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("➕ Thêm ZProject vào nhóm", url=url))
    bot.send_message(chat_id, "📌 Muốn mang trí tuệ ZProject vào nhóm? Nhấn nút bên dưới nhé!", reply_markup=markup)