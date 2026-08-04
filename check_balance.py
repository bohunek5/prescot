import re
import sys

with open('../tasmy-cob-48v-opisy.html', 'r', encoding='utf-8') as f:
    html = f.read()

pattern = r'<button class="copy-btn" onclick="copyHtml\(\'([^\']+)\'\)".*?>(.*?)</button>\s*<div id="\1">(.*?)</div>\s*(?=</section>|<div class="product-wrapper">|$)'
matches = list(re.finditer(pattern, html, flags=re.DOTALL))
if not matches:
    pattern = r'<div class="product-wrapper">.*?<button class="copy-btn" onclick="copyHtml\(\'([^\']+)\'\)".*?</button>\s*<div id="\1">(.*?)</div>\s*</div>'
    matches = list(re.finditer(pattern, html, flags=re.DOTALL))

for match in matches:
    model = match.group(1)
    raw_html = match.group(2) if len(match.groups()) == 2 else match.group(3)
    
    div_open = raw_html.count('<div')
    div_close = raw_html.count('</div')
    
    section_open = raw_html.count('<section')
    section_close = raw_html.count('</section')
    
    print(f"Model {model}: div open={div_open}, div close={div_close} | section open={section_open}, section close={section_close}")

