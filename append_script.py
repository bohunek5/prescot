import re
import html

# The structure we need to build for each item:
# <div class="product-accordion" data-model="{model}">
# <button class="product-trigger" onclick="toggleProduct(this)">
# <div class="product-info">
# <span class="product-model">{index}. {model}</span>
# <span class="product-label-badge">{badge_text}</span>
# </div>
# <span class="product-arrow">▼</span>
# </button>
# <div class="product-body">
# <div class="model-block" id="desc-view-wapro-{model}">
# {content}
# </div>
# <div class="edit-block" id="desc-edit-wapro-{model}" style="display: none;">
# <textarea class="edit-textarea" id="textarea-wapro-{model}" oninput="onDescriptionInput('wapro', 'tasmy', '{model}')">{encoded_content}</textarea>
# </div>
# <div class="controls-bar" id="controls-wapro-{model}">
# <button class="control-btn btn-edit" id="btn-edit-wapro-{model}" onclick="toggleEdit('wapro', 'tasmy', '{model}')">Edytuj opis</button>
# <button class="control-btn btn-save" id="btn-save-wapro-{model}" onclick="saveDescription('wapro', 'tasmy', '{model}')" style="display: none;">Zapisz opis</button>
# <button class="control-btn btn-copy" onclick="copyDescriptionHtml('wapro', '{model}', this)" style="border-color: #f59e0b; color: #f59e0b;" title="Kopiuj opis HTML">Kopiuj opis HTML</button>
# <button class="control-btn btn-ean" onclick="navigator.clipboard.writeText('BRAK'); this.innerText='Skopiowano!'; setTimeout(()=>this.innerText='EAN: BRAK', 2000);" style="border-color: #0ea5e9; color: #0ea5e9;" title="Skopiuj EAN">EAN: BRAK</button>
# <span class="control-status" id="status-wapro-{model}"></span>
# </div>
# </div>
# </div>

def generate_accordion(model, content, index, badge_text="WAPRO"):
    encoded_content = html.escape(content.strip())
    # replace quotes if needed, though html.escape handles it for textarea
    return f'''
<div class="product-accordion" data-model="{model}">
<button class="product-trigger" onclick="toggleProduct(this)">
<div class="product-info">
<span class="product-model">{index}. {model}</span>
<span class="product-label-badge">{badge_text}</span>
</div>
<span class="product-arrow">▼</span>
</button>
<div class="product-body">
<div class="model-block" id="desc-view-wapro-{model}">
{content.strip()}
</div>
<div class="edit-block" id="desc-edit-wapro-{model}" style="display: none;">
<textarea class="edit-textarea" id="textarea-wapro-{model}" oninput="onDescriptionInput('wapro', 'tasmy', '{model}')">{encoded_content}</textarea>
</div>
<div class="controls-bar" id="controls-wapro-{model}">
<button class="control-btn btn-edit" id="btn-edit-wapro-{model}" onclick="toggleEdit('wapro', 'tasmy', '{model}')">Edytuj opis</button>
<button class="control-btn btn-save" id="btn-save-wapro-{model}" onclick="saveDescription('wapro', 'tasmy', '{model}')" style="display: none;">Zapisz opis</button>
<button class="control-btn btn-copy" onclick="copyDescriptionHtml('wapro', '{model}', this)" style="border-color: #f59e0b; color: #f59e0b;" title="Kopiuj opis HTML">Kopiuj opis HTML</button>
<button class="control-btn btn-ean" onclick="navigator.clipboard.writeText('BRAK'); this.innerText='Skopiowano!'; setTimeout(()=>this.innerText='EAN: BRAK', 2000);" style="border-color: #0ea5e9; color: #0ea5e9;" title="Skopiuj EAN">EAN: BRAK</button>
<span class="control-status" id="status-wapro-{model}"></span>
</div>
</div>
</div>
'''

import sys
input_files = ['/Users/karolbohdanowicz/my-ai-agents/tasmy-cob-48v-opisy.html', '/Users/karolbohdanowicz/my-ai-agents/rozdzielacze-opisy.html']
output_html = ""
current_idx = 100

for fpath in input_files:
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            raw_data = f.read()
    except Exception as e:
        print(f"Error reading {fpath}: {e}")
        continue
    
    # split by <!-- model -->
    blocks = raw_data.split('<!-- ')
    for b in blocks:
        if not b.strip(): continue
        parts = b.split(' -->\n', 1)
        if len(parts) == 2:
            model = parts[0].strip()
            content = parts[1].strip()
            # Determine badge text based on title or model
            badge_text = "Nowość"
            if "48V" in model or "48V" in content: badge_text = "Taśma COB 48V"
            elif "HPD" in model: badge_text = "Rozdzielacz"
            output_html += generate_accordion(model, content, current_idx, badge_text)
            current_idx += 1

with open("/Users/karolbohdanowicz/my-ai-agents/prescot/new_products.html", "w") as out:
    out.write(output_html)

print("Generated new_products.html with", current_idx - 100, "products")
