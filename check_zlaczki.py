import re
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('id="wapro-zlaczki"')
end = text.find('id="wapro-', start + 20)
if end == -1:
    end = text.find('id="panel-', start)
if end == -1:
    end = len(text)
content = text[start:end]

matches = re.findall(r'<span class="product-model">([^<]+)</span>', content)
print("Items in zlaczki:", len(matches))
if matches:
    print("Last item:", matches[-1])
else:
    print("No items found.")
