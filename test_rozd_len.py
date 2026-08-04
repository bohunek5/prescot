import re
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

start2 = text.find('id="wapro-zlaczki"')
sub2 = text[start2:start2+100000]
end2 = sub2.find('id="panel-tim"')
if end2 == -1: end2 = len(sub2)
content2 = sub2[:end2]

matches2 = re.findall(r'<span class="product-model">([^<]+)</span>', content2)
print("Items:", len(matches2))
print("Last item:", matches2[-1])
