import sys

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('<div class="product-accordion" data-model="24D002-050-8-WW27">')
end = html.find('<div class="product-accordion"', start + 10)
print(html[start:end])
