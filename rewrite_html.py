from bs4 import BeautifulSoup
import re

INDEX_FILE = "/Users/karolbohdanowicz/my-ai-agents/prescot/index.html"

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

zlaczki_dict = {
    "FC8-MONO-MULTI-9IN1": ["2-pin 8mm", "Model 8mm 2-pin przeznaczony do jednokolorowych taśm LED o szerokości laminatu 8mm. Pełna kompatybilność zarówno z najnowszymi taśmami COB (jednolita linia światła) jak i standardowymi taśmami SMD."],
    "FC10-MONO-MULTI-9IN1": ["2-pin 10mm", "Model 10mm 2-pin przeznaczony do jednokolorowych taśm LED o szerokości laminatu 10mm. Pełna kompatybilność zarówno z najnowszymi taśmami COB (jednolita linia światła) jak i standardowymi taśmami SMD."],
}

with open(INDEX_FILE, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

# Find all items that are zlaczki
for div in soup.find_all('div', id=re.compile(r'^desc-view-wapro-FC.*')):
    sku = div['id'].replace('desc-view-wapro-', '')
    
    new_desc = None
    if "FC8-MONO-MULTI" in sku:
        new_desc = generate_zlaczka_html(sku, "2-pin 8mm", zlaczki_dict.get("FC8-MONO-MULTI-9IN1", ["", "Pełna kompatybilność zarówno z najnowszymi taśmami COB (jednolita linia światła) jak i standardowymi taśmami SMD."])[1])
    elif "FC10-MONO-MULTI" in sku:
        new_desc = generate_zlaczka_html(sku, "2-pin 10mm", zlaczki_dict.get("FC10-MONO-MULTI-9IN1", ["", "Pełna kompatybilność zarówno z najnowszymi taśmami COB (jednolita linia światła) jak i standardowymi taśmami SMD."])[1])
    elif "COB-RGB" in sku:
        new_desc = generate_zlaczka_html(sku, "3-pin/4-pin RGB", "Zaprojektowana dla taśm wielokolorowych RGB. Kompatybilna z taśmami COB oraz SMD.")
    elif "SMD-RGBW" in sku:
        new_desc = generate_zlaczka_html(sku, "5-pin RGBW", "Zaprojektowana dla taśm wielokolorowych RGBW (z dodatkowym białym kanałem). Kompatybilna z taśmami SMD.")
    elif "SMD-RGB" in sku:
        new_desc = generate_zlaczka_html(sku, "4-pin RGB", "Zaprojektowana dla taśm wielokolorowych RGB. Kompatybilna z taśmami SMD.")
    elif "FC" in sku:
        new_desc = generate_zlaczka_html(sku, sku.replace("FC10-", "").replace("FC8-", ""), "Dostosowana do precyzyjnego łączenia wybranego typu taśmy LED, obsługuje zarówno układy COB jak i SMD, o ile odpowiada ilości pinów i szerokości.")
        
    if new_desc:
        div.clear()
        div.append(BeautifulSoup(new_desc, 'html.parser'))

with open(INDEX_FILE, 'w', encoding='utf-8') as f:
    f.write(str(soup))
print("Zlaczki updated in HTML.")
