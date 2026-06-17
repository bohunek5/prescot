import re
import pandas as pd
import sys

USER_V2_FILE = "/Users/karolbohdanowicz/Downloads/opisy KAROL v2.html"
SCHARFER_TEXT = "/Users/karolbohdanowicz/Downloads/TOP Scharfer - OSTATECZNY.txt"
INDEX_HTML = "/Users/karolbohdanowicz/my-ai-agents/prescot/index.html"
EXCEL_FILE = "/Users/karolbohdanowicz/Desktop/EksportowaneArtykuly.xlsx"

master_dict = {}

# 1. Parse user's v2 HTML (for Profiles / Taśmy)
try:
    with open(USER_V2_FILE, "r", encoding="utf-8") as f:
        v2_content = f.read()
    v2_blocks = re.findall(r'<!-- START ([^ ]+) -->(.*?)<!-- KONIEC \1 -->', v2_content, re.DOTALL)
    for sku, html in v2_blocks:
        master_dict[sku.strip()] = html.strip()
    print(f"Extracted {len(v2_blocks)} blocks from v2 HTML")
except Exception as e:
    print("Error reading V2 file:", e)

# 2. Parse Scharfer
try:
    with open(SCHARFER_TEXT, "r", encoding="utf-8") as f:
        scharfer_content = f.read()
    scharfer_blocks = re.findall(r'START (SCH-[^\n]+)(.*?)KONIEC \1', scharfer_content, re.DOTALL)
    for sku, html in scharfer_blocks:
        sku = sku.strip()
        html = html.strip()
        
        # Inject 7-letnia gwarancja
        if 'Produkt objęty jest 7-letnią gwarancją' not in html:
            html = html.replace(
                "narażonych na wilgoć.",
                "narażonych na wilgoć. <strong style=\"font-family:inherit; color:inherit !important;\">Produkt objęty jest 7-letnią gwarancją producenta.</strong>"
            )
            html = html.replace(
                "ochroną przed wilgocią.",
                "ochroną przed wilgocią. <strong style=\"font-family:inherit; color:inherit !important;\">Produkt objęty jest 7-letnią gwarancją producenta.</strong>"
            )
        master_dict[sku] = html
    print(f"Extracted {len(scharfer_blocks)} Scharfer blocks")
except Exception as e:
    print("Error reading Scharfer text:", e)

# 3. Generate Sterowniki with strictly functional text
sterowniki_skus = ['PR-MONO-12A', 'PR-CCT-12A', 'PR-RGB-12A', 'PR-RGBW-12A', 'PR-RGBCCT-12A']

for sku in sterowniki_skus:
    nazwa = sku.replace("PR-", "").replace("-12A", "")
    
    if nazwa == "MONO":
        funkcje_opis = "Umożliwia sterowanie taśmami jednokolorowymi (MONO). Funkcje: płynne ściemnianie i rozjaśnianie (1-100%) bez efektu migotania PWM. Parowanie z wieloma nadajnikami (np. pilot i panel ścienny jednocześnie)."
    elif nazwa == "CCT":
        funkcje_opis = "Umożliwia sterowanie taśmami o zmiennej temperaturze barwowej (CCT). Funkcje: płynna regulacja temperatury bieli (ciepła-zimna) oraz niezależne ściemnianie (1-100%)."
    elif nazwa == "RGB":
        funkcje_opis = "Umożliwia sterowanie taśmami wielokolorowymi (RGB). Funkcje: precyzyjny wybór barwy (16 milionów kolorów), wbudowane programy dynamiczne, płynne ściemnianie."
    elif nazwa == "RGBW":
        funkcje_opis = "Umożliwia sterowanie taśmami wielokolorowymi z dodatkową diodą białą (RGBW). Funkcje: niezależne sterowanie kanałem białym i kolorami RGB, co pozwala na precyzyjne mieszanie barw."
    elif nazwa == "RGBCCT":
        funkcje_opis = "Umożliwia sterowanie najbardziej zaawansowanymi taśmami 5-kanałowymi (RGBCCT). Funkcje: pełna kontrola nad paletą RGB oraz niezależna, precyzyjna regulacja temperatury światła białego (CCT)."

    blog_sterowniki = """<section style="font-family:inherit; margin:18px 0 28px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <div style="font-family:inherit; margin-bottom:18px; background:none !important; background-color:transparent !important; color:inherit;">
    <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px;  line-height:1.2;">
    <font color="#ffffff">Praktyczne poradniki</font>
  </span>
    <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
      Jak zaplanować sterowanie w domu
    </h3>
    <p style="font-family:inherit; margin:0 0 16px 0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.78; font-size:14px; line-height:1.6;">
      Zobacz, jak połączyć piloty, panele ścienne i smartfony, by całe oświetlenie w domu było ze sobą spójne i łatwe w obsłudze.
    </p>
  </div>
  <div style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit; align-items:stretch;">
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Rodzaje sterowania taśmami LED</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">piloty, panele, WiFi i Smart Home</small>
      <a href="https://www.prescot.com.pl/pl/n/32" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać zasilacz do taśmy i sterownika?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">napięcie, rezerwa mocy i miejsce montażu</small>
      <a href="https://www.prescot.com.pl/pl/n/33" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
  </div>
</section>"""

    new_html = f"""<section style="font-family:inherit; margin:28px 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px;  line-height:1.2;">
    <font color="#ffffff">Sterownik LED Prescot {nazwa}</font>
  </span>
  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Odbiornik radiowy do taśm LED ({sku})
  </h3>
  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    Sterownik <strong style="font-family:inherit; color:inherit !important;">{sku}</strong> pracujący w standardzie RF 2.4GHz. {funkcje_opis} Można go powiązać z kilkoma nadajnikami (np. pilot i panel naścienny). Dodanie opcjonalnego mostka WiFi rozszerza jego funkcje o sterowanie z aplikacji mobilnej i asystentów głosowych.
  </p>
</section>
<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px;  line-height:1.2;">
    <font color="#ffffff">Parametry techniczne i funkcje użytkowe</font>
  </span>
  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Stabilne działanie i synchronizacja stref
  </h3>
  <ul style="font-family:inherit; margin:0; padding-left:18px; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    <li style="margin-bottom:6px;"><strong style="font-family:inherit; color:inherit !important;">Zasilanie i moc:</strong> Napięcie wejściowe DC 5-24V. Maksymalne łączne obciążenie to 12A (dla 12V obsłuży moce do 144W, dla 24V do 288W).</li>
    <li style="margin-bottom:6px;"><strong style="font-family:inherit; color:inherit !important;">Auto-retransmisja:</strong> Odbiorniki automatycznie przekazują sygnał radiowy między sobą (w promieniu 30m), wydłużając faktyczny zasięg instalacji.</li>
    <li style="margin-bottom:6px;"><strong style="font-family:inherit; color:inherit !important;">Auto-synchronizacja:</strong> Wiele odbiorników w jednej strefie automatycznie synchronizuje przejścia tonalne i programy dynamiczne.</li>
    <li style="margin-bottom:6px;"><strong style="font-family:inherit; color:inherit !important;">Tryb "Nie przeszkadzać":</strong> Możliwość ustawienia stanu zgaszonego po zaniku zasilania sieciowego (przydatne m.in. nocą).</li>
  </ul>
</section>
{blog_sterowniki}"""
    master_dict[sku] = new_html

print("Generated new Sterowniki")

# 4. Generate Złączki with explicit mention of COB and SMD connections
BLOG_ZLĄCZKI = """<section style="font-family:inherit; margin:0; padding:0; background:none !important; background-color:transparent !important; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px;  line-height:1.2;">
    <font color="#ffffff">Praktyczne poradniki</font>
  </span>
  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Szybki montaż instalacji LED
  </h3>
  <p style="font-family:inherit; margin:0 0 16px 0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.78; font-size:14px; line-height:1.6;">
    Sprawdź jak poprawnie łączyć taśmy LED bez lutowania i na co uważać przy cięciu.
  </p>
  <div style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit; align-items:stretch;">
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak łączyć taśmy LED?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">lutowanie czy złączki zaciskowe</small>
      <a href="https://www.prescot.com.pl/pl/n/18" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Cięcie i modyfikacja taśm</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">oznaczenia miejsc cięcia i profile</small>
      <a href="https://www.prescot.com.pl/pl/n/20" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
  </div>
</section>"""

def generate_zlaczka_html(model, nazwa):
    return f"""<section style="font-family:inherit; margin:28px 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px;  line-height:1.2;">
    <font color="#ffffff">Złączka zaciskowa LED 9w1 - {nazwa}</font>
  </span>
  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Szybkie łączenie taśm COB i SMD bez lutowania
  </h3>
  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    Złączka <strong style="font-family:inherit; color:inherit !important;">{model}</strong> to bezlutowe narzędzie instalacyjne z transparentną obudową, która nie zasłania diod i nie rzuca cienia w profilu. Ostre piny dociskowe przebijają laminat po włożeniu przewodu lub taśmy, zapewniając pewny styk. <br><br>
    <strong style="font-family:inherit; color:inherit !important;">Kompatybilność:</strong> Doskonale nadaje się do łączenia nowoczesnych taśm COB (tworząc jednolitą linię światła), standardowych taśm SMD, a także pozwala na ich bezpośrednie, wzajemne łączenie (np. przedłużenie taśmy COB taśmą SMD).
  </p>
</section>
<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px;  line-height:1.2;">
    <font color="#ffffff">9 konfiguracji montażowych</font>
  </span>
  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Uniwersalność i oszczędność czasu
  </h3>
  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    Konstrukcja 9w1 sprawia, że wystarczy przyciąć odpowiednio obudowę, aby uzyskać jeden z 9 wariantów łączenia. Złączka umożliwia: klasyczne łączenie taśmy z taśmą, taśmy z przewodem zasilającym, tworzenie kątów 90 stopni (L), zasilanie z boku, oraz połączenia rozgałęźne typu T. Instalacja wymaga jedynie zaciśnięcia pinów kombinerkami, co znacznie ułatwia montaż długich obwodów świetlnych w trudno dostępnych miejscach.
  </p>
</section>
{BLOG_ZLĄCZKI}"""

zlaczki_skus = ['FC8-MONO-MULTI-9IN1', 'FC10-MONO-MULTI-9IN1', 'FC-COB-RGB', 'FC-SMD-RGBW', 'FC-SMD-RGB']
for sku in zlaczki_skus:
    if "FC8-MONO-MULTI" in sku:
        new_desc = generate_zlaczka_html(sku, "2-pin 8mm (MONO)")
    elif "FC10-MONO-MULTI" in sku:
        new_desc = generate_zlaczka_html(sku, "2-pin 10mm (MONO)")
    elif "COB-RGB" in sku:
        new_desc = generate_zlaczka_html(sku, "3/4-pin 10mm (RGB)")
    elif "SMD-RGBW" in sku:
        new_desc = generate_zlaczka_html(sku, "5-pin 12mm (RGBW)")
    elif "SMD-RGB" in sku:
        new_desc = generate_zlaczka_html(sku, "4-pin 10mm (RGB)")
    master_dict[sku] = new_desc

print("Generated new Złączki")

# 4.5. Remove spaces between numbers and units, remove uppercase, fix LM
for sku in master_dict:
    # Remove text-transform:uppercase from badges
    master_dict[sku] = master_dict[sku].replace('text-transform:uppercase;', '')
    master_dict[sku] = master_dict[sku].replace('TEXT-TRANSFORM:UPPERCASE;', '')
    
    # Fix casing for lm/m, lm/W, lm and remove spaces
    master_dict[sku] = re.sub(r'(?i)(\d+)\s*lm/m\b', r'\1lm/m', master_dict[sku])
    master_dict[sku] = re.sub(r'(?i)(\d+)\s*lm/w\b', r'\1lm/W', master_dict[sku])
    master_dict[sku] = re.sub(r'(?i)(\d+)\s*lm\b', r'\1lm', master_dict[sku])
    
    # 8 mm -> 8mm, 12 V -> 12V, 18 W -> 18W, 12 A -> 12A, 30 m -> 30m
    master_dict[sku] = re.sub(r'(\d+)\s+(mm|V|W|A|m)\b', r'\1\2', master_dict[sku])

# 5. Read index.html and update safely
with open(INDEX_HTML, 'r', encoding='utf-8') as f:
    html_content = f.read()

import vary_seo
import vary_colors
import generate_wapro_unikat

excel_export_dict = {}

try:
    df_temp = pd.read_excel(EXCEL_FILE)
    sku_to_nazwa = dict(zip(df_temp['INDEKS_HANDLOWY'].astype(str).str.strip(), df_temp['NAZWA_CALA'].astype(str)))
    sku_to_kat = dict(zip(df_temp['INDEKS_HANDLOWY'].astype(str).str.strip(), df_temp['KATEGORIA_WIELOPOZIOMOWA'].astype(str)))
except Exception as e:
    print("Error reading Excel for names:", e)
    sku_to_nazwa = {}
    sku_to_kat = {}

def inject_safely(html_str):
    updated = 0
    for sku, original_content in master_dict.items():
        nazwa_cala = sku_to_nazwa.get(sku, "")
        kategoria = sku_to_kat.get(sku, "")
        for tab in ['wapro', 'tim', 'allegro']:
            if tab == 'tim':
                platform_content = generate_wapro_unikat.generate_wapro_html(original_content, sku, nazwa_cala, kategoria, seed_suffix='_tim')
                platform_content = vary_seo.vary_text(platform_content, 'tim')
                platform_content = vary_colors.randomize_color_blocks(platform_content)
            elif tab == 'allegro':
                platform_content = generate_wapro_unikat.generate_wapro_html(original_content, sku, nazwa_cala, kategoria, seed_suffix='_allegro')
                platform_content = vary_seo.vary_text(platform_content, 'allegro')
                platform_content = vary_colors.randomize_color_blocks(platform_content)
            else:
                platform_content = generate_wapro_unikat.generate_wapro_html(original_content, sku, nazwa_cala, kategoria, seed_suffix='')
                excel_export_dict[sku] = platform_content  # Save back for Excel export
                
            start_marker = f'<div class="model-block" id="desc-view-{tab}-{sku}">'
            end_marker = f'<div class="edit-block" id="desc-edit-{tab}-{sku}"'
            
            start_idx = html_str.find(start_marker)
            if start_idx != -1:
                end_idx = html_str.find(end_marker, start_idx)
                if end_idx != -1:
                    # Double check we didn't match a prefix by looking at the next character
                    # If it's a quote or space, it's exact. If it's a digit/letter, it's a prefix match.
                    next_char = html_str[end_idx + len(end_marker)]
                    if next_char in ['"', ' ']:
                        # Perform safe injection
                        html_str = html_str[:start_idx + len(start_marker)] + '\n' + platform_content + '\n</div>\n' + html_str[end_idx:]
                        updated += 1
                        
                        # Also update corresponding textarea
                        textarea_id = f'id="textarea-{tab}-{sku}"'
                        ta_start_idx = html_str.find(textarea_id, end_idx)
                        if ta_start_idx != -1:
                            ta_close_bracket = html_str.find('>', ta_start_idx)
                            ta_end_tag = html_str.find('</textarea>', ta_close_bracket)
                            if ta_end_tag != -1:
                                html_str = html_str[:ta_close_bracket + 1] + '\n' + platform_content + '\n' + html_str[ta_end_tag:]
    print(f"Injected {updated} blocks into HTML.")
    return html_str

new_html = inject_safely(html_content)

with open(INDEX_HTML, 'w', encoding='utf-8') as f:
    f.write(new_html)

# 6. Overwrite Excel file
try:
    df = pd.read_excel(EXCEL_FILE)
    updated_excel = 0
    for idx, row in df.iterrows():
        sku = str(row['INDEKS_HANDLOWY']).strip()
        if sku in excel_export_dict:
            df.at[idx, 'Opis'] = excel_export_dict[sku]
            updated_excel += 1

    df.to_excel(EXCEL_FILE, index=False)
    print(f"Updated {updated_excel} SKUs in Excel.")
except Exception as e:
    print("Error processing Excel:", e)
