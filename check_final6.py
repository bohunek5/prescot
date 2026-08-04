import sys
with open('../rozdzielacze-opisy.html', 'r', encoding='utf-8') as f:
    html = f.read()
parts = html.split('<!-- HPD-')
for part in parts[1:]:
    model = 'HPD-' + part.split('-->')[0].strip()
    raw = part.split('-->', 1)[1].strip()
    div_open = raw.count('<div')
    div_close = raw.count('</div')
    sec_open = raw.count('<section')
    sec_close = raw.count('</section')
    print(f"Model {model}: div open={div_open}, div close={div_close} | section open={sec_open}, section close={sec_close}")
