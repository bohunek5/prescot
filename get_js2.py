with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('function switchMainTab')
print(content[idx:idx+800])
