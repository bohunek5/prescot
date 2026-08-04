import re
import html
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Wczytanie 48V
with open('../tasmy-cob-48v-opisy.html', 'r', encoding='utf-8') as f:
    html_48v = f.read()

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
    
    div_open = raw.count('<div')
    div_close = raw.count('</div')
    sec_open = raw.count('<section')
    sec_close = raw.count('</section')
    if sec_open > sec_close:
        raw += '\n</section>' * (sec_open - sec_close)
    if div_open > div_close:
        raw += '\n</div>' * (div_open - div_close)
    db_48v[model] = raw

# 2. Wczytanie Rozdzielaczy
with open('../rozdzielacze-opisy.html', 'r', encoding='utf-8') as f:
    html_rozd = f.read()
    
db_rozd = {}
parts = html_rozd.split('<!-- HPD-')
for part in parts[1:]:
    model = 'HPD-' + part.split('-->')[0].strip()
    raw = part.split('-->', 1)[1].strip()
    
    div_open = raw.count('<div')
    div_close = raw.count('</div')
    sec_open = raw.count('<section')
    sec_close = raw.count('</section')
    if sec_open > sec_close:
        raw += '\n</section>' * (sec_open - sec_close)
    if div_open > div_close:
        raw += '\n</div>' * (div_open - div_close)
    db_rozd[model] = raw

# 3. Naprawa index.html (brakujące przyciski WAPRO)
missing_wapro_buttons = """<div class="sub-tabs">
<button class="active" onclick="switchSubTab('wapro', 'tasmy', this)"><svg fill="none" height="18" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewbox="0 0 24 24" width="18"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.9 1.2 1.5 1.5 2.5"></path><path d="M9 18h6"></path><path d="M10 22h4"></path></svg> Taśmy LED (22)</button>
<button onclick="switchSubTab('wapro', 'sterowniki', this)"><svg fill="none" height="18" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewbox="0 0 24 24" width="18"><line x1="21" x2="14" y1="4" y2="4"></line><line x1="10" x2="3" y1="4" y2="4"></line><line x1="21" x2="12" y1="12" y2="12"></line><line x1="8" x2="3" y1="12" y2="12"></line><line x1="21" x2="16" y1="20" y2="20"></line><line x1="12" x2="3" y1="20" y2="20"></line><line x1="14" x2="14" y1="1" y2="7"></line><line x1="8" x2="8" y1="9" y2="15"></line><line x1="16" x2="16" y1="17" y2="23"></line></svg> Sterowniki LED (5)</button>
<button onclick="switchSubTab('wapro', 'zasilacze', this)"><svg fill="none" height="18" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewbox="0 0 24 24" width="18"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg> Zasilacze Scharfer (20)</button>
<button onclick="switchSubTab('wapro', 'profile', this)"><svg fill="none" height="18" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewbox="0 0 24 24" width="18"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"></path><path d="M3.27 6.96L12 12.01l8.73-5.05"></path><path d="M12 22.08V12"></path></svg> Profile KLUŚ (21)</button>
<button onclick="switchSubTab('wapro', 'zlaczki', this)"><svg fill="none" height="18" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewbox="0 0 24 24" width="18"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg> Złączki bezlutowe (17)</button>
</div>\n"""
if '<div class="sub-tabs">' not in text[text.find('id="panel-wapro"'):text.find('id="wapro-tasmy"')]:
    # Need to insert it
    panel_start = text.find('<div class="main-tab-panel" id="panel-wapro">')
    if panel_start == -1:
        panel_start = text.find('<div class="main-tab-panel active" id="panel-wapro">')
        
    sub_tab_panel = text.find('<div class="sub-tab-panel active" id="wapro-tasmy">', panel_start)
    text = text[:sub_tab_panel] + missing_wapro_buttons + text[sub_tab_panel:]

# Zabezpieczenie przez niezamknietym wapro-tasmy z poprzedniego stanu
# W oryginalnym pliku WAPRO mialo zepsuta strukture z brakiem </div> dla wapro-tasmy
# Ale dodanie </div> mogloby zepsuc wapro-sterowniki. Let's find end of wapro-tasmy
sterowniki_start = text.find('<div class="sub-tab-panel" id="wapro-sterowniki">')
if sterowniki_start != -1:
    before = text[:sterowniki_start].strip()
    if not before.endswith('</div>'):
        # wapro-tasmy not closed!
        text = text[:sterowniki_start] + '</div>\n' + text[sterowniki_start:]

# 4. Generate the HTML for the new items
injected_html = ""
next_num = 23 # Taśmy ends at 22
for model, raw in db_48v.items():
    escaped_html = html.escape(raw)
    injected_html += f"""<div class="product-accordion" data-model="{model}">
<button class="product-trigger" onclick="toggleProduct(this)">
<div class="product-info">
<span class="product-model">{next_num}. {model}</span>
<span class="product-label-badge">Taśmy COB 48V</span>
</div>
<span class="product-arrow">▼</span>
</button>
<div class="product-body">
<div class="product-controls">
<button class="control-btn btn-edit" id="btn-edit-wapro-{model}" onclick="toggleEdit('wapro', 'tasmy', '{model}')">Edytuj opis</button>
<button class="control-btn btn-save" id="btn-save-wapro-{model}" onclick="saveDescription('wapro', 'tasmy', '{model}')" style="display: none;">Zapisz opis</button>
<button class="control-btn btn-copy" onclick="copyDescriptionHtml('wapro', '{model}', this)" style="border-color: #f59e0b; color: #f59e0b;" title="Kopiuj opis HTML">Kopiuj opis HTML</button>
<button class="control-btn btn-ean" onclick="navigator.clipboard.writeText('BRAK'); this.innerText='Skopiowano!'; setTimeout(()=>this.innerText='EAN: BRAK', 2000);" style="border-color: #0ea5e9; color: #0ea5e9;" title="Skopiuj EAN">EAN: BRAK</button>
<span class="control-status" id="status-wapro-{model}"></span>
</div>
<div class="model-block" id="desc-view-wapro-{model}">
{raw}
</div>
<textarea id="desc-wapro-{model}" style="display:none;">{escaped_html}</textarea>
</div>
</div>\n"""
    next_num += 1

# Generate rozdzielacze HTML
for model, raw in db_rozd.items():
    escaped_html = html.escape(raw)
    injected_html += f"""<div class="product-accordion" data-model="{model}">
<button class="product-trigger" onclick="toggleProduct(this)">
<div class="product-info">
<span class="product-model">{next_num}. {model}</span>
<span class="product-label-badge">Rozdzielacze mocy</span>
</div>
<span class="product-arrow">▼</span>
</button>
<div class="product-body">
<div class="product-controls">
<button class="control-btn btn-edit" id="btn-edit-wapro-{model}" onclick="toggleEdit('wapro', 'tasmy', '{model}')">Edytuj opis</button>
<button class="control-btn btn-save" id="btn-save-wapro-{model}" onclick="saveDescription('wapro', 'tasmy', '{model}')" style="display: none;">Zapisz opis</button>
<button class="control-btn btn-copy" onclick="copyDescriptionHtml('wapro', '{model}', this)" style="border-color: #f59e0b; color: #f59e0b;" title="Kopiuj opis HTML">Kopiuj opis HTML</button>
<button class="control-btn btn-ean" onclick="navigator.clipboard.writeText('BRAK'); this.innerText='Skopiowano!'; setTimeout(()=>this.innerText='EAN: BRAK', 2000);" style="border-color: #0ea5e9; color: #0ea5e9;" title="Skopiuj EAN">EAN: BRAK</button>
<span class="control-status" id="status-wapro-{model}"></span>
</div>
<div class="model-block" id="desc-view-wapro-{model}">
{raw}
</div>
<textarea id="desc-wapro-{model}" style="display:none;">{escaped_html}</textarea>
</div>
</div>\n"""
    next_num += 1

# Wklejamy na koniec wapro-tasmy
# Szukamy zamkniecia wapro-tasmy, jesli go naprawilismy wyzej to sterowniki_start to poczatek nast sekcji
sterowniki_start = text.find('<div class="sub-tab-panel" id="wapro-sterowniki">')
if sterowniki_start != -1:
    text = text[:sterowniki_start] + injected_html + '\n' + text[sterowniki_start:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print(f"Dodano {len(db_48v)} tasm 48V oraz {len(db_rozd)} rozdzielaczy do wapro-tasmy.")
