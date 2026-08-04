import re
import html
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's clean it by replacing the whole content of the accordion
# for all freshly added models (48EC480-050-8-NW1, 48EC480-050-8-NW, 48EC480-050-8-NW50,
# 48EC480-050-8-WW1, 48EC480-050-8-WW, 48EC480-050-8-WW50, and HPD-...)

with open('../tasmy-cob-48v-opisy.html', 'r', encoding='utf-8') as f:
    html_48v = f.read()

with open('../rozdzielacze-opisy.html', 'r', encoding='utf-8') as f:
    html_rozd = f.read()

# 1. Parse tasmy-cob-48v-opisy.html
db_48v = {}
pattern = r'<button class="copy-btn" onclick="copyHtml\(\'([^\']+)\'\)".*?>(.*?)</button>\s*<div id="\1">(.*?)</div>\s*(?=</section>|<div class="product-wrapper">|$)'
matches = list(re.finditer(pattern, html_48v, flags=re.DOTALL))
if not matches:
    pattern = r'<div class="product-wrapper">.*?<button class="copy-btn" onclick="copyHtml\(\'([^\']+)\'\)".*?</button>\s*<div id="\1">(.*?)</div>\s*</div>'
    matches = list(re.finditer(pattern, html_48v, flags=re.DOTALL))

for match in matches:
    model = match.group(1)
    raw = match.group(2) if len(match.groups()) == 2 else match.group(3)
    raw = raw.strip()
    
    # Fix balance for 48v
    div_open = raw.count('<div')
    div_close = raw.count('</div')
    sec_open = raw.count('<section')
    sec_close = raw.count('</section')
    
    if sec_open > sec_close:
        raw += '\n</section>' * (sec_open - sec_close)
    if div_open > div_close:
        raw += '\n</div>' * (div_open - div_close)
        
    db_48v[model] = raw

# 2. Parse rozdzielacze-opisy.html
# It doesn't have the wrapper script, just sections.
# Let's extract by <!-- HPD-xxx -->
db_rozd = {}
parts = html_rozd.split('<!-- HPD-')
for part in parts[1:]:
    model = 'HPD-' + part.split('-->')[0].strip()
    raw = part.split('-->', 1)[1].strip()
    
    # Fix balance
    div_open = raw.count('<div')
    div_close = raw.count('</div')
    sec_open = raw.count('<section')
    sec_close = raw.count('</section')
    
    if sec_open > sec_close:
        raw += '\n</section>' * (sec_open - sec_close)
    if div_open > div_close:
        raw += '\n</div>' * (div_open - div_close)
        
    db_rozd[model] = raw

# 3. Replace in index.html
parts_idx = text.split('<div class="product-accordion" data-model="')
out_html = parts_idx[0]

for p in parts_idx[1:]:
    model_id = p.split('">')[0]
    is_new = False
    raw_html = ""
    
    if model_id in db_48v:
        raw_html = db_48v[model_id]
        is_new = True
    elif model_id in db_rozd:
        raw_html = db_rozd[model_id]
        is_new = True
        
    if is_new:
        # Reconstruct the entire accordion perfectly
        # We need to extract the product-info from the current HTML
        # because it has the number and badge text.
        info_start = p.find('<div class="product-info">')
        info_end = p.find('</div>', info_start) + 6
        product_info = p[info_start:info_end]
        
        # We'll just build it from scratch
        escaped_html = html.escape(raw_html)
        
        rebuilt = f"""<button class="product-trigger" onclick="toggleProduct(this)">
{product_info}
<span class="product-arrow">▼</span>
</button>
<div class="product-body">
<div class="model-block" id="desc-view-wapro-{model_id}">
{raw_html}
</div>
<textarea id="desc-wapro-{model_id}" style="display:none;">{escaped_html}</textarea>
<div class="controls-bar" id="controls-wapro-{model_id}">
<button class="control-btn btn-edit" id="btn-edit-wapro-{model_id}" onclick="toggleEdit('wapro', 'tasmy', '{model_id}')">Edytuj opis</button>
<button class="control-btn btn-save" id="btn-save-wapro-{model_id}" onclick="saveDescription('wapro', 'tasmy', '{model_id}')" style="display: none;">Zapisz opis</button>
<button class="control-btn btn-copy" onclick="copyDescriptionHtml('wapro', '{model_id}', this)" style="border-color: #f59e0b; color: #f59e0b;" title="Kopiuj opis HTML">Kopiuj opis HTML</button>
<button class="control-btn btn-ean" onclick="navigator.clipboard.writeText('BRAK'); this.innerText='Skopiowano!'; setTimeout(()=>this.innerText='EAN: BRAK', 2000);" style="border-color: #0ea5e9; color: #0ea5e9;" title="Skopiuj EAN">EAN: BRAK</button>
<span class="control-status" id="status-wapro-{model_id}"></span>
</div>
</div>
</div>\n\n"""
        
        # We append to out_html
        out_html += '<div class="product-accordion" data-model="' + model_id + '">\n' + rebuilt
    else:
        # Just copy original
        out_html += '<div class="product-accordion" data-model="' + p

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(out_html)

print("Done replacing.")

