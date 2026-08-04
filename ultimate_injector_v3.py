import re

def parse_cob_48v():
    with open('../tasmy-cob-48v-opisy.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    parts = html.split('<div class="product-wrapper">')
    items = []
    
    for p in parts[1:]:
        model_match = re.search(r'id="([^"]+)"', p)
        if not model_match: continue
        model = model_match.group(1)
        if not model.startswith('48EC480'): continue
        
        # Balance div and section tags in the raw html piece
        # Find where the id="MODEL" div starts
        content_start = p.find(f'id="{model}"')
        content_start = p.find('>', content_start) + 1
        raw_html = p[content_start:]
        
        # Remove trailing </div> of id="..." div AND product-wrapper
        raw_html = raw_html[:raw_html.rfind('</div>')]
        raw_html = raw_html[:raw_html.rfind('</div>')]
        raw_html = raw_html.strip()
        
        # Now balance the raw_html just in case
        d_op = raw_html.count('<div')
        d_cl = raw_html.count('</div')
        s_op = raw_html.count('<section')
        s_cl = raw_html.count('</section')
        while s_cl < s_op:
            raw_html += '\n</section>'
            s_cl += 1
        while d_cl < d_op:
            raw_html += '\n</div>'
            d_cl += 1
        
        # wrap in accordion
        acc = f'''<div class="product-accordion" data-model="{model}">
<button class="product-trigger" onclick="toggleProduct(this)">
<div class="product-info">
<span class="product-model">{{NUM}}. {model}</span>
<span class="product-name">{model} (Taśma COB 48V)</span>
</div>
<svg class="chevron" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
</button>
<div class="product-body">
<div class="model-block" id="desc-view-wapro-{model}">
{raw_html}
</div>
<textarea id="desc-wapro-{model}" style="display:none;">
{raw_html}
</textarea>
</div>
<div class="product-controls">
<button class="control-btn btn-edit" id="btn-edit-wapro-{model}" onclick="toggleEdit('wapro', 'tasmy', '{model}')">Edytuj opis</button>
<button class="control-btn btn-save" id="btn-save-wapro-{model}" onclick="saveDescription('wapro', 'tasmy', '{model}')" style="display: none;">Zapisz opis</button>
<button class="control-btn btn-copy" onclick="copyDescriptionHtml('wapro', '{model}', this)" style="border-color: #f59e0b; color: #f59e0b;" title="Kopiuj opis HTML">Kopiuj opis HTML</button>
<button class="control-btn btn-ean" onclick="navigator.clipboard.writeText('BRAK'); this.innerText='Skopiowano!'; setTimeout(()=>this.innerText='EAN: BRAK', 2000);" style="border-color: #0ea5e9; color: #0ea5e9;" title="Skopiuj EAN">EAN: BRAK</button>
<span class="control-status" id="status-wapro-{model}"></span>
</div>
</div>'''
        items.append(acc)
    return items

def parse_rozdzielacze():
    with open('../rozdzielacze-opisy.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    parts = html.split('<!-- HPD-')
    items = []
    
    for p in parts[1:]:
        model = 'HPD-' + p.split('-->')[0].strip()
        
        # balance tags
        div_op = p.count('<div')
        div_cl = p.count('</div')
        sec_op = p.count('<section')
        sec_cl = p.count('</section')
        
        while sec_cl < sec_op:
            p += '\n</section>'
            sec_cl += 1
        while div_cl < div_op:
            p += '\n</div>'
            div_cl += 1
        
        p = '<!-- ' + model + ' -->' + p[p.find('-->')+3:]
        
        # wrap in accordion
        raw_html = p.strip()
        acc = f'''<div class="product-accordion" data-model="{model}">
<button class="product-trigger" onclick="toggleProduct(this)">
<div class="product-info">
<span class="product-model">{{NUM}}. {model}</span>
<span class="product-name">{model} (Rozdzielacz)</span>
</div>
<svg class="chevron" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
</button>
<div class="product-body">
<div class="model-block" id="desc-view-wapro-{model}">
{raw_html}
</div>
<textarea id="desc-wapro-{model}" style="display:none;">
{raw_html}
</textarea>
</div>
<div class="product-controls">
<button class="control-btn btn-edit" id="btn-edit-wapro-{model}" onclick="toggleEdit('wapro', 'zlaczki', '{model}')">Edytuj opis</button>
<button class="control-btn btn-save" id="btn-save-wapro-{model}" onclick="saveDescription('wapro', 'zlaczki', '{model}')" style="display: none;">Zapisz opis</button>
<button class="control-btn btn-copy" onclick="copyDescriptionHtml('wapro', '{model}', this)" style="border-color: #f59e0b; color: #f59e0b;" title="Kopiuj opis HTML">Kopiuj opis HTML</button>
<button class="control-btn btn-ean" onclick="navigator.clipboard.writeText('BRAK'); this.innerText='Skopiowano!'; setTimeout(()=>this.innerText='EAN: BRAK', 2000);" style="border-color: #0ea5e9; color: #0ea5e9;" title="Skopiuj EAN">EAN: BRAK</button>
<span class="control-status" id="status-wapro-{model}"></span>
</div>
</div>'''
        items.append(acc)
    return items

def inject_items():
    cob_items = parse_cob_48v()
    rozd_items = parse_rozdzielacze()
    
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update logo size (3x larger)
    html = re.sub(
        r'<img src="prescot_logo.svg" alt="Prescot LED" style="height: 60px; margin-bottom: 15px;" />',
        r'<img src="prescot_logo.svg" alt="Prescot LED" style="height: 180px; margin-bottom: 15px;" />',
        html
    )
    
    # 2. Insert sub-tabs if missing
    if '<div class="sub-tabs">' not in html[:html.find('id="wapro-tasmy"')]:
        sub_tabs_html = """
<div class="sub-tabs">
  <button class="active" onclick="switchSubTab('wapro', 'tasmy', this)">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
    Taśmy LED (72)
  </button>
  <button onclick="switchSubTab('wapro', 'sterowniki', this)">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
    Sterowniki LED (5)
  </button>
  <button onclick="switchSubTab('wapro', 'zasilacze', this)">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="15" rx="2" ry="2"/><polyline points="17 2 12 7 7 2"/></svg>
    Zasilacze Scharfer (20)
  </button>
  <button onclick="switchSubTab('wapro', 'profile', this)">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
    Profile KLUŚ (21)
  </button>
  <button onclick="switchSubTab('wapro', 'zlaczki', this)">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>
    Złączki i rozdzielacze bezlutowe (22)
  </button>
</div>
"""
        # Insert after <!-- SUB-TABS -->
        insert_idx = html.find('<!-- SUB-TABS -->') + len('<!-- SUB-TABS -->\n')
        html = html[:insert_idx] + sub_tabs_html + html[insert_idx:]

    # 3. Update the existing tab name if it's already there but just "Złączki bezlutowe (17)"
    html = html.replace('Złączki bezlutowe (17)', 'Złączki i rozdzielacze bezlutowe (22)')

    # 4. Inject 48V items at the end of wapro-tasmy
    # Numbering from 67
    for i, cob in enumerate(cob_items):
        cob_items[i] = cob.replace('{NUM}', str(67 + i))

    tasmy_insert_idx = html.find('id="wapro-sterowniki"')
    tasmy_insert_idx = html.rfind('</div>', 0, tasmy_insert_idx) # Before the closing div of wapro-tasmy
    tasmy_insert_idx = html.rfind('</div>', 0, tasmy_insert_idx) # Two divs to go inside
    
    html = html[:tasmy_insert_idx+6] + '\n' + '\n'.join(cob_items) + '\n' + html[tasmy_insert_idx+6:]

    # 5. Inject Rozdzielacze at the end of wapro-zlaczki
    # Numbering from 18
    for i, rozd in enumerate(rozd_items):
        rozd_items[i] = rozd.replace('{NUM}', str(18 + i))
        
    zlaczki_insert_idx = html.find('<!-- ==================== TIM TAB PANEL')
    zlaczki_insert_idx = html.rfind('</div>', 0, zlaczki_insert_idx) 
    zlaczki_insert_idx = html.rfind('</div>', 0, zlaczki_insert_idx) 
    
    html = html[:zlaczki_insert_idx+6] + '\n' + '\n'.join(rozd_items) + '\n' + html[zlaczki_insert_idx+6:]

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    print(f"Injected {len(cob_items)} cob items and {len(rozd_items)} rozdzielacze successfully.")

inject_items()
