import re
from bs4 import BeautifulSoup

with open('/Users/karolbohdanowicz/Downloads/opisy KAROL v2.html', 'r', encoding='utf-8') as f:
    ref_html = f.read()

ref_h3_map = {}
blocks = re.findall(r'<!-- START ([^\s]+) -->(.*?)<!-- KONIEC \1 -->', ref_html, re.DOTALL)
for sku, content in blocks:
    if sku.startswith('A0') or sku.startswith('C'):
        soup = BeautifulSoup(content, 'html.parser')
        sections = soup.find_all('section')
        if len(sections) > 1:
            h3 = sections[1].find('h3')
            if h3:
                ref_h3_map[sku] = h3.text.strip()

with open('index.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

count = 0
for view_div in soup.find_all('div', id=lambda x: x and ('desc-view-allegro-' in x or 'desc-view-tim-' in x or 'desc-view-wapro-' in x)):
    m = re.search(r'desc-view-(allegro|tim|wapro)-(.*)', view_div['id'])
    if not m: continue
    sku = m.group(2)
    if sku in ref_h3_map:
        sections = view_div.find_all('section', recursive=False)
        if len(sections) > 1:
            sec2 = sections[1]
            pill = sec2.find('span')
            # Check if there is NO h3
            if not sec2.find('h3'):
                new_h3 = soup.new_tag('h3', style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;")
                new_h3.string = ref_h3_map[sku]
                if pill:
                    pill.insert_after(new_h3)
                else:
                    sec2.insert(0, new_h3)
                count += 1

print(f"Restored H3 in block 2 for {count} profile instances.")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))
