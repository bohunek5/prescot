import sys
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('data-model="24E009-050-8-WW27100"')
end = text.find('<div class="product-accordion"', start + 10)
if end == -1: end = len(text)
content = text[start:end]

body_start = content.find('<div class="product-body">')
body_end = content.rfind('</div>', 0, content.rfind('</div>'))
controls_start = content.find('<div class="product-controls">')

print("Body start:", body_start)
print("Controls start:", controls_start)
print("Body ends somewhere after controls?" , controls_start > body_start)
print("Does controls end before body ends?", content.find('</div>', controls_start) < body_end)

