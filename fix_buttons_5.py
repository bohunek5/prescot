import re
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Usunmy w ogole te stare niepotrzebne przyciski z produktow.
html = re.sub(r'--\s*<div style="font-family: inherit; display: grid; grid-template-columns: repeat\(auto-fit, minmax\(220px, 1fr\)\).*?</a></div></div>', '', html, flags=re.DOTALL)
html = html.replace('<!-- 48EC480-050-8-NW1 -->\n', '')
html = html.replace('\n\n\n\n\n\n\n\n\n\n', '\n')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
