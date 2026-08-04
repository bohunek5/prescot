import sys
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('id="wapro-zlaczki"')
sub = text[start:start+100000] # big chunk
end = sub.find('<!-- ==================== TIM TAB PANEL')
if end != -1:
    print(sub[end-500:end])
else:
    print("Could not find TIM tab panel")
