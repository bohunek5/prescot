import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('data-model="PR-MAD36-1224"')
end = content.find('data-model="PR-MAD60-1224"')
section = content[start:end]

print("Wapro controls:", section.find('id="btn-edit-wapro-PR-MAD36-1224"'))
print("Tim controls:", section.find('id="btn-edit-tim-PR-MAD36-1224"'))
print("Allegro controls:", section.find('id="btn-edit-allegro-PR-MAD36-1224"'))
print("Shoper controls:", section.find('id="btn-edit-shoper-PR-MAD36-1224"'))

# Let's see where Tim controls are:
if section.find('id="btn-edit-tim-PR-MAD36-1224"') != -1:
    idx = section.find('id="btn-edit-tim-PR-MAD36-1224"')
    print(section[idx-100:idx+200])

