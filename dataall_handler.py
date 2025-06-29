import os
import json
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

ADMIN_ID = 5819094246
GROUP_FILE = "groups.json"

def handle_dataall(bot, message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "⛔ Bạn không có quyền dùng lệnh này.")

    users = [f for f in os.listdir() if f.startswith("memory_") and f.endswith(".json")]
    total_users = len(users)

    groups = []
    if os.path.exists(GROUP_FILE):
        with open(GROUP_FILE, "r") as f:
            groups = json.load(f)
    total_groups = len(groups)

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    today_ask = 0
    yesterday_ask = 0
    for user_file in users:
        with open(user_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                created = item.get("created", None)
                if not created:
                    continue
                date = datetime.strptime(created, "%Y-%m-%d").date()
                if date == today:
                    today_ask += 1
                elif date == yesterday:
                    yesterday_ask += 1

    diff = today_ask - yesterday_ask
    trend = "🔺 Tăng" if diff > 0 else ("🔻 Giảm" if diff < 0 else "⏸️ Không đổi")

    # Nội dung HTML
    stat_html = f"""
<b>📊 Thống kê hoạt động ZProject Bot - Zproject X Dương Công Bằng</b><br><br>
👤 Tổng người dùng: <b>{total_users}</b><br>
👥 Nhóm đã tham gia: <b>{total_groups}</b><br>
✍️ Lượt dùng Bot hôm nay: <b>{today_ask}</b><br>
📆 So với hôm qua: <b>{diff:+d}</b> → {trend}<br>
🗓 Ngày: <i>{today.strftime('%d/%m/%Y')}</i>
"""

    # Gửi kèm nút export
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📄 Xuất file thống kê", callback_data="export_stats"))
    bot.send_message(message.chat.id, stat_html, parse_mode="HTML", reply_markup=markup)