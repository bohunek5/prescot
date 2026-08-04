import sys
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('<div class="product-accordion" data-model="48EC480-050-8-NW1">')
end = html.find('<div class="product-accordion" data-model="48EC480-050-8-NW">', start)
content = html[start:end]
print("48V 1 DIV OPEN:", content.count('<div'), "CLOSE:", content.count('</div'))

start = html.find('<div class="product-accordion" data-model="HPD-MONO-19">')
end = html.find('<div class="product-accordion" data-model="HPD-MONO-14">', start)
content = html[start:end]
print("ROZDZ 1 DIV OPEN:", content.count('<div'), "CLOSE:", content.count('</div'))
