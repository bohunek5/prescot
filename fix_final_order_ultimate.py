import sys
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's fix the newly injected ones
# The new ones have:
# <div class="product-body">
# <div class="product-controls"> ... </div>
# <div class="model-block"> ... </div>
# <textarea> ... </textarea>
# </div>
# </div> (closes accordion)

# We want:
# <div class="product-body">
# <div class="model-block"> ... </div>
# <textarea> ... </textarea>
# </div>
# <div class="product-controls"> ... </div>
# </div> (closes accordion)

parts = text.split('<div class="product-accordion" data-model="')
out_html = parts[0]

for p in parts[1:]:
    model = p.split('">')[0]
    if '48EC480' in model or 'HPD-' in model:
        # It's one of ours
        # Extract product-controls
        ctrl_start = p.find('<div class="product-controls">')
        if ctrl_start != -1:
            ctrl_end = p.find('</div>', p.find('<span class="control-status"', ctrl_start)) + 6
            ctrl_html = p[ctrl_start:ctrl_end]
            
            # Remove it from its current place
            p = p[:ctrl_start] + p[ctrl_end:]
            
            # Now p ends with:
            # </textarea>
            # </div>
            # </div>\n
            
            # We want to put ctrl_html AFTER the </div> that closes product-body.
            # In our injected HTML, product-body contains model-block and textarea.
            # So after </textarea>, there is \n</div>\n
            textarea_end = p.find('</textarea>') + len('</textarea>')
            body_close = p.find('</div>', textarea_end)
            
            p = p[:body_close+6] + '\n' + ctrl_html + p[body_close+6:]
            
    out_html += '<div class="product-accordion" data-model="' + p

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(out_html)

print("Fixed controls placement.")

