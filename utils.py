import time

def auto_group_greeting(bot, GROUPS):
    while True:
        time.sleep(1800)
        for group_id in GROUPS:
            try:
                bot.send_message(group_id, "👋 Chào cả nhà! Đừng quên dùng /ask để hỏi AI Zproject nha!")
            except:
                pass