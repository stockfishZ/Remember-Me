import urllib.request
import base64
import os
import re

css_url = 'https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap'
out_dir = r'D:\Project\RememberMe\brag-output-v4\work'
ttf_path = os.path.join(out_dir, 'PressStart2P.woff2')
js_path = os.path.join(out_dir, 'font_base64.js')

try:
    req = urllib.request.Request(css_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode('utf-8')
    print('CSS fetched:', content[:150])
    match = re.search(r'url\((https://[^)]+)\)', content)
    if match:
        font_url = match.group(1)
        print('Downloading font from:', font_url)
        with urllib.request.urlopen(font_url, timeout=10) as f_resp:
            font_data = f_resp.read()
        with open(ttf_path, 'wb') as f:
            f.write(font_data)
        b64 = base64.b64encode(font_data).decode('ascii')
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(f'const FONT_PRESS_START_2P_BASE64 = "{b64}";\n')
        print(f"Saved {len(font_data)} bytes to {ttf_path} and {js_path}")
    else:
        print("No font url found in CSS")
except Exception as e:
    print("Download error:", e)
