import sys

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('<div class="product-accordion" data-model="Z05-096-0-NW">')
end = html.find('<div class="product-accordion"', start + 10)
print(html[start:end])
