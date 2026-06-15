import re
import pandas as pd

USER_V2_FILE = "/Users/karolbohdanowicz/Downloads/opisy KAROL v2.html"
SCHARFER_TEXT = "/Users/karolbohdanowicz/Downloads/TOP Scharfer - OSTATECZNY.txt"
INDEX_HTML = "/Users/karolbohdanowicz/my-ai-agents/prescot/test_index.html"
EXCEL_FILE = "/Users/karolbohdanowicz/Desktop/EksportowaneArtykuly.xlsx"

master_dict = {}

# 1. Parse user's v2 HTML
with open(USER_V2_FILE, "r", encoding="utf-8") as f:
    v2_content = f.read()

v2_blocks = re.findall(r'<!-- START ([^ ]+) -->(.*?)<!-- KONIEC \1 -->', v2_content, re.DOTALL)
for sku, html in v2_blocks:
    master_dict[sku] = html.strip()
print(f"Extracted {len(v2_blocks)} blocks from v2 HTML")

# 2. Parse Scharfer
with open(SCHARFER_TEXT, "r", encoding="utf-8") as f:
    scharfer_content = f.read()

scharfer_blocks = re.findall(r'START (SCH-[^\n]+)(.*?)KONIEC \1', scharfer_content, re.DOTALL)
for sku, html in scharfer_blocks:
    sku = sku.strip()
    master_dict[sku] = html.strip()
print(f"Extracted {len(scharfer_blocks)} Scharfer blocks")

# 3. Generate Sterowniki with user's new feedback
sterowniki_skus = ['PR-MONO-12A', 'PR-CCT-12A', 'PR-RGB-12A', 'PR-RGBW-12A', 'PR-RGBCCT-12A']

for sku in sterowniki_skus:
    nazwa = sku.replace("PR-", "").replace("-12A", "")
    
    if nazwa == "MONO":
        funkcje_opis = "Pozwala na sterowanie taśmami jednokolorowymi (MONO). Możesz płynnie ściemniać i rozjaśniać światło (od 1% do 100%), dopasowując je do pory dnia czy nastroju, bez efektu migotania."
    elif nazwa == "CCT":
        funkcje_opis = "Stworzony do taśm ze zmienną barwą bieli (CCT). Możesz w dowolnej chwili płynnie przejść od ciepłego, relaksującego światła do zimnej bieli idealnej do pracy, niezależnie regulując przy tym jasność."
    elif nazwa == "RGB":
        funkcje_opis = "Przeznaczony do wielokolorowych taśm RGB. Pozwala na wybór dowolnej barwy z palety 16 milionów kolorów, umożliwiając tworzenie dynamicznych aranżacji, podświetleń nastrojowych czy gamingowych."
    elif nazwa == "RGBW":
        funkcje_opis = "Obsługuje taśmy wielokolorowe z dodatkową diodą białą (RGBW). Dzięki temu zyskujesz pełny wybór 16 milionów kolorów do dekoracji oraz czyste, jasne światło białe do codziennych zadań."
    elif nazwa == "RGBCCT":
        funkcje_opis = "Najbardziej zaawansowany model obsługujący wszystkie typy taśm. Oprócz palety 16 milionów kolorów RGB daje pełną kontrolę nad temperaturą barwową światła białego (od bardzo ciepłego po zimne)."

    blog_sterowniki = """<section style="font-family:inherit; margin:18px 0 28px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <div style="font-family:inherit; margin-bottom:18px; background:none !important; background-color:transparent !important; color:inherit;">
    <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
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
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Sterownik LED Prescot {nazwa}</font>
  </span>
  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Odbiornik radiowy do bezprzewodowego sterowania oświetleniem
  </h3>
  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    Sterownik <strong style="font-family:inherit; color:inherit !important;">{sku}</strong> to element systemu Prescot pozwalający na łatwe i bezprzewodowe zarządzanie oświetleniem w standardzie <strong style="font-family:inherit; color:inherit !important;">RF 2.4GHz</strong>. {funkcje_opis} Możesz połączyć go z kilkoma nadajnikami (np. jednym pilotem wielostrefowym i oddzielnym panelem naściennym). A po sparowaniu z mostkiem WiFi zyskujesz pełną obsługę z aplikacji w smartfonie oraz integrację ze Smart Home (m.in. Amazon Alexa, Google Assistant).
  </p>
</section>
<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Funkcje ułatwiające codzienne użytkowanie</font>
  </span>
  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Stabilny zasięg do 30m i funkcja "Nie przeszkadzać"
  </h3>
  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    Urządzenie wyposażono w funkcję <strong style="font-family:inherit; color:inherit !important;">auto-retransmisji i synchronizacji</strong> – sygnał jest automatycznie podawany dalej z jednego odbiornika do drugiego (jeśli znajdują się w promieniu do 30 metrów od siebie), dzięki czemu zasięg systemu staje się praktycznie nieograniczony, a oświetlenie we wszystkich strefach działa równo. Dodatkową przydatną funkcją jest tryb <strong style="font-family:inherit; color:inherit !important;">"Nie przeszkadzać"</strong> – po przerwie w dostawie prądu oświetlenie pozostaje zgaszone, żeby nie obudzić domowników w środku nocy. Napięcie wejściowe wynosi DC 5-24V. Maksymalne łączne obciążenie to 12A (dla 12V obsłuży moce do 144W, dla 24V do 288W). Niewielki rozmiar (74.5 x 35.6 x 16.5 mm) ułatwia dyskretny montaż w zabudowie czy tuż obok zasilacza.
  </p>
</section>
{blog_sterowniki}"""
    master_dict[sku] = new_html

print("Generated new Sterowniki")

# 4. Generate Złączki
zlaczki_dict = {
    "FC8-MONO-MULTI-9IN1": ["2-pin 8mm", "Model 8mm 2-pin przeznaczony do jednokolorowych taśm LED o szerokości laminatu 8mm. Pasuje idealnie do nowych, gęstych taśm COB (gdzie tworzy niewidoczne łączenie bez przerw w świetle) oraz do klasycznych taśm SMD."],
    "FC10-MONO-MULTI-9IN1": ["2-pin 10mm", "Model 10mm 2-pin przeznaczony do jednokolorowych taśm LED o szerokości laminatu 10mm. Gwarantuje pewny docisk przy taśmach COB oraz tradycyjnych taśmach SMD."],
}

BLOG_ZLĄCZKI = """<section style="font-family:inherit; margin:0; padding:0; background:none !important; background-color:transparent !important; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
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

def generate_zlaczka_html(model, nazwa, opis_stykow):
    return f"""<section style="font-family:inherit; margin:28px 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Złączka zaciskowa LED 9w1 - {nazwa}</font>
  </span>
  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Niezawodne połączenie bez lutowania dla taśm COB i SMD
  </h3>
  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    Złączka <strong style="font-family:inherit; color:inherit !important;">{model}</strong> (typu 9w1) to wygodne narzędzie instalacyjne eliminujące potrzebę używania lutownicy. Posiada całkowicie transparentną obudowę, która w przeciwieństwie do starszych białych modeli nie rzuca ciemnego cienia w profilu i nie zasłania diod. Charakteryzuje się bardzo smukłym profilem, przez co łatwo wchodzi w większość standardowych korytek aluminiowych. {opis_stykow}
  </p>
</section>
<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Gdzie użyć i jak łączyć</font>
  </span>
  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Jedna złączka - 9 sposobów połączenia
  </h3>
  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    Specjalnie zaprojektowany system pinów sprawia, że jedna złączka potrafi obsłużyć do 9 różnych wariantów łączenia: od prostego połączenia <strong style="font-family:inherit; color:inherit !important;">przewód z taśmą</strong> czy <strong style="font-family:inherit; color:inherit !important;">taśma z taśmą</strong>, przez zasilania narożne "L" i boczne "T", po łączenie krzyżowe zasilania. Wewnątrz umieszczono ostre, dociskowe piny, które przebijają laminat po włożeniu przewodu lub taśmy. Zacisk dokonywany jest kombinerkami lub ręcznie. Rozwiązanie to drastycznie skraca czas montażu długich obwodów świetlnych.
  </p>
</section>
{BLOG_ZLĄCZKI}"""

# Generate Zlaczki for known SKUs
zlaczki_skus = ['FC8-MONO-MULTI-9IN1', 'FC10-MONO-MULTI-9IN1', 'FC-COB-RGB', 'FC-SMD-RGBW', 'FC-SMD-RGB']
for sku in zlaczki_skus:
    if "FC8-MONO-MULTI" in sku:
        new_desc = generate_zlaczka_html(sku, "2-pin 8mm", zlaczki_dict.get("FC8-MONO-MULTI-9IN1", ["", ""])[1])
    elif "FC10-MONO-MULTI" in sku:
        new_desc = generate_zlaczka_html(sku, "2-pin 10mm", zlaczki_dict.get("FC10-MONO-MULTI-9IN1", ["", ""])[1])
    elif "COB-RGB" in sku:
        new_desc = generate_zlaczka_html(sku, "3-pin/4-pin RGB", "Zaprojektowana specjalnie dla taśm wielokolorowych RGB. Działa prawidłowo zarówno z gładkimi taśmami COB, jak i SMD.")
    elif "SMD-RGBW" in sku:
        new_desc = generate_zlaczka_html(sku, "5-pin RGBW", "Dedykowana do taśm wielokolorowych z dodatkowym kanałem białym RGBW. Przeznaczona do taśm SMD.")
    elif "SMD-RGB" in sku:
        new_desc = generate_zlaczka_html(sku, "4-pin RGB", "Zaprojektowana dla standardowych taśm wielokolorowych RGB w technologii SMD.")
    
    master_dict[sku] = new_desc

print("Generated new Złączki")

# 5. We now have a full dictionary of correct HTML in master_dict.
# Update index.html
with open(INDEX_HTML, 'r', encoding='utf-8') as f:
    html_content = f.read()

# For every platform (tim, allegro, wapro, etc.), find <div class="model-block" id="desc-view-<platform>-<sku>"> and replace its content
for sku, content in master_dict.items():
    # Regex to find desc-view-(platform)-sku
    pattern = r'(<div class="model-block" id="desc-view-[^-]+-' + re.escape(sku) + r'">).*?(</div>\s*<!--|<div class="model-block"|<div class="edit-block")'
    
    def repl(m):
        prefix = m.group(1)
        suffix = m.group(2)
        # return the prefix, the new content, and then the end tags (which might be <div class="edit-block" or </div><!-- etc)
        # To be safe and clean, we'll just put \n content \n suffix
        # But wait, suffix might contain </div> which actually BELONGS to the model-block or another div.
        return f"{prefix}\n{content}\n</div>\n{suffix}" if 'edit-block' in suffix else f"{prefix}\n{content}\n{suffix}"
    
    # Actually, simpler: regex to replace everything inside desc-view-(platform)-(sku) until its corresponding closing div.
    # Since index.html has a flat inner structure for these blocks initially:
    pattern = r'(<div class="model-block" id="desc-view-[a-z]+-' + re.escape(sku) + r'">)[\s\S]*?(?=</div>\s*<!--\s*KONIEC|<div class="edit-block")'
    # Actually, edit-block is inside model-block usually? No, edit-block is adjacent to model-block in my index.html structure!
    # Let's check index.html structure!
    # <div class="model-block" id="desc-view-tim-A01587A_1">...</div>
    # <div class="edit-block" id="desc-edit-tim-A01587A_1" ...>

    # So replacing from <div class="model-block" id="..."> to the very next </div> should be perfectly safe, provided the inner HTML has perfectly matching <div>s. 
    # But inner HTML doesn't have bare <div>s! It only has <section>, <span>, <div>... wait, the blogs use <div>!
    pass

# A simpler way to update index.html safely:
for sku, content in master_dict.items():
    # The id is desc-view-<tab>-<sku>
    # There are three tabs: wapro, tim, allegro
    for tab in ['wapro', 'tim', 'allegro']:
        id_str = f'desc-view-{tab}-{sku}'
        # We find exactly <div class="model-block" id="id_str"> and the NEXT <div class="edit-block"
        start_marker = f'<div class="model-block" id="{id_str}">'
        end_marker = f'<div class="edit-block" id="desc-edit-{tab}-{sku}"'
        
        start_idx = html_content.find(start_marker)
        if start_idx != -1:
            # Found it! Look for the end marker
            end_idx = html_content.find(end_marker, start_idx)
            if end_idx != -1:
                # Replace everything between start_marker and end_idx
                # Note: there is a closing </div> before edit-block that belongs to model-block!
                html_content = html_content[:start_idx + len(start_marker)] + '\n' + content + '\n</div>\n' + html_content[end_idx:]

with open(INDEX_HTML, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Updated index.html with {len(master_dict)} items.")

# 6. Overwrite Excel file
df = pd.read_excel(EXCEL_FILE)
updated_excel = 0
for idx, row in df.iterrows():
    sku = str(row['INDEKS_HANDLOWY']).strip()
    if sku in master_dict:
        df.at[idx, 'Opis'] = master_dict[sku]
        updated_excel += 1

df.to_excel(EXCEL_FILE, index=False)
print(f"Updated {updated_excel} SKUs in Excel.")
