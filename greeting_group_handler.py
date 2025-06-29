from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def handle_bot_added(bot, message):
    if message.new_chat_members:
        for member in message.new_chat_members:
            if member.id == bot.get_me().id:
                markup = InlineKeyboardMarkup()
                markup.add(
                    InlineKeyboardButton("📢 Kênh Thông Báo", url="https://t.me/zproject3"),
                    InlineKeyboardButton("💬 Kênh Chat", url="https://t.me/zproject4")
                )

                greeting = (
                    "<b>🖖 Xin Chào Mọi Người!</b>\n\n"
                    "<i>Tôi là ZProject và WormGpt V3</i>, được phát triển bởi <b>Zproject X Duong Cong Bang</b>.\n"
                    "Telegram của nhà phát triển tôi: <a href='https://t.me/zproject2'>@duongcongbang.dev</a>\n\n"
                    "<blockquote>Hãy tham gia ngay cộng đồng ZProject để cập nhật thông tin mới nhất!</blockquote>\n\n"
                    "👉 Bạn có thể nhấn 2 nút bên dưới để theo dõi kênh & trò chuyện cùng chúng tôi 💖"
                )

                bot.send_message(
                    message.chat.id,
                    greeting,
                    parse_mode="HTML",
                    reply_markup=markup
                )