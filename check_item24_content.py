import sys
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('data-model="48EC480-050-8-NW"')
end = text.find('data-model="48EC480-050-8-NW50"', start)
content = text[start:end]

print(content[-500:])
