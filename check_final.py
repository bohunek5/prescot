import re
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Zbadajmy konkretny element
start = html.find('<div class="product-accordion" data-model="48EC480-050-8-NW1">')
end = html.find('<div class="product-accordion" data-model="48EC480-050-8-NW">', start)
content = html[start:end]
print("DIV OPEN:", content.count('<div'), "DIV CLOSE:", content.count('</div'))
print("SEC OPEN:", content.count('<section'), "SEC CLOSE:", content.count('</section'))
print("---")
# Pokażmy koncowkę
print(content[-300:])
