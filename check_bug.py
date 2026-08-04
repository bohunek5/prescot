import re
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's find all product-accordion in wapro-tasmy
start = text.find('id="wapro-tasmy"')
end = text.find('id="wapro-sterowniki"')
content = text[start:end]

matches = re.findall(r'<span class="product-model">([^<]+)</span>', content)
for i, m in enumerate(matches[-15:]): # Last 15
    print(i, m)
