import re

index_path = '/Users/karolbohdanowicz/my-ai-agents/prescot/index.html'

files_and_regex = [
    ('/Users/karolbohdanowicz/Downloads/PROFILE.html', r'<!-- START ([\w-]+) -->(.*?)<!-- KONIEC \1 -->'),
    ('/Users/karolbohdanowicz/Downloads/STEROWIKI_I_ZLACZKI.html', r'<!-- START ([\w-]+) -->(.*?)<!-- KONIEC \1 -->')
]

descriptions = {}

# 1. Parse PROFILE and STEROWIKI_I_ZLACZKI
for file_path, pattern in files_and_regex:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    matches = re.findall(pattern, content, re.DOTALL)
    for sku, html in matches:
        descriptions[sku] = html.strip()
    print(f"Extracted {len(matches)} descriptions from {file_path}")

# 2. Parse ZASILACZE
zasilacze_path = '/Users/karolbohdanowicz/Downloads/ZASILACZE.html'
with open(zasilacze_path, 'r', encoding='utf-8') as f:
    content = f.read()
matches = re.findall(r'<div class="model-header">MODEL: ([\w-]+)</div>.*?<div class="model-block">(.*?)</div>\s*(?:<div class="model-header"|<hr|<body)', content, re.DOTALL)
for sku, html in matches:
    descriptions[sku] = html.strip()
print(f"Extracted {len(matches)} descriptions from {zasilacze_path}")

print(f"Total extracted descriptions: {len(descriptions)}")

# 3. Update index.html
with open(index_path, 'r', encoding='utf-8') as f:
    index_content = f.read()

updated_count = 0

for sku, html in descriptions.items():
    # Update desc-view blocks for all tabs (wapro, tim, allegro)
    for tab in ['wapro', 'tim', 'allegro']:
        # 1. Update the view block: <div class="model-block" id="desc-view-{tab}-{sku}">...</div>
        view_pattern = rf'(<div class="model-block" id="desc-view-{tab}-{sku}">)(.*?)(</div>\s*<div class="edit-block" id="desc-edit-{tab}-{sku}")'
        
        def replacer_view(match):
            return match.group(1) + "\n" + html + "\n" + match.group(3)
            
        index_content, count1 = re.subn(view_pattern, replacer_view, index_content, flags=re.DOTALL)
        
        # 2. Update the textarea content: <textarea class="edit-textarea" id="textarea-{tab}-{sku}"...>...</textarea>
        textarea_pattern = rf'(<textarea class="edit-textarea" id="textarea-{tab}-{sku}"[^>]*>)(.*?)(</textarea>)'
        
        def replacer_textarea(match):
            return match.group(1) + "\n" + html + "\n" + match.group(3)
            
        index_content, count2 = re.subn(textarea_pattern, replacer_textarea, index_content, flags=re.DOTALL)
        
        if count1 > 0 or count2 > 0:
            updated_count += 1

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(index_content)

print(f"Updated {updated_count} elements in {index_path}")
