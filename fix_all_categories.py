import re
from bs4 import BeautifulSoup

def get_category(sku):
    if sku.startswith(('WZ-', 'V1', 'T1', 'V2', 'RT1', 'RT6', 'DIM-')) or 'RGB' in sku and len(sku) < 10 or sku.startswith('PR-'):
        return 'sterowniki'
    if sku.startswith(('SC-', 'LRS-', 'RS-', 'SCH-')):
        return 'zasilacze'
    if sku.startswith(('B8547', '18032', 'A01587', 'A02966')):
        return 'profile'
    if sku.startswith(('FC10', 'FC8', 'ZLC', 'M4-')):
        return 'zlaczki'
    return 'tasmy'

blog_html = """
<div class="blog-grid" style="font-family:inherit; margin-top: 28px; background:none !important; background-color:transparent !important; color:inherit;">
    <h3 style="font-family:inherit; margin:0 0 16px 0; font-size:22px; font-weight:700;">Baza Wiedzy - Prescot</h3>
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; align-items:stretch;">
        <div style="min-height:190px; padding:18px; border:1px solid currentColor; border-radius:12px; display:flex; flex-direction:column;">
            <strong style="display:block; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak czytać parametry taśmy LED?</strong>
            <small style="display:block; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">moc, lumeny, CRI, napięcie i IP</small>
            <a href="https://www.prescot.com.pl/pl/n/23" style="display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; font-weight:700; font-size:14px;">Czytaj poradnik</a>
        </div>
        <div style="min-height:190px; padding:18px; border:1px solid currentColor; border-radius:12px; display:flex; flex-direction:column;">
            <strong style="display:block; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Montaż taśmy LED na zewnątrz</strong>
            <small style="display:block; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">IP, uszczelnienie i ochrona połączeń</small>
            <a href="https://www.prescot.com.pl/pl/n/16" style="display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; font-weight:700; font-size:14px;">Czytaj poradnik</a>
        </div>
        <div style="min-height:190px; padding:18px; border:1px solid currentColor; border-radius:12px; display:flex; flex-direction:column;">
            <strong style="display:block; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać taśmę LED do mieszkania?</strong>
            <small style="display:block; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">barwa, moc i miejsce montażu</small>
            <a href="https://www.prescot.com.pl/pl/n/12" style="display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; font-weight:700; font-size:14px;">Czytaj poradnik</a>
        </div>
        <div style="min-height:190px; padding:18px; border:1px solid currentColor; border-radius:12px; display:flex; flex-direction:column;">
            <strong style="display:block; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać profil aluminiowy do taśmy LED?</strong>
            <small style="display:block; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">profil, klosz, chłodzenie i estetyka linii światła</small>
            <a href="https://www.prescot.com.pl/pl/n/15" style="display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; font-weight:700; font-size:14px;">Czytaj poradnik</a>
        </div>
    </div>
</div>
"""

def generate_desc(category, sku, badge_text=""):
    blocks = []
    
    if category == 'sterowniki':
        badge_lower = badge_text.lower()
        sku_upper = sku.upper()
        if 'cct' in badge_lower or 'cct' in sku_upper:
            typ_desc = "Pełna kontrola nad temperaturą barwową (CCT) pozwala błyskawicznie zmienić klimat wnętrza – od chłodnego światła do pracy, po ciepłe do relaksu."
            typ_head = "Zarządzanie temperaturą bieli"
            pill = "KONTROLA CCT"
        elif 'rgbw' in badge_lower or 'rgbw' in sku_upper:
            typ_desc = "Odkryj nieskończone możliwości palety RGB wzbogacone o dedykowaną, czystą biel. Twórz niesamowite sceny świetlne i zapisuj ulubione kolory, aby natychmiast wracać do pożądanego nastroju."
            typ_head = "Kolory i czysta biel w jednym"
            pill = "MAGIA RGBW"
        elif 'rgb' in badge_lower or 'rgb' in sku_upper:
            typ_desc = "Zarządzaj milionami kolorów z palety RGB. Twórz dynamiczne przejścia lub wybierz stały odcień, który idealnie dopełni Twoją przestrzeń życiową."
            typ_head = "Pełna paleta barw do dyspozycji"
            pill = "MAGIA RGB"
        else:
            typ_desc = "Płynne i pozbawione migotania ściemnianie taśm jednokolorowych to podstawa wygody. Idealnie dostosuj jasność do pory dnia lub potrzeb domowników."
            typ_head = "Płynna regulacja jasności"
            pill = "PRECYZYJNE ŚCIEMNIANIE"

        blocks.append((
            pill,
            typ_head,
            f"Wysokiej klasy system sterowania, który daje Ci pełną swobodę. {typ_desc} Szybka reakcja na polecenia i intuicyjna obsługa zapewniają bezproblemowe zarządzanie światłem na co dzień."
        ))
        blocks.append((
            "WSZECHSTRONNA FUNKCJONALNOŚĆ",
            "Rozwiązania, które ułatwiają życie",
            "<ul><li style='margin-bottom:8px;'><b>Wysoka obciążalność:</b> Obsługa długich odcinków taśm LED (nawet 15-20m) na jednym kontrolerze bez utraty stabilności.</li><li style='margin-bottom:8px;'><b>Auto-retransmisja sygnału:</b> Urządzenia mogą przekazywać sygnał radiowy między sobą (do 30m), co pozwala na budowę ogromnych stref świetlnych.</li><li style='margin-bottom:0;'><b>Tryb 'Do Not Disturb':</b> Inteligentna funkcja, która zapobiega samoistnemu włączeniu świateł po chwilowym zaniku zasilania w nocy.</li></ul>"
        ))
        blocks.append((
            "SYSTEM WIELE-DO-WIELU",
            "Nieskończone możliwości łączenia",
            "Ten ekosystem rośnie razem z Twoimi potrzebami. Przypisz wiele sterowników do jednego pilota, tworząc zsynchronizowane strefy, lub używaj kilku pilotów (np. ściennego i przenośnego) do sterowania jedną sekcją. Instalacja jest elastyczna i banalnie prosta."
        ))
        
    elif category == 'zasilacze':
        badge_lower = badge_text.lower()
        sku_lower = sku.lower()
        
        w_match = re.search(r'(\d+)W', badge_text, re.IGNORECASE)
        watt = f" {w_match.group(1)}W" if w_match else ""
        
        if 'slim' in badge_lower or 'sch-' in sku_lower:
            pill = "KOMPAKTOWY ROZMIAR"
            head = f"Wąska obudowa do zadań specjalnych{watt}"
            desc = "Ten zasilacz o ultracienkim profilu został stworzony z myślą o bardzo ograniczonych przestrzeniach. Idealnie mieści się za lustrem, w płytkiej wnęce meblowej czy w ciasnym kanale sufitu podwieszanego – zapewniając moc bez konieczności kucia ścian."
        elif 'hermetycz' in badge_lower or 'lrs' in sku_lower or 'ip67' in badge_lower:
            pill = "PODWYŻSZONA ODPORNOŚĆ"
            head = f"Bezpieczna praca w trudnych warunkach{watt}"
            desc = "Wytrzymała aluminiowa obudowa i wysoki stopień ochrony gwarantują bezawaryjną pracę tam, gdzie standardowe zasilacze zawodzą. Konstrukcja odporna na zapylenie i wilgoć, idealna do instalacji zewnętrznych oraz łazienek."
        else:
            pill = "ZASILANIE PREMIUM"
            head = f"Stabilne napięcie dla Twojej instalacji{watt}"
            desc = "Wydajny zasilacz to absolutny fundament instalacji LED. Zapewnia stałe napięcie i odpowiednią rezerwę mocy, co przekłada się na idealną, równą jasność całej taśmy na każdym jej metrze i zapobiega nadmiernemu przegrzewaniu diod."

        blocks.append((pill, head, desc))
        
        blocks.append((
            "BEZPIECZEŃSTWO I TRWAŁOŚĆ",
            "Ochrona Twojej instalacji LED",
            "<ul><li style='margin-bottom:8px;'><b>Ochrona przeciwzwarciowa:</b> Natychmiastowe odcięcie zasilania w przypadku zwarcia, chroniące układ elektryczny.</li><li style='margin-bottom:8px;'><b>Ochrona przeciążeniowa:</b> Zabezpieczenie chroniące przed uszkodzeniem spowodowanym podpięciem zbyt dużej liczby taśm.</li><li style='margin-bottom:0;'><b>Wydajne komponenty:</b> Elementy wewnętrzne odpowiednio dobrane i przystosowane do pracy pod pełnym obciążeniem.</li></ul>"
        ))
        blocks.append((
            "PRZEWAGA SCHARFER ORAZ MONTAŻ",
            "Ergonomia instalacji i cisza działania",
            "Marka Scharfer słynie ze świetnej stabilizacji napięcia oraz pasywnego chłodzenia, co całkowicie eliminuje irytujący problem piszczących cewek. Sama budowa urządzenia to ukłon w stronę instalatorów – mocne zaciski śrubowe oraz wygoda podłączenia przewodów sprawiają, że instalacja przebiega błyskawicznie i profesjonalnie."
        ))

    elif category == 'profile':
        blocks.append((
            "PROFIL KLUŚ",
            "Fundament trwałego systemu LED",
            "Profil aluminiowy renomowanej marki KLUŚ to absolutny niezbędnik każdej profesjonalnej instalacji. Pełni kluczową funkcję radiatora – skutecznie odprowadza ciepło z nagrzewających się diod LED. Pamiętaj: bez odpowiedniego aluminiowego profilu, żywotność każdej, nawet najlepszej taśmy ulega drastycznemu skróceniu!"
        ))
        blocks.append((
            "RODZAJE I ZASTOSOWANIE",
            "Profile wpuszczane i nawierzchniowe",
            "W ofercie posiadamy dwa najpopularniejsze warianty profili KLUŚ: wpuszczane oraz nawierzchniowe. Profile wpuszczane wtapiają się we frezowane płyty meblowe czy GK, tworząc zlicowaną linię. Nawierzchniowe przykręca lub przykleja się błyskawicznie pod szafkami czy we wnękach."
        ))
        blocks.append((
            "IDEALNA LINIA ŚWIATŁA",
            "Mleczny klosz i rozproszenie",
            "Oprócz funkcji chłodzącej, profil w połączeniu z odpowiednim, mlecznym kloszem fantastycznie rozprasza światło, niwelując efekt \"kropkowania\" diod na taśmie (szczególnie w taśmach SMD). Dzięki temu uzyskujesz gładką, przyjemną dla oka linię świetlną."
        ))
        
    elif category == 'zlaczki':
        badge_lower = badge_text.lower()
        
        if '8mm' in badge_lower:
            szerokosc = "8mm (np. popularne taśmy jednokolorowe MONO COB lub SMD)"
        elif '10mm' in badge_lower:
            szerokosc = "10mm (często taśmy CCT, RGB lub wyższe moce MONO)"
        elif '12mm' in badge_lower:
            szerokosc = "12mm (zazwyczaj taśmy RGBW lub wielokolorowe)"
        else:
            szerokosc = "odpowiedniej szerokości"

        if 'kątow' in badge_lower or ' l ' in badge_lower:
            zasada = "Złączka typu L (kątowa) służy do estetycznego i bezpiecznego zakręcania taśmą pod kątem 90 stopni, bez ryzyka przełamania ścieżek miedzianych na laminacie."
            zastosowanie = "Idealna przy załamaniach blatu, w narożnikach sufitów podwieszanych i półek meblowych."
        elif 'trójnik' in badge_lower or ' t ' in badge_lower or ' t' in badge_lower:
            zasada = "Złączka typu T (trójnik) rozgałęzia sygnał i zasilanie w trzech kierunkach. Działa jak rozdzielacz, pozwalając na poprowadzenie światła w dwie strony od jednego punktu."
            zastosowanie = "Świetnie sprawdza się w rozbudowanych instalacjach, gdzie potrzebujemy stworzyć odnogi od głównego ciągu świetlnego."
        elif '9w1' in badge_lower or 'uniwersalna' in badge_lower:
            zasada = "Uniwersalny zestaw 9w1 (wielofunkcyjna złączka) pozwala na łączenie prostych odcinków, wyprowadzenie kabli do zasilacza lub łączenie taśm ze złączką narożną."
            zastosowanie = "Prawdziwy niezbędnik instalatora – jeden komplet rozwiązuje większość typowych problemów łączeniowych na obiekcie, dając ogromną swobodę."
        else:
            zasada = "Standardowa złączka służy do szybkiego łączenia dwóch odciętych kawałków taśmy w jedną dłuższą linię lub do bezlutowego podpięcia przewodów zasilających."
            zastosowanie = "Podstawowy element instalacyjny, pozwalający na przedłużanie taśmy bez konieczności kłopotliwego lutowania."

        blocks.append((
            "ZASADA DZIAŁANIA",
            "Szybki i pewny styk bez lutowania",
            f"{zasada} Kluczem działania złączek zaciskowych typu klips są ostre, metalowe piny wewnątrz, które mocno dociskają (lub przebijają) miedziane punkty stykowe taśmy, gwarantując ciągłość obwodu."
        ))
        blocks.append((
            "KOMPATYBILNOŚĆ",
            f"Dopasowana do taśm {szerokosc.split(' ')[0]}",
            f"Prezentowany model został zaprojektowany z myślą o taśmach o szerokości laminatu {szerokosc}. Solidny zacisk poliwęglanowej obudowy chroni przed przypadkowym wysunięciem się taśmy podczas pracy."
        ))
        blocks.append((
            "PRAKTYCZNE ZASTOSOWANIE",
            "Zwiększona wygoda instalatora",
            f"{zastosowanie} Wykorzystanie złączek eliminuje konieczność trudnego lutowania bezpośrednio na drabinie, co przyspiesza pracę i ułatwia szybkie przeróbki."
        ))
    else:
        return None, None
        
    html = ""
    text_val = ""
    for b in blocks:
        pill, h, p = b
        html += f"""
<section style="font-family: inherit; margin: 0 0 18px 0; padding: 22px 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
<span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;"> <span style="color: #ffffff;">{pill}</span> </span>
<h3 style="font-family: inherit; margin: 0 0 8px 0; background: none !important; background-color: transparent !important; color: inherit !important; font-size: 22px; line-height: 1.3; font-weight: bold;">{h}</h3>
"""
        if p.startswith("<ul>"):
            html += f"{p}\n</section>"
            text_val += f"{pill}\n{h}\n[Funkcje opisane punktowo]\n\n"
        else:
            html += f"<p style=\"font-family: inherit; margin: 0; background: none !important; background-color: transparent !important; color: inherit !important; font-size: 16px; line-height: 1.6; opacity: 0.85;\">{p}</p>\n</section>"
            text_val += f"{pill}\n{h}\n{p}\n\n"

    html += blog_html
    return html, text_val.strip()

with open('index.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

cards = soup.find_all('div', class_='product-accordion')
updates_count = {'sterowniki': 0, 'zasilacze': 0, 'profile': 0, 'zlaczki': 0, 'tasmy': 0}

for card in cards:
    sku = card.get('data-model')
    if not sku:
        continue
    
    cat = get_category(sku)
    badge_span = card.find('span', class_='product-label-badge')
    badge_text = badge_span.text.strip() if badge_span else sku
    
    for tab in ['wapro', 'tim', 'allegro']:
        model_block = card.find('div', id=f'desc-view-{tab}-{sku}')
        textarea = card.find('textarea', id=f'textarea-{tab}-{sku}')

        if model_block and textarea:
            if cat == 'tasmy':
                existing_html = "".join([str(c) for c in model_block.contents])
                if "Baza Wiedzy - Prescot" not in existing_html:
                    blog_soup = BeautifulSoup(blog_html, 'html.parser')
                    model_block.append(blog_soup)
                    updates_count[cat] += 1
            else:
                html, text_val = generate_desc(cat, sku, badge_text)
                if html:
                    spec_table = model_block.find('section', class_='product-parameters-section')
                    spec_html = str(spec_table) if spec_table else ""
                    
                    new_html = html + "\n" + spec_html
                    new_soup = BeautifulSoup(new_html, 'html.parser')
                    
                    model_block.clear()
                    model_block.append(new_soup)
                    
                    textarea.string = text_val
                    updates_count[cat] += 1

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))
    
print(f"Updated items: {updates_count}")
