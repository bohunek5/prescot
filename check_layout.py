with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find PR-MONO-12A in wapro
idx = content.find('data-model="PR-MONO-12A"')
print(content[idx:idx+1500])
