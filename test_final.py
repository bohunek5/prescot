import re
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('id="wapro-tasmy"')
end = text.find('id="wapro-sterowniki"')
content = text[start:end]

matches = re.findall(r'<span class="product-model">([^<]+)</span>', content)
for i, m in enumerate(matches[-10:]):
    print(i, m)

print("---")
start2 = text.find('id="wapro-zlaczki"')
sub2 = text[start2:start2+100000]
end2 = sub2.find('id="panel-tim"')
if end2 == -1: end2 = len(sub2)
content2 = sub2[:end2]

matches2 = re.findall(r'<span class="product-model">([^<]+)</span>', content2)
for i, m in enumerate(matches2[-10:]):
    print(i, m)
