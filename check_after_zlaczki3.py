import sys
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

zlaczki_start = text.find('id="wapro-zlaczki"')
tim_start = text.find('id="panel-tim"')

print("Zlaczki start:", zlaczki_start)
print("Tim start:", tim_start)
if tim_start > zlaczki_start:
    print(text[tim_start-500:tim_start])
