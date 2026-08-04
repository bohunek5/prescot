import re
import html

# Load FC8 description
fc8_desc = """<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
 <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
 <font color="#ffffff">ZŁĄCZKA LED</font>
 </span>

 <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
 Wygodne łączenie pod kątem 90°
 </h3>

 <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
 Przeznaczona do łączenia taśm SMD i COB o szerokości laminatu 8mm. Złącze typu L ("kątowe") idealnie sprawdza się na załamaniach profili oraz przy montażu w narożnikach ścian, półek czy sufitów podwieszanych.
 </p>
</section>

<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
 <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
 <font color="#ffffff">KLUCZOWE CECHY</font>
 </span>

 <ul style="font-family:inherit; margin:0; padding:0 0 0 20px; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
 <li style="font-family:inherit; margin-bottom:6px;"><strong style="font-family:inherit; color:inherit !important;">Złącze kątowe (typ L):</strong> Pozwala ominąć potrzebę lutowania przy zmianie kierunku obwodu pod kątem prostym.</li>
 <li style="font-family:inherit; margin-bottom:6px;"><strong style="font-family:inherit; color:inherit !important;">Szerokość 8mm:</strong> Odpowiednia dla standardowych taśm jednokolorowych.</li>
 <li style="font-family:inherit; margin-bottom:0;"><strong style="font-family:inherit; color:inherit !important;">Wytrzymałe zapięcie:</strong> Ostre, pionowe piny (zęby) solidnie przebijają się przez laminat, tworząc trwałe połączenie na lata.</li>
 </ul>
</section>

<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
 <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
 <font color="#ffffff">GDZIE UŻYĆ</font>
 </span>

 <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
 Narożniki i meble
 </h3>

 <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
 Ułatwia estetyczne przejście przez narożnik i pomaga zachować ciągłość podświetlenia tam, gdzie klasyczne zagięcie taśmy byłoby ryzykowne. Przed zaciśnięciem wyrównaj biegunowość, dosuń taśmę lub przewód do środka złączki i zaciśnij piny pionowo.
 </p>
</section>

<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
 <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
 <font color="#ffffff">Dobór</font>
 </span>

 <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
 8mm, 12/24V
 </h3>

 <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
 Dobierz złączkę do szerokości PCB oraz rodzaju taśmy SMD/COB mono. Zakres pracy: <strong style="font-family:inherit; color:inherit !important;">12/24V</strong>. Indeks handlowy: <strong style="font-family:inherit; color:inherit !important;">FC8-MONO-MULTI-L</strong>.
 </p>
</section>

<section style="font-family:inherit; margin:0 0 28px 0; padding:24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">

 <div style="font-family:inherit; margin-bottom:22px; background:none !important; background-color:transparent !important; color:inherit;">
 <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
 <font color="#ffffff">Praktyczne poradniki</font>
 </span>

 <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:24px; line-height:1.25; font-weight:700;">
 Praktyczne poradniki dla Twoich instalacji
 </h3>

 <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.72; font-size:14px; line-height:1.6;">
 Poniższe poradniki prowadzą dalej: od doboru taśmy i profilu po montaż, zasilanie oraz ochronę instalacji.
 </p>
 </div>

 <div style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(230px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit;">

 <div style="font-family:inherit; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit;">
 <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak czytać parametry taśmy LED?</strong>
 <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">moc, lumeny, CRI, napięcie i IP</small>
 <a href="https://www.prescot.com.pl/pl/n/23" style="font-family:inherit; display:inline-block; min-width:142px; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important;">
 <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
 </a>
 </div>
 <div style="font-family:inherit; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit;">
 <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Montaż taśmy LED na zewnątrz</strong>
 <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">IP, uszczelnienie i ochrona połączeń</small>
 <a href="https://www.prescot.com.pl/pl/n/16" style="font-family:inherit; display:inline-block; min-width:142px; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important;">
 <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
 </a>
 </div>
 <div style="font-family:inherit; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit;">
 <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać taśmę LED do mieszkania?</strong>
 <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">barwa, moc i miejsce montażu</small>
 <a href="https://www.prescot.com.pl/pl/n/12" style="font-family:inherit; display:inline-block; min-width:142px; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important;">
 <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
 </a>
 </div>
 <div style="font-family:inherit; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit;">
 <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać profil aluminiowy do taśmy LED?</strong>
 <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">profil, klosz, chłodzenie i estetyka linii światła</small>
 <a href="https://www.prescot.com.pl/pl/n/15" style="font-family:inherit; display:inline-block; min-width:142px; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important;">
 <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
 </a>
 </div>

 </div>
</section>"""
fc8_escaped = html.escape(fc8_desc)

def extract_block(html_text, start_tag):
    start_idx = html_text.find(start_tag)
    if start_idx == -1:
        return ""
    
    # Simple nested div counter
    div_count = 0
    i = start_idx
    while i < len(html_text):
        if html_text[i:i+4] == '<div':
            div_count += 1
            i += 4
        elif html_text[i:i+6] == '</div>':
            div_count -= 1
            i += 6
            if div_count == 0:
                return html_text[start_idx:i]
        else:
            i += 1
            
    return ""

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Tab Counts (12) -> (17) for zlaczki
content = content.replace('Złączki bezlutowe (12)', 'Złączki bezlutowe (17)')

# 2. Update FC8-MONO-MULTI-L descriptions
platforms = ['wapro', 'tim', 'allegro']
for platform in platforms:
    # Update model block
    pattern_block = r'(<div class="model-block" id="desc-view-' + platform + r'-FC8-MONO-MULTI-L">)(.*?)(</div>\s*<div class="edit-block")'
    content = re.sub(pattern_block, r'\1\n' + fc8_desc + r'\n\3', content, flags=re.DOTALL)
    
    # Update textarea
    pattern_textarea = r'(<textarea class="edit-textarea" id="textarea-' + platform + r'-FC8-MONO-MULTI-L"[^>]*>)(.*?)(</textarea>)'
    content = re.sub(pattern_textarea, r'\1' + fc8_escaped + r'\3', content, flags=re.DOTALL)

# 3. Add 5 missing RGB SKUs
new_skus = [
    ('FC10-COB-RGB-TP', 'Złączka bezlutowa 10mm RGB – zasilanie'),
    ('FC10-SMD-RGB-TP', 'Złączka bezlutowa 10mm RGB – zasilanie'),
    ('FC10-SMD-RGB-TPT', 'Złączka bezlutowa 10mm RGB – łączenie proste'),
    ('FC10-COB-RGB-TPT', 'Złączka bezlutowa 10mm RGB – łączenie proste'),
    ('FC10-SMD-RGBW-TP', 'Złączka bezlutowa 12mm RGBW – zasilanie')
]

def generate_accordion(sku, badge, index, platform, content_html):
    base_sku = 'FC10-MONO-MULTI-TPT' if 'TPT' in sku else 'FC10-MONO-MULTI-TP'
    start_tag = f'<div class="product-accordion" data-model="{base_sku}">'
    
    block = extract_block(content_html, start_tag)
    if not block:
        print(f"Could not extract block for {base_sku}")
        return ""
    
    block = re.sub(r'<span class="product-model">\d+\.\s*' + base_sku + r'</span>', f'<span class="product-model">{index}. {sku}</span>', block)
    block = re.sub(r'<span class="product-label-badge">.*?</span>', f'<span class="product-label-badge">{badge}</span>', block)
    block = block.replace(f'data-model="{base_sku}"', f'data-model="{sku}"')
    
    block = block.replace(f'desc-view-{platform}-{base_sku}', f'desc-view-{platform}-{sku}')
    block = block.replace(f'desc-edit-{platform}-{base_sku}', f'desc-edit-{platform}-{sku}')
    block = block.replace(f'textarea-{platform}-{base_sku}', f'textarea-{platform}-{sku}')
    block = block.replace(f"'{platform}', 'zlaczki', '{base_sku}'", f"'{platform}', 'zlaczki', '{sku}'")
    block = block.replace(f"'{platform}', '{base_sku}'", f"'{platform}', '{sku}'")
    block = block.replace(f'btn-edit-{platform}-{base_sku}', f'btn-edit-{platform}-{sku}')
    block = block.replace(f'btn-save-{platform}-{base_sku}', f'btn-save-{platform}-{sku}')
    block = block.replace(f'status-{platform}-{base_sku}', f'status-{platform}-{sku}')
    
    rgb_type = 'RGBW' if 'RGBW' in sku else 'RGB'
    width = '12mm' if 'RGBW' in sku else '10mm'
    
    block = block.replace('ZŁĄCZKA MONO', f'ZŁĄCZKA {rgb_type}')
    block = block.replace('Szerokość 10mm', f'Szerokość {width}')
    block = block.replace('szerokości laminatu 10mm', f'szerokości laminatu {width}')
    block = block.replace('do taśm jednokolorowych (MONO)', f'do taśm wielokolorowych ({rgb_type})')
    
    return block

platforms.reverse()
for platform in platforms:
    panel_id_str = f'<div class="sub-tab-panel" id="{platform}-zlaczki">'
    start_idx = content.find(panel_id_str)
    if start_idx == -1:
        print(f"Panel not found for {platform}")
        continue
    
    if platform == 'wapro':
        end_str = '</div>\n</div>\n<!-- ==================== TIM TAB PANEL ==================== -->'
    elif platform == 'tim':
        end_str = '</div>\n</div>\n<!-- ==================== ALLEGRO TAB PANEL ==================== -->'
    else:
        end_str = '</div>\n</div>\n<script>'
        
    end_idx = content.find(end_str, start_idx)
    if end_idx == -1:
        print(f"End string not found for {platform}")
        continue
        
    accordions_html = "\n"
    current_index = 13
    for sku, badge in new_skus:
        # Important: pass the chunk of HTML for this specific platform to avoid cross-platform extraction
        platform_html = content[start_idx:end_idx]
        accordions_html += generate_accordion(sku, badge, current_index, platform, platform_html) + "\n"
        current_index += 1
        
    content = content[:end_idx] + accordions_html + content[end_idx:]

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done appending Zlaczki!")
