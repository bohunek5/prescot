import re
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('id="wapro-tasmy"')
end = text.find('id="wapro-sterowniki"')
content = text[start:end]

matches = re.findall(r'<span class="product-model">([^<]+)</span>', content)
print("Items in tasmy:", len(matches))
for m in matches[-10:]:
    print(m)
