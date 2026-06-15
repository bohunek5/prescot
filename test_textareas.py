import re

INDEX_HTML = "/Users/karolbohdanowicz/my-ai-agents/prescot/test_index.html"

with open(INDEX_HTML, 'r', encoding='utf-8') as f:
    html_content = f.read()

# For each textarea, we want to replace its content with the content of its corresponding desc-view div.
# We can find all SKUs.
textarea_pattern = re.compile(r'<textarea class="edit-textarea" id="textarea-([a-z]+)-([a-zA-Z0-9_-]+)"[^>]*>')

# We will just do a simple pass
def replace_textarea_contents(html_str):
    matches = list(textarea_pattern.finditer(html_str))
    
    # Process from the end so indices don't shift
    for m in reversed(matches):
        tab = m.group(1)
        sku = m.group(2)
        textarea_tag = m.group(0)
        start_idx = m.end()
        end_idx = html_str.find('</textarea>', start_idx)
        
        # Find the corresponding model-block content
        id_str = f'desc-view-{tab}-{sku}'
        model_start_marker = f'<div class="model-block" id="{id_str}">'
        model_start_idx = html_str.find(model_start_marker)
        
        if model_start_idx != -1 and end_idx != -1:
            # We assume the model block ends right before the next edit-block
            # or we can just extract from the updated master_dict if we had it,
            # but we can just grab what is in the HTML.
            next_div_idx = html_str.find('</div>', model_start_idx)
            # Actually, the model block has inner divs. 
            # It's safer to find the next edit block.
            end_model_marker = f'<div class="edit-block" id="desc-edit-{tab}-{sku}"'
            end_model_idx = html_str.find(end_model_marker, model_start_idx)
            if end_model_idx != -1:
                # The model content is everything between model_start_marker and the last </div> before edit_block.
                model_content_with_div = html_str[model_start_idx + len(model_start_marker):end_model_idx]
                model_content = model_content_with_div.rsplit('</div>', 1)[0].strip()
                
                # Replace textarea content
                html_str = html_str[:start_idx] + '\n' + model_content + '\n' + html_str[end_idx:]
    return html_str

new_html = replace_textarea_contents(html_content)

with open(INDEX_HTML, 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Updated textareas to match view blocks.")
