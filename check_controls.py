import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('id="btn-edit-wapro-PR-MAD36-1224"')
print(content[idx-200:idx+300])

