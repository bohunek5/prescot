import re
import pandas as pd

# Define factual descriptions
def get_sterownik_html(sku):
    typ = "Jednokolorowy (MONO)" if "MONO" in sku else ("CCT (Dual White)" if "CCT" in sku and "RGB" not in sku else ("RGB" if "RGB-" in sku else ("RGBW" if "RGBW" in sku else "RGBCCT")))
    return f"""<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; border:1px solid currentColor; border-radius:12px;">
  <h3 style="font-size:18px; margin:0 0 12px 0;">Specyfikacja techniczna ({sku}):</h3>
  <ul style="margin:0; padding-left:20px; font-size:14px; line-height:1.6;">
    <li><b>Typ sterownika:</b> {typ}</li>
    <li><b>Zasilanie wejściowe:</b> DC 5-24V (wtyk 5.5x2.1mm)</li>
    <li><b>Maksymalne obciążenie:</b> 12A łącznie (max 6A na kanał)</li>
    <li><b>Komunikacja:</b> Bezprzewodowa 2.4GHz RF</li>
    <li><b>Zasięg sterowania:</b> do 30m</li>
    <li><b>Temperatura pracy:</b> -25°C do 40°C</li>
    <li><b>Wymiary:</b> 74,5 x 35,6 x 16,5 mm</li>
    <li><b>Funkcje dodatkowe:</b> Auto-retransmisja i synchronizacja, przełączanie częstotliwości PWM, funkcja "Nie przeszkadzać"</li>
  </ul>
</section>"""

def get_zlaczka_html(sku):
    szerokosc = "8mm" if "FC8" in sku else "10mm"
    typ = "CCT" if "CCT" in sku else ("RGBW" if "RGBW" in sku else ("RGB" if "RGB" in sku else "MONO"))
    
    html = f"""<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; border:1px solid currentColor; border-radius:12px;">
  <h3 style="font-size:18px; margin:0 0 12px 0;">Specyfikacja techniczna ({sku}):</h3>
  <ul style="margin:0; padding-left:20px; font-size:14px; line-height:1.6;">
    <li><b>Zastosowanie:</b> Taśmy {typ} o szerokości {szerokosc}</li>
    <li><b>Typ montażu:</b> Szybkozłączka zaciskowa (bez lutowania)</li>
"""
    if "9IN1" in sku:
        html += f"""    <li><b>Warianty połączeń (9w1):</b> Taśma-Taśma, Taśma-Przewód, Przewód-Przewód, narożne L, boczne T, krzyżowe X</li>"""
    else:
        html += f"""    <li><b>Przeznaczenie:</b> Łączenie taśm LED i przewodów</li>"""
        
    html += f"""
    <li><b>Budowa:</b> Smukły, transparentny design pozwalający na montaż w profilach LED</li>
    <li><b>Zalety:</b> Brak ciemnych obszarów, pewny docisk dzięki pionowym pinom</li>
  </ul>
</section>"""
    return html

def get_scharfer_html(sku):
    parts = sku.split('-')
    if len(parts) >= 3:
        w = parts[1]
        v = parts[2]
    else:
        w = "?"
        v = "?"
        
    return f"""<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; border:1px solid currentColor; border-radius:12px;">
  <h3 style="font-size:18px; margin:0 0 12px 0;">Specyfikacja techniczna ({sku}):</h3>
  <ul style="margin:0; padding-left:20px; font-size:14px; line-height:1.6;">
    <li><b>Napięcie wyjściowe:</b> {v}V DC</li>
    <li><b>Moc znamionowa:</b> {w}W (obsługa 100% obciążenia)</li>
    <li><b>Klasa szczelności:</b> IP67 (wodoodporny)</li>
    <li><b>Gwarancja:</b> 5 lat</li>
    <li><b>Zabezpieczenia:</b> Zwarciowe, przeciążeniowe, nadnapięciowe</li>
  </ul>
</section>"""

# SKUs to update
sterowniki = ['PR-CCT-12A', 'PR-MONO-12A', 'PR-RGB-12A', 'PR-RGBCCT-12A', 'PR-RGBW-12A']
zlaczki = ['FC8-MONO-MULTI-9IN1', 'FC8-MONO-MULTI-TP', 'FC8-MONO-MULTI-TPT', 'FC8-MONO-MULTI', 'FC8-MONO-MULTI-L', 'FC8-MONO-MULTI-T', 
           'FC10-MONO-MULTI-9IN1', 'FC10-MONO-MULTI-TPT', 'FC10-MONO-MULTI', 'FC10-MONO-MULTI-L', 'FC10-MONO-MULTI-T', 'FC10-MONO-MULTI-TP',
           'FC10-COB-RGB-TP', 'FC10-COB-RGB-TPT', 'FC8-SMD-CCT-TP', 'FC10-SMD-RGB-TP', 'FC10-SMD-RGB-TPT', 'FC10-SMD-RGBW-TP', 'FC10-SMD-RGBW-TPT']
scharfer = ['SCH-18-12', 'SCH-20-12', 'SCH-30-12', 'SCH-45-12', 'SCH-60-12', 'SCH-100-12', 'SCH-150-12', 'SCH-200-12', 'SCH-300-12', 'SCH-400-12', 
            'SCH-18-24', 'SCH-20-24', 'SCH-30-24', 'SCH-45-24', 'SCH-60-24', 'SCH-100-24', 'SCH-150-24', 'SCH-200-24', 'SCH-300-24', 'SCH-400-24']

descriptions = {}
for s in sterowniki: descriptions[s] = get_sterownik_html(s)
for z in zlaczki: descriptions[z] = get_zlaczka_html(z)
for sc in scharfer: descriptions[sc] = get_scharfer_html(sc)

# Update index.html
index_path = '/Users/karolbohdanowicz/my-ai-agents/prescot/index.html'
with open(index_path, 'r', encoding='utf-8') as f:
    index_content = f.read()

updated_html = 0
for sku, html in descriptions.items():
    for tab in ['wapro', 'tim', 'allegro']:
        view_pattern = rf'(<div class="model-block" id="desc-view-{tab}-{sku}">)(.*?)(</div>\s*<div class="edit-block" id="desc-edit-{tab}-{sku}")'
        def replacer_view(match):
            return match.group(1) + "\n" + html + "\n" + match.group(3)
        index_content, c1 = re.subn(view_pattern, replacer_view, index_content, flags=re.DOTALL)
        
        textarea_pattern = rf'(<textarea class="edit-textarea" id="textarea-{tab}-{sku}"[^>]*>)(.*?)(</textarea>)'
        def replacer_textarea(match):
            return match.group(1) + "\n" + html + "\n" + match.group(3)
        index_content, c2 = re.subn(textarea_pattern, replacer_textarea, index_content, flags=re.DOTALL)
        
        if c1 > 0 or c2 > 0:
            updated_html += 1

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(index_content)

print(f"Updated {updated_html} elements in index.html")

# Update Excel
excel_path = '/Users/karolbohdanowicz/Desktop/EksportowaneArtykuly.xlsx'
df = pd.read_excel(excel_path)
updated_excel = 0
for idx, row in df.iterrows():
    sku = str(row['INDEKS_HANDLOWY']).strip()
    if sku in descriptions:
        df.at[idx, 'OPIS'] = descriptions[sku]
        updated_excel += 1

df.to_excel(excel_path, index=False)
print(f"Updated {updated_excel} rows in Excel")
