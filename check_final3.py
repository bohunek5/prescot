import re
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('<div class="product-accordion" data-model="48EC480-050-8-NW1">')
end = html.find('<div class="product-accordion" data-model="48EC480-050-8-NW">', start)
content = html[start:end]

lines = content.split('\n')
print(lines[30])
