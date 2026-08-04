import re
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

start2 = text.find('id="wapro-zlaczki"')
sub2 = text[start2:start2+100000]
print(sub2[:1000])
