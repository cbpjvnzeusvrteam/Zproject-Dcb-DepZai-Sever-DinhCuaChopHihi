from ask_handler import handle_ask
from types import SimpleNamespace

def handle_retry_button(bot, call):
    _, uid, question = call.data.split("|", 2)
    if str(call.from_user.id) != uid:
        return bot.answer_callback_query(call.id, "🚫 Không phải câu hỏi của bạn nha!")

    msg = SimpleNamespace()
    msg.chat = call.message.chat
    msg.message_id = call.message.message_id
    msg.text = "/ask " + question
    msg.from_user = call.from_user
    msg.reply_to_message = None

    bot.answer_callback_query(call.id, "🔁 Đang trả lời lại...")
    handle_ask(bot, msg)