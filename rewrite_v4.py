import re
import pandas as pd

blog_html = """<section style="font-family:inherit; margin:18px 0 28px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <div style="font-family:inherit; margin-bottom:18px; background:none !important; background-color:transparent !important; color:inherit;">
    <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px;  line-height:1.2;">
    <font color="#ffffff">Praktyczne poradniki</font>
  </span>

    <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
      Dobierz komponenty bez zgadywania
    </h3>

    <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.78; font-size:14px; line-height:1.6;">
      Poradniki prowadzą przez parametry, zasilanie, profile aluminiowe i montaż, czyli decyzje, które naprawdę wpływają na efekt końcowy.
    </p>
  </div>

  <div style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit; align-items:stretch;">
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak czytać parametry taśmy LED?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">moc, lumeny, CRI, napięcie i IP</small>
      <a href="https://www.prescot.com.pl/pl/n/23" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Montaż taśmy LED na zewnątrz</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">IP, uszczelnienie i ochrona połączeń</small>
      <a href="https://www.prescot.com.pl/pl/n/16" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać taśmę LED do mieszkania?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">barwa, moc i miejsce montażu</small>
      <a href="https://www.prescot.com.pl/pl/n/12" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać profil aluminiowy do taśmy LED?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">profil, klosz, chłodzenie i estetyka linii światła</small>
      <a href="https://www.prescot.com.pl/pl/n/15" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
  </div>
</section>"""

def get_sterownik_html(sku):
    typ = "Jednokolorowych (MONO)" if "MONO" in sku else ("CCT (Dual White)" if "CCT" in sku and "RGB" not in sku else ("RGB" if "RGB-" in sku else ("RGBW" if "RGBW" in sku else "RGBCCT")))
    
    # First block: general description
    if "CCT" in sku and "RGB" not in sku:
        opis_ogolny = f"Zaawansowany sterownik radiowy dedykowany do taśm LED {typ}. Pozwala na swobodne zarządzanie temperaturą barwową (od ciepłej do zimnej) oraz jasnością z poziomu jednego pilota. Działa w niezawodnym paśmie bezprzewodowym 2.4GHz RF, co zapewnia bezproblemowy zasięg do 30 metrów w otwartej przestrzeni, bez konieczności celowania pilotem w odbiornik."
    elif "RGB-" in sku:
        opis_ogolny = f"Zaawansowany sterownik radiowy dedykowany do taśm LED {typ}. Oferuje pełną kontrolę nad paletą 16 milionów kolorów, umożliwiając płynną zmianę nasycenia oraz jasności światła. Działa w niezawodnym paśmie bezprzewodowym 2.4GHz RF, co zapewnia bezproblemowy zasięg do 30 metrów w otwartej przestrzeni, bez konieczności celowania pilotem w odbiornik."
    elif "RGBW" in sku:
        opis_ogolny = f"Zaawansowany sterownik radiowy dedykowany do wielokolorowych taśm LED {typ}. Łączy w sobie sterowanie paletą 16 mln kolorów RGB z niezależnym, czystym kanałem białym. Działa w niezawodnym paśmie bezprzewodowym 2.4GHz RF, co zapewnia bezproblemowy zasięg do 30 metrów w otwartej przestrzeni, bez konieczności celowania pilotem w odbiornik."
    elif "RGBCCT" in sku:
        opis_ogolny = f"Najbardziej zaawansowany sterownik radiowy dedykowany do taśm LED {typ}. To urządzenie typu 'wszystko w jednym': pozwala na kontrolę kolorów RGB, regulację temperatury barwy białej CCT oraz płynne ściemnianie. Działa w niezawodnym paśmie bezprzewodowym 2.4GHz RF, co zapewnia bezproblemowy zasięg do 30 metrów w otwartej przestrzeni, bez konieczności celowania pilotem w odbiornik."
    else: # MONO
        opis_ogolny = f"Niezawodny sterownik radiowy (ściemniacz) dedykowany do taśm LED {typ}. Pozwala na precyzyjne, płynne sterowanie jasnością od 1% do 100%, dostosowując oświetlenie do każdej sytuacji. Działa w niezawodnym paśmie bezprzewodowym 2.4GHz RF, co zapewnia bezproblemowy zasięg do 30 metrów w otwartej przestrzeni, bez konieczności celowania pilotem w odbiornik."

    return f"""<section style="font-family:inherit; margin:28px 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Dedykowany do taśm {typ}</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Odbiornik radiowy LED {sku}
  </h3>

  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    {opis_ogolny} Idealne rozwiązanie do zabudowy – odbiornik można bez trudu schować nad sufitem podwieszanym, za meblami czy w rozdzielni.
  </p>
</section>

<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">KONTROLA I FUNKCJE</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 14px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Zaawansowana kontrola i wygoda
  </h3>

  <ul style="font-family:inherit; margin:0; padding-left:20px; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    <li style="margin-bottom:8px;"><b>Wysoka obciążalność:</b> Maksymalne obciążenie wynosi 12A (max 6A na kanał), obsługa napięć z zakresu DC 5-24V.</li>
    <li style="margin-bottom:8px;"><b>Auto-retransmisja sygnału:</b> Odbiornik automatycznie przekazuje sygnał do kolejnego urządzenia w odległości do 30m, pozwalając na budowę nieskończenie długich ciągów oświetleniowych.</li>
    <li style="margin-bottom:8px;"><b>Automatyczna synchronizacja:</b> Wiele odbiorników w jednej strefie pracuje idealnie równo – efekty świetlne i zmiany kolorów następują bez opóźnień.</li>
    <li style="margin-bottom:8px;"><b>Zmienna częstotliwość PWM:</b> Możliwość zmiany częstotliwości chroni przed efektem migotania, co jest kluczowe przy nagrywaniu wideo i zapobiega zmęczeniu wzroku.</li>
    <li style="margin-bottom:0;"><b>Tryb "Nie przeszkadzać" (Do Not Disturb):</b> Inteligentna funkcja blokująca samoistne załączenie się oświetlenia w środku nocy po niespodziewanym zaniku i powrocie zasilania w sieci domowej.</li>
  </ul>
</section>
{blog_html}"""

def get_zlaczka_html(sku):
    szerokosc = "8mm" if "FC8" in sku else "10mm"
    typ = "CCT" if "CCT" in sku else ("RGBW" if "RGBW" in sku else ("RGB" if "RGB" in sku else "MONO"))
    
    kompatybilnosc = "Uniwersalne zastosowanie: doskonale łączy zarówno taśmy COB (linia ciągła), jak i tradycyjne SMD."
    if "-COB-" in sku: kompatybilnosc = "Zaprojektowana specjalnie pod bezpunktowe taśmy COB."
    if "-SMD-" in sku: kompatybilnosc = "Zaprojektowana dla standardowych taśm SMD."
    
    warianty = "Wszechstronna budowa 9w1: łączy taśmę z taśmą, taśmę z przewodem, pozwala na łączenie narożne (L), boczne (T) oraz krzyżowe (X)." if "9IN1" in sku else "Szybkie, stabilne połączenie zaciskowe na piny bez konieczności czasochłonnego lutowania."

    return f"""<section style="font-family:inherit; margin:28px 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Łączenie {typ} {szerokosc}</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Solidny montaż COB i SMD bez lutowania ({sku})
  </h3>

  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    {kompatybilnosc} Złączka oparta jest o system pionowych pinów dociskowych, które przebijają powłokę i gwarantują pewny styk bez przerywania i migotania obwodu. {warianty}
  </p>
</section>

<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Transparentny design do profili</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Brak zaciemnień, idealne do profili LED
  </h3>

  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    Smukła i kompaktowa budowa złączki sprawia, że bez problemu mieści się ona w większości aluminiowych profili LED. Dzięki krystalicznie przezroczystej obudowie światło swobodnie przenika na zewnątrz, całkowicie eliminując nieestetyczny efekt martwych, niedoświetlonych stref w miejscu łączenia.
  </p>
</section>
{blog_html}"""

def get_scharfer_html(sku):
    parts = sku.split('-')
    if len(parts) >= 3:
        w = parts[1]
        v = parts[2]
    else:
        w = "?"
        v = "?"
        
    return f"""<section style="font-family:inherit; margin:28px 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Napięcie {v}V DC | Moc {w}W</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Stabilne zasilanie z obsługą 100% obciążenia ({sku})
  </h3>

  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    Zasilacze z tej serii charakteryzują się bardzo stabilnym napięciem wyjściowym i zdolnością do ciągłej pracy pod pełnym, stuprocentowym obciążeniem. To sprzęt klasy premium dla wymagających instalacji, redukujący migotanie i przedłużający żywotność samych taśm LED. Wbudowane, aktywne zabezpieczenia: przeciwzwarciowe, przeciążeniowe i nadnapięciowe chronią Twój obwód.
  </p>
</section>

<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">IP67 | 7 LAT GWARANCJI</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Szczelny metalowy korpus i legendarna bezawaryjność
  </h3>

  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    Obudowa o klasie wodoszczelności IP67 gwarantuje, że elektronika jest w pełni uodporniona na kurz, zabrudzenia i wilgoć. Dzięki doskonałemu odprowadzaniu ciepła przez zwarty korpus, zasilacze Scharfer objęte są bezkompromisową, 7-letnią gwarancją producenta – to dowód na rzeczywistą trwałość, potwierdzoną certyfikatem CE.
  </p>
</section>
{blog_html}"""

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
