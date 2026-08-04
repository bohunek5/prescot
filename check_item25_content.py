import re
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('data-model="48EC480-050-8-NW50"')
end = text.find('data-model="48EC480-050-8-WW1"', start)
content = text[start:end]

print(content)
