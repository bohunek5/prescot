import sys
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('id="wapro-zlaczki"')
sub = text[start:start+100000]
end = sub.find('id="panel-tim"')
if end != -1:
    print(sub[end-500:end])
else:
    print("Could not find panel-tim")
