import re
import html
import sys
import os

# Szykowanie poprawnego wstrzykiwania

# 1. Wczytajmy bazy
path_48v = '../tasmy-cob-48v-opisy.html'
path_rozd = '../rozdzielacze-opisy.html'

if not os.path.exists(path_48v):
    print("Brak pliku", path_48v)
    sys.exit(1)
if not os.path.exists(path_rozd):
    print("Brak pliku", path_rozd)
    sys.exit(1)

with open(path_48v, 'r', encoding='utf-8') as f:
    html_48v = f.read()

with open(path_rozd, 'r', encoding='utf-8') as f:
    html_rozd = f.read()

with open('index.html', 'r', encoding='utf-8') as f:
    idx_html = f.read()


new_items = []
current_id_number = 100

def parse_and_generate(source_html, badge_text):
    global current_id_number
    
    pattern = r'<button class="copy-btn" onclick="copyHtml\(\'([^\']+)\'\)".*?>(.*?)</button>\s*<div id="\1">(.*?)</div>\s*(?=</section>|<div class="product-wrapper">|$)'
    matches = list(re.finditer(pattern, source_html, flags=re.DOTALL))
    if not matches:
        # Drugi wzorzec z div wrapperem
        pattern = r'<div class="product-wrapper">.*?<button class="copy-btn" onclick="copyHtml\(\'([^\']+)\'\)".*?</button>\s*<div id="\1">(.*?)</div>\s*</div>'
        matches = list(re.finditer(pattern, source_html, flags=re.DOTALL))
        
    for match in matches:
        model = match.group(1)
        raw_html = match.group(2) if len(match.groups()) == 2 else match.group(3)
        raw_html = raw_html.strip()
        
        escaped_html = html.escape(raw_html)
        
        item_html = f"""
<div class="product-accordion" data-model="{model}">
<button class="product-trigger" onclick="toggleProduct(this)">
<div class="product-info">
<span class="product-model">{current_id_number}. {model}</span>
<span class="product-label-badge">{badge_text}</span>
</div>
<span class="product-arrow">▼</span>
</button>
<div class="product-body">
<div class="model-block" id="desc-view-wapro-{model}">{raw_html}</div>
<textarea id="desc-wapro-{model}" style="display:none;">{escaped_html}</textarea>
<div class="controls-bar" id="controls-wapro-{model}">
<button class="control-btn btn-edit" id="btn-edit-wapro-{model}" onclick="toggleEdit('wapro', 'tasmy', '{model}')">Edytuj opis</button>
<button class="control-btn btn-save" id="btn-save-wapro-{model}" onclick="saveDescription('wapro', 'tasmy', '{model}')" style="display: none;">Zapisz opis</button>
<button class="control-btn btn-copy" onclick="copyDescriptionHtml('wapro', '{model}', this)" style="border-color: #f59e0b; color: #f59e0b;" title="Kopiuj opis HTML">Kopiuj opis HTML</button>
<button class="control-btn btn-ean" onclick="navigator.clipboard.writeText('BRAK'); this.innerText='Skopiowano!'; setTimeout(()=>this.innerText='EAN: BRAK', 2000);" style="border-color: #0ea5e9; color: #0ea5e9;" title="Skopiuj EAN">EAN: BRAK</button>
<span class="control-status" id="status-wapro-{model}"></span>
</div>
</div>
</div>"""
        new_items.append(item_html)
        current_id_number += 1

parse_and_generate(html_48v, "Taśma COB 48V")
parse_and_generate(html_rozd, "Rozdzielacz mocy")

final_injections = "\n".join(new_items)

target = '<div class="sub-tab-panel" id="wapro-sterowniki">'
idx = idx_html.find(target)

if idx != -1:
    last_div = idx_html.rfind('</div>', 0, idx)
    out_html = idx_html[:last_div] + final_injections + '\n</div>\n' + idx_html[idx:]
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(out_html)
    print("Wstrzyknieto pomyslnie")
else:
    print("Blad wstrzykiwania")
