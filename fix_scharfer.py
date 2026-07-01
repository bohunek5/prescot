import re
from bs4 import BeautifulSoup

with open('index.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

with open('broken_index.html', 'r', encoding='utf-8') as f:
    broken_soup = BeautifulSoup(f.read(), 'html.parser')

dim_map = {}
for view_div in broken_soup.find_all('div', id=lambda x: x and 'desc-view-allegro-SCH-' in x):
    sku = view_div['id'].replace('desc-view-allegro-', '')
    text = view_div.get_text(' ', strip=True)
    wymiar_m = re.search(r'Wymiar[^:]*:\s*([\d\.\sx]+mm)', text, re.IGNORECASE)
    if not wymiar_m:
        wymiar_m = re.search(r'([\d\.\s]+x[\d\.\s]+x[\d\.\s]+mm)', text, re.IGNORECASE)
    dim_map[sku] = wymiar_m.group(1).strip() if wymiar_m else 'Brak'

scharfer_skus = list(set(div['id'].replace('desc-view-allegro-', '') for div in soup.find_all('div', id=lambda x: x and 'desc-view-allegro-SCH-' in x)))

def get_tier_text(power, voltage, sku):
    if power <= 30:
        return {
            'h3_1': f"Stabilne zasilanie {voltage}V do małych i punktowych instalacji LED",
            'p_1': f"Scharfer {sku} to zasilacz LED DC o mocy <b>{power}W</b>, przeznaczony do instalacji pracujących na napięciu <b>{voltage}V</b>. Model wyróżnia się kompaktowym formatem do dyskretnych instalacji. Zapewnia stabilne napięcie wyjściowe dla taśm LED i podświetleń dekoracyjnych. Konstrukcja pozwala stosować go w ograniczonych przestrzeniach.",
            'h3_2': "Do krótkich odcinków taśm LED, podświetleń półek i małych liter reklamowych",
            'p_2': f"Ten wariant wybierz wtedy, gdy potrzebujesz zasilacza <b>{voltage}V</b> do instalacji LED o łącznej mocy mieszczącej się w limicie <b>{power}W</b>. Sprawdzi się idealnie przy meblach, wnękach czy dekoracyjnym oświetleniu akcentowym."
        }
    elif power <= 60:
        return {
            'h3_1': f"Stabilne zasilanie {voltage}V do domowych i meblowych instalacji LED",
            'p_1': f"Scharfer {sku} to wydajny zasilacz LED DC o mocy <b>{power}W</b>, przeznaczony do instalacji pracujących na napięciu <b>{voltage}V</b>. Model zapewnia ciągłe zasilanie bez migotania, idealne do zabudowy sufitowej, kuchennej oraz łazienkowej.",
            'h3_2': "Do sufitów podwieszanych, blatów i oświetlenia ciągłego",
            'p_2': f"Ten wariant wybierz, gdy instalujesz oświetlenie na napięciu <b>{voltage}V</b> o łącznej mocy nieprzekraczającej <b>{power}W</b>. Niewielki rozmiar ułatwia schowanie urządzenia za płytą GK czy w szafce."
        }
    elif power <= 200:
        return {
            'h3_1': f"Niezawodne zasilanie {voltage}V do większych instalacji świetlnych",
            'p_1': f"Scharfer {sku} to profesjonalny zasilacz LED DC o mocy <b>{power}W</b>, przeznaczony do ciągłej pracy przy napięciu <b>{voltage}V</b>. Zapewnia doskonałą stabilność, pozwalając na podłączenie długich odcinków taśm świetlnych bez spadku jakości świecenia.",
            'h3_2': "Do całych pomieszczeń, salonów, biur i oświetlenia architektonicznego",
            'p_2': f"Ten zasilacz będzie idealny dla systemów oświetleniowych <b>{voltage}V</b> wymagających łącznie do <b>{power}W</b> mocy. Dzięki dużej sprawności idealnie nadaje się do ciągów LED, w których wymagane jest pewne i ciągłe obciążenie."
        }
    else:
        return {
            'h3_1': f"Przemysłowa moc {power}W ({voltage}V) do bezkompromisowych instalacji",
            'p_1': f"Scharfer {sku} to flagowy zasilacz dużej mocy (<b>{power}W</b>) dla instalacji <b>{voltage}V</b>. Skonstruowany do pracy w najbardziej wymagających warunkach i na długich dystansach oświetleniowych. Zapewnia odpowiednią rezerwę energetyczną do utrzymania potężnych obwodów.",
            'h3_2': "Do oświetlenia elewacji, długich korytarzy, hoteli i wielkich instalacji",
            'p_2': f"Wybierz ten model dla instalacji <b>{voltage}V</b> pobierających do <b>{power}W</b>. Sprawdzi się tam, gdzie potrzeba jednego, mocnego serca układu oświetleniowego, aby zasilić całą strefę z jednego miejsca."
        }

count = 0
for plat in ['allegro', 'tim', 'wapro']:
    for sku in scharfer_skus:
        view_div = soup.find('div', id=f'desc-view-{plat}-{sku}')
        if not view_div: continue
        
        # Parse params
        power_m = re.search(r'(\d+)W', sku)
        if not power_m:
            power_m = re.search(r'-(\d+)-', sku)
        power = int(power_m.group(1)) if power_m else 0
        voltage = 24 if '24' in sku.split('-')[-1] else 12
        prad = round(power / voltage, 2)
        wymiar = dim_map.get(sku, 'Brak')
        
        tier = get_tier_text(power, voltage, sku)
        
        # Create block HTML
        block_html = f'''
<section style="font-family: inherit; margin: 28px 0 18px 0; padding: 22px 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
  <span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;">
    <span style="color: #ffffff;">Zasilacz LED Scharfer {voltage}V</span>
  </span>
  <h3 style="font-family: inherit; margin: 0 0 8px 0; background: none !important; background-color: transparent !important; color: inherit !important; font-size: 22px; line-height: 1.3; font-weight: bold;">{tier["h3_1"]}</h3>
  <p style="font-family: inherit; margin: 0; background: none !important; background-color: transparent !important; color: inherit !important; opacity: .82; font-size: 14px; line-height: 1.65;">{tier["p_1"]}</p>
</section>

<section style="font-family: inherit; margin: 0 0 18px 0; padding: 22px 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
  <span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;">
    <span style="color: #ffffff;">Gdzie użyć</span>
  </span>
  <h3 style="font-family: inherit; margin: 0 0 8px 0; background: none !important; background-color: transparent !important; color: inherit !important; font-size: 22px; line-height: 1.3; font-weight: bold;">{tier["h3_2"]}</h3>
  <p style="font-family: inherit; margin: 0; background: none !important; background-color: transparent !important; color: inherit !important; opacity: .82; font-size: 14px; line-height: 1.65;">{tier["p_2"]}</p>
</section>

<section style="font-family: inherit; margin: 0 0 28px 0; padding: 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
  <span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;">
    <span style="color: #ffffff;">Parametry modelu {sku}</span>
  </span>
  <div style="font-family: inherit; display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; background: none !important; background-color: transparent !important; color: inherit;">
    <div style="font-family: inherit; padding: 16px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit;">
      <strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Moc wyjściowa</strong>
      <small style="font-family: inherit; display: block; color: inherit !important; opacity: .78; font-size: 13px; line-height: 1.45;">
        <strong style="font-family: inherit; color: inherit !important;">{power}W</strong>
      </small>
    </div>
    <div style="font-family: inherit; padding: 16px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit;">
      <strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Wyjście DC</strong>
      <small style="font-family: inherit; display: block; color: inherit !important; opacity: .78; font-size: 13px; line-height: 1.45;">
        <strong style="font-family: inherit; color: inherit !important;">{voltage}V DC</strong> / {prad}A
      </small>
    </div>
    <div style="font-family: inherit; padding: 16px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit;">
      <strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Wymiar</strong>
      <small style="font-family: inherit; display: block; color: inherit !important; opacity: .78; font-size: 13px; line-height: 1.45;">{wymiar}</small>
    </div>
    <div style="font-family: inherit; padding: 16px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit;">
      <strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Pełne obciążenie</strong>
      <small style="font-family: inherit; display: block; color: inherit !important; opacity: .78; font-size: 13px; line-height: 1.45;">Możliwość pracy przy <strong style="font-family: inherit; color: inherit !important;">100% obciążenia</strong></small>
    </div>
    <div style="font-family: inherit; padding: 16px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit;">
      <strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Napięcie wejściowe</strong>
      <small style="font-family: inherit; display: block; color: inherit !important; opacity: .78; font-size: 13px; line-height: 1.45;">
        <strong style="font-family: inherit; color: inherit !important;">100-240V AC</strong>
      </small>
    </div>
  </div>
  <p style="font-family: inherit; margin: 16px 0 0 0; background: none !important; background-color: transparent !important; color: inherit !important; opacity: .82; font-size: 14px; line-height: 1.65;">
    Najważniejsze cechy serii: stabilne napięcie wyjściowe, wysoka wydajność transferu, praca przy <strong style="font-family: inherit; color: inherit !important;">100% obciążenia</strong>, zabezpieczenie przed przeciążeniem i zwarciem. Przy planowaniu instalacji dobierz odpowiedni przekrój przewodu do obciążenia i długości prowadzenia, a moc zasilacza dopasuj do łącznej długości oraz poboru taśm LED.
  </p>

  <section style="font-family: inherit; margin: 18px 0 0 0; padding: 22px 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
    <div style="font-family: inherit; margin-bottom: 18px; background: none !important; background-color: transparent !important; color: inherit;">
      <span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;">
        <span style="color: #ffffff;">Praktyczne poradniki</span>
      </span>
      <h3 style="font-family: inherit; margin: 0 0 8px 0; background: none !important; background-color: transparent !important; color: inherit !important; font-size: 22px; line-height: 1.3; font-weight: bold;">Dobierz zasilacz LED bez zgadywania</h3>
      <p style="font-family: inherit; margin: 0; background: none !important; background-color: transparent !important; color: inherit !important; opacity: .78; font-size: 14px; line-height: 1.6;">Sprawdź krótkie poradniki, które pomogą dobrać moc, typ obudowy, napięcie i stopień ochrony IP do konkretnej instalacji LED.</p>
    </div>
    <div style="font-family: inherit; display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; background: none !important; background-color: transparent !important; color: inherit; align-items: stretch;">
      <div style="font-family: inherit; min-height: 190px; padding: 18px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit; display: flex; flex-direction: column;">
        <strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Do czego służą zasilacze LED?</strong>
        <small style="font-family: inherit; display: block; color: inherit !important; opacity: .76; font-size: 12px; line-height: 1.4; margin-bottom: 15px;">taśmy LED, moduły LED i sterowniki</small>
        <a style="font-family: inherit; display: inline-block; min-width: 142px; margin-top: auto; padding: 10px 17px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; text-decoration: none !important; text-align: center; line-height: 1.2; border: 0 !important; align-self: flex-start;" href="https://www.prescot.com.pl/pl/n/26">
          <span style="color: #ffffff;"><span style="font-family: inherit; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; text-decoration: none !important; font-weight: bold; font-size: 14px;">Czytaj poradnik</span></span>
        </a>
      </div>
      <div style="font-family: inherit; min-height: 190px; padding: 18px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit; display: flex; flex-direction: column;">
        <strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Zasilacze LED - gdzie użyć którego?</strong>
        <small style="font-family: inherit; display: block; color: inherit !important; opacity: .76; font-size: 12px; line-height: 1.4; margin-bottom: 15px;">desktop, gniazdkowy, siatkowy, slim i hermetyczny</small>
        <a style="font-family: inherit; display: inline-block; min-width: 142px; margin-top: auto; padding: 10px 17px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; text-decoration: none !important; text-align: center; line-height: 1.2; border: 0 !important; align-self: flex-start;" href="https://www.prescot.com.pl/pl/n/25">
          <span style="color: #ffffff;"><span style="font-family: inherit; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; text-decoration: none !important; font-weight: bold; font-size: 14px;">Czytaj poradnik</span></span>
        </a>
      </div>
      <div style="font-family: inherit; min-height: 190px; padding: 18px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit; display: flex; flex-direction: column;">
        <strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Jak dobrać zasilacz LED do taśmy?</strong>
        <small style="font-family: inherit; display: block; color: inherit !important; opacity: .76; font-size: 12px; line-height: 1.4; margin-bottom: 15px;">moc W/m, długość taśmy i zapas mocy</small>
        <a style="font-family: inherit; display: inline-block; min-width: 142px; margin-top: auto; padding: 10px 17px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; text-decoration: none !important; text-align: center; line-height: 1.2; border: 0 !important; align-self: flex-start;" href="https://www.prescot.com.pl/pl/n/24">
          <span style="color: #ffffff;"><span style="font-family: inherit; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; text-decoration: none !important; font-weight: bold; font-size: 14px;">Czytaj poradnik</span></span>
        </a>
      </div>
      <div style="font-family: inherit; min-height: 190px; padding: 18px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit; display: flex; flex-direction: column;">
        <strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Stopnie IP - dlaczego to ważne?</strong>
        <small style="font-family: inherit; display: block; color: inherit !important; opacity: .76; font-size: 12px; line-height: 1.4; margin-bottom: 15px;">IP20, IP33, IP44 i IP67 w praktyce</small>
        <a style="font-family: inherit; display: inline-block; min-width: 142px; margin-top: auto; padding: 10px 17px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; text-decoration: none !important; text-align: center; line-height: 1.2; border: 0 !important; align-self: flex-start;" href="https://www.prescot.com.pl/pl/n/27">
          <span style="color: #ffffff;"><span style="font-family: inherit; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; text-decoration: none !important; font-weight: bold; font-size: 14px;">Czytaj poradnik</span></span>
        </a>
      </div>
    </div>
  </section>
</section>
'''
        # We need to completely replace the inner contents of view_div with block_html
        new_content = BeautifulSoup(block_html, 'html.parser')
        view_div.clear()
        for child in list(new_content.children):
            view_div.append(child)
        
        count += 1

print(f"Updated {count} Scharfer instances across platforms.")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))
