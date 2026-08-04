import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('id="desc-view-tim-PR-MAD36-1224"')
print(content[idx-100:idx+100])
