import re

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix FC10-SMD-RGBW-TP "12mm" mistake.
# Only replace within the block for FC10-SMD-RGBW-TP to avoid breaking anything else.
start_tag = '<div class="product-accordion" data-model="FC10-SMD-RGBW-TP">'
start_idx = 0
while True:
    start_idx = content.find(start_tag, start_idx)
    if start_idx == -1: break
    
    # find end of block
    div_count = 0
    i = start_idx
    while i < len(content):
        if content[i:i+4] == '<div':
            div_count += 1
            i += 4
        elif content[i:i+6] == '</div>':
            div_count -= 1
            i += 6
            if div_count == 0: break
        else:
            i += 1
    
    end_idx = i
    block = content[start_idx:end_idx]
    
    # Fix the badge
    block = block.replace('Złączka bezlutowa 12mm RGBW', 'Złączka bezlutowa 10mm RGBW')
    # Fix the specifications
    block = block.replace('Szerokość 12mm', 'Szerokość 10mm')
    block = block.replace('szerokości laminatu 12mm', 'szerokości laminatu 10mm')
    # Fix the spec table
    block = block.replace('<span style="font-size: 15px; font-weight: 600; color: inherit;">12mm</span>', '<span style="font-size: 15px; font-weight: 600; color: inherit;">10mm</span>')
    
    # Also fix Kompatybilność for RGBW
    block = block.replace('2-pin MONO', '5-pin RGBW')
    # Also fix TPT if it says Trójnik
    block = block.replace('Trójnik (T)', 'Prosta z przewodem')
    
    content = content[:start_idx] + block + content[end_idx:]
    start_idx += len(block)

# 2. Fix the Kompatybilność and Kształt for the RGB models
rgb_models = ['FC10-COB-RGB-TP', 'FC10-SMD-RGB-TP', 'FC10-SMD-RGB-TPT', 'FC10-COB-RGB-TPT']
for sku in rgb_models:
    s_tag = f'<div class="product-accordion" data-model="{sku}">'
    s_idx = 0
    while True:
        s_idx = content.find(s_tag, s_idx)
        if s_idx == -1: break
        
        div_count = 0
        i = s_idx
        while i < len(content):
            if content[i:i+4] == '<div':
                div_count += 1
                i += 4
            elif content[i:i+6] == '</div>':
                div_count -= 1
                i += 6
                if div_count == 0: break
            else:
                i += 1
        
        e_idx = i
        block = content[s_idx:e_idx]
        
        # Fix Kompatybilność for RGB
        block = block.replace('2-pin MONO', '4-pin RGB')
        # Fix Kształt if it says Trójnik but it is TP or TPT
        block = block.replace('Trójnik (T)', 'Prosta z przewodem')
        
        content = content[:s_idx] + block + content[e_idx:]
        s_idx += len(block)

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done fixing specs and 10mm widths!")
