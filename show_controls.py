import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('id="desc-view-tim-PR-MAD36-1224"')
controls_start = content.rfind('<div class="product-controls">', 0, idx)
print(content[controls_start:idx])
