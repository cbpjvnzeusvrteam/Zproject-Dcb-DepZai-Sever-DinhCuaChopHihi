from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def handle_start(bot, message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📢 Kênh thông báo", url="https://t.me/zproject3"),
        InlineKeyboardButton("💬 Nhóm chat ZProject", url="https://t.me/zproject4"),
        InlineKeyboardButton("👤 Liên hệ Admin", url="https://t.me/zproject2")
    )

    welcome = "🤖 Xin chào bạn đến với <b>ZProject Bot</b>!\n\n"
    welcome += "Hãy chọn liên kết bên dưới để kết nối cùng cộng đồng ZProject nhen ✨"

    bot.send_message(message.chat.id, welcome, reply_markup=markup, parse_mode="HTML")