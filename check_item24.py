import re
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('data-model="48EC480-050-8-NW"')
# To avoid NW1, NW50 we need to match exactly
# Wait, let's just find the exact block
block_start = text.find('<div class="product-accordion" data-model="48EC480-050-8-NW">')
block_end = text.find('<div class="product-accordion" data-model="48EC480-050-8-NW50">', block_start)
content = text[block_start:block_end]

div_op = content.count('<div')
div_cl = content.count('</div')
sec_op = content.count('<section')
sec_cl = content.count('</section')

print("NW -> div open:", div_op, "div close:", div_cl)
print("NW -> sec open:", sec_op, "sec close:", sec_cl)
