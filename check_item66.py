import sys
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()
    
# revert to the original commit 7bedda0 so we can see the pure unmodified index.html
import subprocess
subprocess.run(['git', 'checkout', '7bedda0', 'index.html'])

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('data-model="24E009-050-8-WW27100"')
end = text.find('</div>', start)
content = text[start:start+2000]
print(content)
