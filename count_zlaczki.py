import re
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('id="wapro-zlaczki"')
end = text.find('id="panel-tim"')
content = text[start:end]

matches = re.findall(r'<span class="product-model">([^<]+)</span>', content)
print("Items in zlaczki:", len(matches))
for m in matches:
    print(m)
