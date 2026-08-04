import re

# EAN mapping for the new SKUs
ean_map = {
    'FC10-COB-RGB-TP': '5905475363559',
    'FC10-COB-RGB-TPT': '5905475363566',
    'FC10-SMD-RGB-TP': '5905475363689',
    'FC10-SMD-RGB-TPT': '5905475363696',
    'FC10-SMD-RGBW-TP': '5905475363702'
}

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

def update_ean_in_block(block, old_eans, new_ean):
    for old_ean in old_eans:
        block = block.replace(old_ean, new_ean)
    return block

# The old EANs that were cloned
old_eans_to_replace = ['5905475363634', '5905475363641']

# We need to find the specific block for each SKU and replace its EANs.
for sku, new_ean in ean_map.items():
    # Find all start occurrences of the accordion for this SKU
    start_tag = f'<div class="product-accordion" data-model="{sku}">'
    
    start_idx = 0
    while True:
        start_idx = content.find(start_tag, start_idx)
        if start_idx == -1:
            break
            
        # Find the end of this accordion using a simple div counter
        div_count = 0
        i = start_idx
        while i < len(content):
            if content[i:i+4] == '<div':
                div_count += 1
                i += 4
            elif content[i:i+6] == '</div>':
                div_count -= 1
                i += 6
                if div_count == 0:
                    break
            else:
                i += 1
                
        end_idx = i
        block = content[start_idx:end_idx]
        
        # Replace the EANs
        new_block = update_ean_in_block(block, old_eans_to_replace, new_ean)
        
        # Re-insert the block
        content = content[:start_idx] + new_block + content[end_idx:]
        
        # Advance the index by the new block's length
        start_idx += len(new_block)

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done updating EANs!")
