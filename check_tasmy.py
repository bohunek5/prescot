import sys
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

tasmy_start = text.find('id="wapro-tasmy"')
tim_start = text.find('id="wapro-sterowniki"')
print("Tasmy start:", tasmy_start)
print("Sterowniki start:", tim_start)
if tim_start > tasmy_start:
    print(text[tim_start-500:tim_start])
