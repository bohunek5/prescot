import re
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()
    
# Chcemy sprawdzic czy na koncu nowo dodanych elementow sa guziki (controls-bar)
idx = html.find('<div class="product-accordion" data-model="48EC480-050-8-NW1">')
end = html.find('</div>\n</div>\n</div>', idx)
print(html[end-300:end+50])
