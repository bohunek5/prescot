import re
import pandas as pd
from bs4 import BeautifulSoup

SCHARFER_FILE = "/Users/karolbohdanowicz/Downloads/TOP Scharfer - OSTATECZNY.txt"
INDEX_FILE = "/Users/karolbohdanowicz/my-ai-agents/prescot/index.html"
EXCEL_FILE = "/Users/karolbohdanowicz/Desktop/EksportowaneArtykuly.xlsx"

# 1. Parse Scharfer gotowce
scharfer_gotowce = {}
with open(SCHARFER_FILE, 'r', encoding='utf-8') as f:
    content = f.read()
    # Find all START {sku} ... KONIEC {sku}
    matches = re.finditer(r'START\s+(SCH-[^\n]+)\n(.*?)\nKONIEC\s+\1', content, re.DOTALL)
    for match in matches:
        sku = match.group(1).strip()
        html = match.group(2).strip()
        scharfer_gotowce[sku] = html

# 2. Define Blog templates
BLOG_ZASILACZE = """
<section style="font-family:inherit; margin:0; padding:0; background:none !important; background-color:transparent !important; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Praktyczne poradniki</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Dobierz zasilacz LED bez zgadywania
  </h3>

  <p style="font-family:inherit; margin:0 0 16px 0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.78; font-size:14px; line-height:1.6;">
    Poradniki pomagają policzyć moc, dobrać typ obudowy, napięcie i stopień ochrony IP do konkretnej instalacji.
  </p>

  <div style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit; align-items:stretch;">
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać zasilacz LED do taśmy?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">moc W/m, długość taśmy i zapas mocy</small>
      <a href="https://www.prescot.com.pl/pl/n/24" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Stopnie IP - dlaczego to ważne?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">IP20, IP33, IP44 i <strong style="font-family:inherit; color:inherit !important;">IP67</strong> w praktyce</small>
      <a href="https://www.prescot.com.pl/pl/n/27" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
  </div>
</section>
"""

BLOG_ZLĄCZKI = """
<section style="font-family:inherit; margin:0; padding:0; background:none !important; background-color:transparent !important; color:inherit;">
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
</section>
"""

BLOG_STEROWNIKI = """
<section style="font-family:inherit; margin:0; padding:0; background:none !important; background-color:transparent !important; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Praktyczne poradniki</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Inteligentne sterowanie oświetleniem
  </h3>

  <p style="font-family:inherit; margin:0 0 16px 0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.78; font-size:14px; line-height:1.6;">
    Dowiedz się jak sparować systemy RF 2.4G i wykorzystać pełny potencjał sterowników LED w swoim domu.
  </p>

  <div style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit; align-items:stretch;">
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Konfiguracja sterowania</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">parowanie stref, retransmisja sygnału</small>
      <a href="https://www.prescot.com.pl/pl/n/21" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Sterowanie aplikacją i głosem</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">Smart Home, bramki WiFi</small>
      <a href="https://www.prescot.com.pl/pl/n/22" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
  </div>
</section>
"""

# HTML Generator Functions
def generate_sterownik_html(model, nazwa, funkcje_opis):
    return f"""<section style="font-family:inherit; margin:28px 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Sterownik LED Prescot {nazwa}</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Inteligentne sterowanie RF 2.4GHz z zaawansowanymi funkcjami
  </h3>

  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    Sterownik <strong style="font-family:inherit; color:inherit !important;">{model}</strong> to nowoczesne urządzenie do obsługi instalacji LED. Pracuje w standardzie <strong style="font-family:inherit; color:inherit !important;">RF 2.4GHz</strong>, oferując zasięg do 30 metrów oraz <strong style="font-family:inherit; color:inherit !important;">auto-retransmisję i synchronizację</strong> (sterownik przekazuje sygnał do kolejnego w zasięgu 30m, co czyni zasięg niemal nieograniczonym). {funkcje_opis}
  </p>
</section>

<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Funkcje i parametry</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Tryb "Nie przeszkadzać" i wysoka wydajność prądowa
  </h3>

  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    Urządzenie wyposażono w funkcję <strong style="font-family:inherit; color:inherit !important;">"Nie przeszkadzać"</strong> (po zaniku zasilania światła pozostają wyłączone w nocy) oraz przełączanie częstotliwości PWM (wysoka/niska), co jest idealne przy nagrywaniu wideo. Napięcie wejściowe i wyjściowe to DC 5-24V. Maksymalne obciążenie wynosi 6A na kanał (łącznie max 12A). Obsługuje złącza zasilania DC 5.5x2.1mm lub zaciski śrubowe. Kompaktowe wymiary (74.5 x 35.6 x 16.5 mm) ułatwiają ukrycie w profilach lub wnękach.
  </p>
</section>

{BLOG_STEROWNIKI}"""

def generate_zlaczka_html(model, nazwa, opis_stykow):
    return f"""<section style="font-family:inherit; margin:28px 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Złączka zaciskowa LED 9w1 - {nazwa}</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Uniwersalne połączenie bez lutowania dla taśm COB i SMD
  </h3>

  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    Złączka <strong style="font-family:inherit; color:inherit !important;">{model}</strong> (9w1) to innowacyjne rozwiązanie, które pozwala na błyskawiczny montaż bez konieczności lutowania. Dzięki transparentnej obudowie (brak ciemnych obszarów) nie zaburza emisji światła. Jest to niezwykle smukły element, który z łatwością mieści się w standardowych profilach aluminiowych LED. {opis_stykow}
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
    Dzięki specjalnej budowie złączy pinowych, jedna złączka umożliwia aż 9 typów połączeń: <strong style="font-family:inherit; color:inherit !important;">przewód z taśmą, taśma z taśmą, przewód z przewodem</strong> oraz zaawansowane łączenia: <strong style="font-family:inherit; color:inherit !important;">zasilanie narożne "L", taśma w kształcie "L", zasilanie boczne "T", taśma z taśmą w kształcie "T", czy zasilanie "X"</strong>. Wystarczy wyrównać biegunowość, włożyć taśmę i/lub przewód do środka, a następnie zacisnąć każdy pin pionowo. Idealnie sprawdza się w wąskich przestrzeniach oraz przy montażu ciągów liniowych z taśm COB i SMD.
  </p>
</section>

{BLOG_ZLĄCZKI}"""


# Data dictionaries for specific product logic
sterowniki_dict = {
    "PR-MONO-12A": ["MONO", "Umożliwia płynną regulację jasności taśm jednokolorowych (DIM) od 1% do 100%."],
    "PR-CCT-12A": ["CCT (Dual White)", "Umożliwia płynną regulację jasności oraz zmiany barwy światła od ciepłej bieli do zimnej (CCT)."],
    "PR-RGB-12A": ["RGB", "Umożliwia płynną regulację jasności oraz wybór spośród 16 milionów kolorów z palety RGB."],
    "PR-RGBW-12A": ["RGBW", "Umożliwia płynną regulację kolorów z palety RGB, a także osobną kontrolę białego kanału światła."],
    "PR-RGBCCT-12A": ["RGBCCT", "Najbardziej zaawansowany model, obsługuje pełne spektrum kolorów RGB oraz pełen zakres bieli (ciepła-zimna)."]
}

zlaczki_dict = {
    "FC8-MONO-MULTI-9IN1": ["2-pin 8mm", "Model 8mm 2-pin przeznaczony do jednokolorowych taśm LED o szerokości laminatu 8mm. Pełna kompatybilność zarówno z najnowszymi taśmami COB (jednolita linia światła) jak i standardowymi taśmami SMD."],
    "FC10-MONO-MULTI-9IN1": ["2-pin 10mm", "Model 10mm 2-pin przeznaczony do jednokolorowych taśm LED o szerokości laminatu 10mm. Pełna kompatybilność zarówno z najnowszymi taśmami COB (jednolita linia światła) jak i standardowymi taśmami SMD."],
    # In case there are older złączki matching the 9w1 logic without 9in1 name
}


def process_description(title, sku):
    # If Scharfer
    if "scharfer" in title.lower() and sku in scharfer_gotowce:
        # Use exact gotowiec text (without START/KONIEC)
        return scharfer_gotowce[sku]
    
    # If Zasilacz ale nie Scharfer (fallback, but user only complained about Scharfer, Sterowniki, Zlaczki)
    if "scharfer" in title.lower():
        # Maybe SKU mismatch?
        pass

    # If Sterownik
    if sku in sterowniki_dict:
        return generate_sterownik_html(sku, sterowniki_dict[sku][0], sterowniki_dict[sku][1])

    # If Złączka
    if "9IN1" in sku or "zlaczka" in title.lower() or "złączka" in title.lower():
        # Extract features
        if "FC8-MONO-MULTI" in sku:
            return generate_zlaczka_html(sku, "2-pin 8mm", zlaczki_dict["FC8-MONO-MULTI-9IN1"][1])
        elif "FC10-MONO-MULTI" in sku:
            return generate_zlaczka_html(sku, "2-pin 10mm", zlaczki_dict["FC10-MONO-MULTI-9IN1"][1])
        elif "COB-RGB" in sku:
            return generate_zlaczka_html(sku, "3-pin/4-pin RGB", "Zaprojektowana dla taśm wielokolorowych RGB. Kompatybilna z taśmami COB oraz SMD.")
        elif "SMD-RGBW" in sku:
            return generate_zlaczka_html(sku, "5-pin RGBW", "Zaprojektowana dla taśm wielokolorowych RGBW (z dodatkowym białym kanałem). Kompatybilna z taśmami SMD.")
        elif "SMD-RGB" in sku:
            return generate_zlaczka_html(sku, "4-pin RGB", "Zaprojektowana dla taśm wielokolorowych RGB. Kompatybilna z taśmami SMD.")
        else:
            return generate_zlaczka_html(sku, sku.replace("FC10-", "").replace("FC8-", ""), "Dostosowana do precyzyjnego łączenia wybranego typu taśmy LED, obsługuje zarówno układy COB jak i SMD, o ile odpowiada ilości pinów i szerokości.")

    return None

# Read HTML file
with open(INDEX_FILE, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

df = pd.read_excel(EXCEL_FILE)

# Process Excel and HTML
for index, row in df.iterrows():
    sku = str(row['INDEKS_HANDLOWY']).strip()
    nazwa = str(row['NAZWA_CALA']).strip()
    
    new_desc = process_description(nazwa, sku)
    
    if new_desc:
        # Update Excel
        df.at[index, 'Opis'] = new_desc
        
        # Update HTML
        # Find element by ID (e.g. desc-view-wapro-SCH-18-12)
        div_id = f"desc-view-wapro-{sku}"
        div_elem = soup.find(id=div_id)
        if div_elem:
            # Replace inner html
            div_elem.clear()
            # We parse the new_desc as HTML and insert it
            new_soup = BeautifulSoup(new_desc, 'html.parser')
            div_elem.append(new_soup)

# Save Excel
df.to_excel(EXCEL_FILE, index=False)

# Save HTML
with open(INDEX_FILE, 'w', encoding='utf-8') as f:
    f.write(str(soup))

print("Rewritten successfully.")
