import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('data-model="PR-MAD36-1224"')
end = content.find('data-model="PR-MAD60-1224"')

print(content[start:start+2000])

