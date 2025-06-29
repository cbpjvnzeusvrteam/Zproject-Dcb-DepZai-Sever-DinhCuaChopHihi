import re

def format_html(text):
    blocks = re.findall(r"```(.*?)```", text, flags=re.DOTALL)
    for block in blocks:
        html_block = f'''
<div style="background:#f5f5f5;border:1px solid #ccc;padding:10px;border-radius:5px;position:relative;">
<pre><code>{block.strip()}</code></pre>
<button onclick="navigator.clipboard.writeText(`{block.strip()}`)" style="position:absolute;top:5px;right:5px;">📋 Copy</button>
</div>
'''
        text = text.replace(f"```{block}```", html_block)
    text = text.replace("\n", "<br>")
    return text