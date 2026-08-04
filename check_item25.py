import re
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('data-model="48EC480-050-8-NW50"')
end = text.find('data-model="48EC480-050-8-WW1"', start)
content = text[start:end]

div_op = content.count('<div')
div_cl = content.count('</div')
sec_op = content.count('<section')
sec_cl = content.count('</section')

print("NW50 -> div open:", div_op, "div close:", div_cl)
print("NW50 -> sec open:", sec_op, "sec close:", sec_cl)

