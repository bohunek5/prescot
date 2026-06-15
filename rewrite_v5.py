import re
import pandas as pd
import json

def update_sterownik_html(html_content):
    # We need to find all Sterowniki in index.html and replace them.
    # What are the SKUs for sterowniki?
    sterowniki_skus = ['PR-MONO-12A', 'PR-CCT-12A', 'PR-RGB-12A', 'PR-RGBW-12A', 'PR-RGBCCT-12A']
    
    # We can use the same logic as before to regenerate the sterowniki HTML but with new text
    for sku in sterowniki_skus:
        nazwa = sku.replace("PR-", "").replace("-12A", "")
        
        if nazwa == "MONO":
            funkcje_opis = "Umożliwia płynną regulację jasności taśm jednokolorowych (od 1% do 100%) z zachowaniem idealnej płynności ściemniania."
        elif nazwa == "CCT":
            funkcje_opis = "Pozwala na płynną zmianę temperatury barwowej (od ciepłej, przez neutralną, aż po zimną) oraz regulację jasności z zachowaniem idealnej płynności."
        elif nazwa == "RGB":
            funkcje_opis = "Oferuje wybór spośród 16 milionów kolorów, umożliwiając tworzenie dowolnych aranżacji i dynamicznych efektów świetlnych."
        elif nazwa == "RGBW":
            funkcje_opis = "Oferuje wybór spośród 16 milionów kolorów oraz niezależne sterowanie dodatkową diodą barwy białej, łącząc oświetlenie dekoracyjne z użytkowym."
        elif nazwa == "RGBCCT":
            funkcje_opis = "Najbardziej wszechstronny model. Oferuje 16 milionów kolorów z palety RGB oraz pełną, płynną regulację barwy białej (CCT od ciepłej do zimnej)."

        blog_sterowniki = """<section style="font-family:inherit; margin:18px 0 28px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <div style="font-family:inherit; margin-bottom:18px; background:none !important; background-color:transparent !important; color:inherit;">
    <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Praktyczne poradniki</font>
  </span>
    <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
      Inteligentne sterowanie oświetleniem
    </h3>
    <p style="font-family:inherit; margin:0 0 16px 0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.78; font-size:14px; line-height:1.6;">
      Zobacz, jak zaplanować sterowanie z pilota, telefonu czy głosowo, by wszystkie strefy działały bez zarzutu.
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
    Płynne sterowanie oświetleniem w standardzie RF 2.4GHz
  </h3>
  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    Sterownik <strong>{sku}</strong> umożliwia wygodne zarządzanie instalacją LED. Pracuje w standardzie <strong>RF 2.4GHz</strong> (zasięg do 30 metrów), wspierając <strong>auto-retransmisję i synchronizację</strong> (sterowniki przekazują sygnał między sobą, zwiększając zasięg bezprzewodowo). Możesz nim sterować za pomocą pilotów (1-strefowych lub wielostrefowych), paneli ściennych, a po dodaniu mostka WiFi – także z poziomu smartfona oraz asystentów głosowych (np. Amazon Alexa, Google Assistant). {funkcje_opis}
  </p>
</section>
<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Funkcje ułatwiające codzienne użytkowanie</font>
  </span>
  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    Tryb cichy i zmiana częstotliwości PWM
  </h3>
  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    Urządzenie wyposażono w przydatną funkcję <strong>"Nie przeszkadzać"</strong> – po zaniku prądu, światła pozostają zgaszone, by nie obudzić domowników w nocy. Ponadto pozwala na przełączanie częstotliwości PWM, eliminując efekt migotania przy nagrywaniu wideo. Napięcie wejściowe i wyjściowe to DC 5-24V. Maksymalne obciążenie wynosi 6A na kanał (łącznie max 12A). Kompaktowe wymiary (74.5 x 35.6 x 16.5 mm) ułatwiają ukrycie sterownika w profilach lub wnękach, a montaż upraszcza wybór wtyku DC 5.5x2.1mm lub tradycyjnych zacisków śrubowych.
  </p>
</section>
{blog_sterowniki}"""

        pattern = f'<div class="model-block" id="desc-view-wapro-{sku}">.*?(?=</div>\\n\\n<!--|</div>\\n\\n\\n|</div>\\n<!--|</div>$)'
        match = re.search(pattern, html_content, re.DOTALL)
        if match:
            new_div = f'<div class="model-block" id="desc-view-wapro-{sku}">\n{new_html}'
            html_content = html_content[:match.start()] + new_div + html_content[match.end():]
        else:
            # Maybe it ends directly
            pattern_alt = f'<div class="model-block" id="desc-view-wapro-{sku}">.*'
            # Will just try simple replacement if it fails, but the first regex usually works.

    return html_content


def add_blogs_to_profiles(html_content):
    profile_blog = """<section style="font-family:inherit; margin:18px 0 28px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <div style="font-family:inherit; margin-bottom:18px; background:none !important; background-color:transparent !important; color:inherit;">
    <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Praktyczne poradniki</font>
  </span>
    <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
      Dobierz profil LED do taśmy i efektu
    </h3>
    <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.78; font-size:14px; line-height:1.6;">
      Profil wpływa na chłodzenie, montaż, wygląd linii i dobór klosza. Te poradniki pomagają uniknąć złego zestawienia taśmy, osłony i zasilania.
    </p>
  </div>
  <div style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit; align-items:stretch;">
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać profil aluminiowy do taśmy LED?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">profil, klosz, chłodzenie i estetyka linii światła</small>
      <a href="https://www.prescot.com.pl/pl/n/15" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
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
  </div>
</section>"""
    
    # Let's extract all Profile blocks. Profile blocks are those whose ID is desc-view-wapro-A... or PO... etc.
    # Actually, we can just look for any block that has "Profil aluminiowy" or similar, or just check the ID
    # A safer way: any block that starts with desc-view-wapro-A or desc-view-wapro-P
    # Let's just find all blocks, and if they don't have "Praktyczne poradniki", and they are profiles, we append.
    # Or even better: in `index.html`, every `<div class="model-block" id="desc-view-wapro-X">` that contains "Profil LED" or "Profil aluminiowy" should get the blog.
    
    blocks = re.split(r'(<div class="model-block" id="desc-view-wapro-[^"]+">)', html_content)
    # blocks[0] is the prefix
    # then blocks[1] is the div opening, blocks[2] is the content, etc.
    
    new_html = blocks[0]
    for i in range(1, len(blocks), 2):
        div_opening = blocks[i]
        content = blocks[i+1]
        
        # Determine if it's a profile
        if "Profil LED" in content or "Profil aluminiowy" in content or "Wykończenie: Srebrny" in content:
            # Check if it already has blogs
            if "Praktyczne poradniki" not in content:
                # Append before the last </div> if it exists
                # The content might end with </div>.
                if content.strip().endswith('</div>'):
                    content = content[:content.rfind('</div>')] + '\n' + profile_blog + '\n</div>\n'
                else:
                    content += '\n' + profile_blog + '\n'
        
        new_html += div_opening + content

    return new_html

def update_excel_from_html(html_path, excel_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Extract all descriptions from HTML
    blocks = re.findall(r'<div class="model-block" id="desc-view-wapro-([^"]+)">(.*?)</div>\s*(?:<!--|<div class="model-block"|$)', html_content, re.DOTALL)
    
    sku_to_html = {}
    for sku, content in blocks:
        sku_to_html[sku] = content.strip()
    
    print(f"Extracted {len(sku_to_html)} HTML blocks from index.html.")

    df = pd.read_excel(excel_path)
    updated_count = 0
    
    for idx, row in df.iterrows():
        sku = str(row['INDEKS_HANDLOWY']).strip()
        if sku in sku_to_html:
            df.at[idx, 'Opis'] = sku_to_html[sku]
            updated_count += 1
            
    print(f"Updated {updated_count} SKUs in Excel.")
    df.to_excel(excel_path, index=False)
    print("Saved Excel.")

if __name__ == "__main__":
    html_file = "/Users/karolbohdanowicz/my-ai-agents/prescot/index.html"
    excel_file = "/Users/karolbohdanowicz/Desktop/EksportowaneArtykuly.xlsx"

    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update sterowniki
    html = update_sterownik_html(html)
    
    # 2. Add blogs to profiles
    html = add_blogs_to_profiles(html)
    
    # 3. Save index.html
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
        
    print("Saved index.html")
    
    # 4. Update Excel
    update_excel_from_html(html_file, excel_file)
