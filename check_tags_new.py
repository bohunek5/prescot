import re
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

models = [
    '48EC480-050-8-NW1',
    '48EC480-050-8-NW',
    '48EC480-050-8-NW50',
    '48EC480-050-8-WW1',
    '48EC480-050-8-WW',
    '48EC480-050-8-WW50'
]

for model in models:
    start = text.find(f'data-model="{model}"')
    if start == -1:
        print("Missing:", model)
        continue
    # Find next accordion
    end = text.find('data-model="', start + 50)
    if end == -1: end = len(text)
    
    content = text[start:end]
    div_op = content.count('<div')
    div_cl = content.count('</div')
    sec_op = content.count('<section')
    sec_cl = content.count('</section')
    
    print(f"{model} -> div op: {div_op}, cl: {div_cl} | sec op: {sec_op}, cl: {sec_cl}")
