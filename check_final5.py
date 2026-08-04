import sys
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()
import re
print("HPD items in index.html:")
print(re.findall(r'data-model="(HPD-[^"]+)"', html)[:5])

with open('../rozdzielacze-opisy.html', 'r', encoding='utf-8') as f:
    html_rozd = f.read()
print("HPD items in rozdzielacze-opisy.html:")
parts = html_rozd.split('<!-- HPD-')
for part in parts[1:6]:
    print('HPD-' + part.split('-->')[0].strip())
