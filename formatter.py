import re

def format_html(text):
    blocks = re.findall(r"```(.*?)```", text, flags=re.DOTALL)
    for block in blocks:
        # Escape HTML nguy hiểm trong code block
        safe = block.strip().replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
        html_block = f"<pre>{safe}</pre>"
        text = text.replace(f"```{block}```", html_block)

    return text  # Giữ nguyên \n để Telegram tự xuống dòng