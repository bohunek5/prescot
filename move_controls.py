import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

mad_models = ['PR-MAD36-1224', 'PR-MAD60-1224', 'PR-MAD100-1224', 'PR-MAD150-1224', 'PR-MAD200-1224', 'PR-MAD300-1224']
tabs = ['wapro', 'tim', 'allegro', 'shoper']

def fix_order(text, model, tab):
    # Find the accordion for this model and tab
    # The accordion starts with: <div class="product-accordion" data-model="PR-MAD36-1224">
    # Wait, there is one accordion per tab? No, they are separated by tabs.
    # Let's find the controls block.
    # The controls block has: <button class="control-btn btn-edit" id="btn-edit-{tab}-{model}"
    
    # We want to extract the entire <div class="product-controls">...</div> that contains this id.
    # Then we remove it from its current position.
    # Then we find the closing </div> of <div class="edit-block" id="desc-edit-{tab}-{model}">...</textarea>\n</div>
    # and insert the controls right after it.
    
    # Match the controls block
    # Note: controls might contain inner tags, but we know it starts with <div class="product-controls"> and ends with </div>
    # We can match it specifically:
    controls_pattern = r'(<div class="product-controls">\s*<button class="control-btn btn-edit" id="btn-edit-' + tab + '-' + model + r'".*?<span class="control-status" id="status-' + tab + '-' + model + r'"></span>\s*</div>)'
    
    match = re.search(controls_pattern, text, re.DOTALL)
    if not match:
        return text
        
    controls_html = match.group(1)
    
    # Remove it
    text = text.replace(controls_html, '')
    
    # Find the edit-block for this tab and model
    # It looks like: <div class="edit-block" id="desc-edit-{tab}-{model}" ...> ... </div>
    # The end of the edit-block is the closing </div> after </textarea>
    edit_block_pattern = r'(<div class="edit-block" id="desc-edit-' + tab + '-' + model + r'".*?</textarea>\s*</div>)'
    
    match_edit = re.search(edit_block_pattern, text, re.DOTALL)
    if not match_edit:
        # If no edit block is found, maybe it's just a view block? Let's just append to model-block
        model_block_pattern = r'(<div class="model-block" id="desc-view-' + tab + '-' + model + r'".*?</section>\s*</div>)'
        match_model = re.search(model_block_pattern, text, re.DOTALL)
        if match_model:
            model_html = match_model.group(1)
            text = text.replace(model_html, model_html + '\n' + controls_html)
            return text
        else:
            # Cannot find where to place it, put it back
            print(f"Could not find edit block or model block for {tab}-{model}")
            return text
            
    edit_html = match_edit.group(1)
    
    # Insert controls AFTER edit-block
    # Because there might be extra spacing or \n, we replace edit_html with edit_html + \n + controls_html
    text = text.replace(edit_html, edit_html + '\n' + controls_html)
    
    # Let's clean up any double empty lines that might have been left behind when removing
    text = text.replace('<div class="product-body">\n\n', '<div class="product-body">\n')
    text = text.replace('<div class="product-body">\n\n<div class="model-block"', '<div class="product-body">\n<div class="model-block"')
    
    return text

for model in mad_models:
    for tab in tabs:
        content = fix_order(content, model, tab)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Moved product controls to the bottom.")
