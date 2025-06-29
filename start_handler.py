from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import send_add_bot_button

def handle_start(bot, message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📢 Kênh thông báo", url="https://t.me/zproject3"),
        InlineKeyboardButton("💬 Nhóm chat", url="https://t.me/zproject4"),
        InlineKeyboardButton("👤 Liên hệ Admin", url="https://t.me/zproject2")
    )

    welcome = (
        "<b>🤖 Xin chào bạn đến với ZProject Bot!</b>\n\n"
        "Tôi là trợ lý AI được phát triển bởi <b>Zproject</b> kết hợp cùng <i>Duong Cong Bang</i>.\n\n"
        "Hãy tham gia cộng đồng ZProject để nhận cập nhật mới nhất và thảo luận cùng mọi người nhé!\n\n"
        "<i>👇 Hãy chọn một trong các nút bên dưới để bắt đầu kết nối:</i>"
    )

    bot.send_message(message.chat.id, welcome, reply_markup=markup, parse_mode="HTML")

    # ➕ Gửi thêm nút mời bot vào nhóm
    send_add_bot_button(bot, message.chat.id, bot.get_me().username)