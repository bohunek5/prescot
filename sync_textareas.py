import html
with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

skus = ["FC10-COB-RGB-TP", "FC10-SMD-RGB-TP", "FC10-SMD-RGB-TPT", "FC10-COB-RGB-TPT", "FC10-SMD-RGBW-TP"]
platforms = ["wapro", "tim", "allegro"]

for sku in skus:
    for plat in platforms:
        # Extract HTML from desc-view
        view_id = f'desc-view-{plat}-{sku}'
        view_start = content.find(f'<div class="model-block" id="{view_id}">')
        if view_start != -1:
            view_content_start = view_start + len(f'<div class="model-block" id="{view_id}">')
            i = view_content_start
            div_count = 1
            while i < len(content):
                if content[i:i+4] == '<div':
                    div_count += 1
                    i += 4
                elif content[i:i+6] == '</div>':
                    div_count -= 1
                    if div_count == 0:
                        break
                    i += 6
                else:
                    i += 1
            view_html = content[view_content_start:i].strip()
            
            # Escape for textarea
            escaped_html = html.escape(view_html)
            
            # Find and replace textarea content
            ta_id = f'textarea-{plat}-{sku}'
            ta_start_tag = f'<textarea class="edit-textarea" id="{ta_id}" oninput="onDescriptionInput(\'{plat}\', \'zlaczki\', \'{sku}\')">'
            ta_start = content.find(ta_start_tag)
            if ta_start != -1:
                ta_content_start = ta_start + len(ta_start_tag)
                ta_end = content.find('</textarea>', ta_content_start)
                if ta_end != -1:
                    content = content[:ta_content_start] + escaped_html + content[ta_end:]

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Textareas synced!")
