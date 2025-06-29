import re

def format_html(text):
    blocks = re.findall(r"```(.*?)```", text, flags=re.DOTALL)
    for block in blocks:
        safe = block.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html_block = f"<pre>{safe}</pre>"
        text = text.replace(f"```{block}```", html_block)
    return text  # Giữ nguyên \n, Telegram sẽ tự xuống dòng