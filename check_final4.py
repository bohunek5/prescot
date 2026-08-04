import re
import sys

with open('../tasmy-cob-48v-opisy.html', 'r', encoding='utf-8') as f:
    html = f.read()

pattern = r'<button class="copy-btn" onclick="copyHtml\(\'48EC480-050-8-NW1\'\)".*?>(.*?)</button>\s*<div id="48EC480-050-8-NW1">(.*?)</div>\s*(?=</section>|<div class="product-wrapper">|$)'
matches = list(re.finditer(pattern, html, flags=re.DOTALL))
raw = matches[0].group(2)
lines = raw.split('\n')
for i, line in enumerate(lines):
    op = line.count('<div')
    cl = line.count('</div')
    if op or cl:
        print(f"{i+1:3d}: +{op} -{cl} | {line.strip()[:60]}")

