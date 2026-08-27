import re
import html

# Base blog section for all descriptions
blogs_section = """<section style="font-family:inherit; margin:0 0 28px 0; padding:24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">

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

def create_description(title, intro_text, features, usage_title, usage_text, tech_spec):
    return f"""<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
 <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
 <font color="#ffffff">ZŁĄCZKA LED HIPPO-M</font>
 </span>

 <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
 {title}
 </h3>

 <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
 {intro_text}
 </p>
</section>

<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
 <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
 <font color="#ffffff">KLUCZOWE CECHY</font>
 </span>

 <ul style="font-family:inherit; margin:0; padding:0 0 0 20px; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
 {features}
 </ul>
</section>

<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
 <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
 <font color="#ffffff">GDZIE UŻYĆ</font>
 </span>

 <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
 {usage_title}
 </h3>

 <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
 {usage_text}
 </p>
</section>

<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
 <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
 <font color="#ffffff">Specyfikacja</font>
 </span>

 <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
 Zgodność z instalacją
 </h3>

 <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
 {tech_spec}
 </p>
</section>

{blogs_section}"""

# Data for 4 SKUs
products = [
    {
        "sku": "FC8-COB-MONO-TP-NW",
        "name": "Złączka do taśmy LED Hippo-M Max SMD/COB mono 8mm taśma-przewód 4A",
        "badge": "NOWOŚĆ",
        "title": "Błyskawiczne zasilanie bez lutowania",
        "intro": "Innowacyjna złączka serii Hippo-M Max przeznaczona do profesjonalnego łączenia taśm SMD i COB o szerokości laminatu 8mm. Pozwala na bezproblemowe wyprowadzenie zasilania z taśmy LED przy użyciu własnego przewodu, eliminując potrzebę używania lutownicy.",
        "features": '''<li style="font-family:inherit; margin-bottom:6px;"><strong style="font-family:inherit; color:inherit !important;">Typ taśma-przewód:</strong> Możliwość wsunięcia i zaciśnięcia własnego przewodu zasilającego, co daje pełną elastyczność długości kabla.</li>
<li style="font-family:inherit; margin-bottom:6px;"><strong style="font-family:inherit; color:inherit !important;">Obsługa COB i SMD:</strong> Wzmocnione, podwójne zęby radzą sobie z każdym typem taśmy 8mm (MONO).</li>
<li style="font-family:inherit; margin-bottom:0;"><strong style="font-family:inherit; color:inherit !important;">Wysoka jakość:</strong> Krystalicznie czysta, transparentna obudowa nie rzuca cienia i nie blokuje diod COB.</li>''',
        "usage_title": "Zasilanie każdego odcinka",
        "usage_text": "Idealna do doprowadzania zasilania do początków lub końców obwodów, tworząc solidne mechaniczne i elektryczne połączenie dzięki solidnemu zaciśnięciu zębów miedzianych.",
        "tech_spec": 'Przeznaczona do taśm szerokości <strong style="font-family:inherit; color:inherit !important;">8mm</strong>. Obsługiwany prąd maksymalny: <strong style="font-family:inherit; color:inherit !important;">4A</strong> (np. ok. 48W dla instalacji 12V lub 96W dla 24V). Indeks handlowy: <strong style="font-family:inherit; color:inherit !important;">FC8-COB-MONO-TP-NW</strong>.'
    },
    {
        "sku": "FC8-COB-MONO-TT-L",
        "name": "Złączka do taśmy LED Hippo-M Max SMD/COB mono 8mm taśma-taśma narożna (L/T) 4A",
        "badge": "NOWOŚĆ",
        "title": "Wygodne łączenie pod kątem 90°",
        "intro": "Specjalistyczna złączka kątowa Hippo-M Max do taśm SMD i COB o szerokości laminatu 8mm. Konstrukcja typu L gwarantuje estetyczne prowadzenie światła w trudnych miejscach bez ryzyka przełamania taśmy.",
        "features": '''<li style="font-family:inherit; margin-bottom:6px;"><strong style="font-family:inherit; color:inherit !important;">Złącze narożne (typ L):</strong> Doskonałe przejście przez zakręty i załamania pod kątem prostym, np. w ramach czy meblach.</li>
<li style="font-family:inherit; margin-bottom:6px;"><strong style="font-family:inherit; color:inherit !important;">Idealne dla COB:</strong> Przezroczysta struktura pozwala na maksymalną przepuszczalność światła i zachowanie równomiernej linii.</li>
<li style="font-family:inherit; margin-bottom:0;"><strong style="font-family:inherit; color:inherit !important;">Trwały styk:</strong> Solidne zaciśnięcie na laminacie taśmy zapewnia niezawodne przewodzenie prądu.</li>''',
        "usage_title": "Narożniki, profile i ramki",
        "usage_text": "Ułatwia estetyczne przejście przez narożnik, utrzymując ciągłość instalacji tam, gdzie taśma LED nie może zostać fizycznie wygięta. Wyrównaj bieguny i zaciśnij mocno szczypcami.",
        "tech_spec": 'Szerokość płytki PCB: <strong style="font-family:inherit; color:inherit !important;">8mm</strong>. Maksymalne obciążenie prądowe: <strong style="font-family:inherit; color:inherit !important;">4A</strong> (12V/24V). Indeks handlowy: <strong style="font-family:inherit; color:inherit !important;">FC8-COB-MONO-TT-L</strong>.'
    },
    {
        "sku": "FC8-COB-MONO-TT",
        "name": "Złączka do taśmy LED Hippo-M Max SMD/COB mono 8mm taśma-taśma 4A",
        "badge": "NOWOŚĆ",
        "title": "Niewidoczne przedłużanie taśmy",
        "intro": "Złączka podłużna z zaawansowanej serii Hippo-M Max stworzona z myślą o bezproblemowym łączeniu dwóch odcinków taśm SMD i COB (szerokość 8mm) w prostej linii.",
        "features": '''<li style="font-family:inherit; margin-bottom:6px;"><strong style="font-family:inherit; color:inherit !important;">Łączenie taśma-taśma:</strong> Przedłużanie obwodu LED bez używania cyny ani narzędzi do lutowania.</li>
<li style="font-family:inherit; margin-bottom:6px;"><strong style="font-family:inherit; color:inherit !important;">Brak mrocznych stref (COB):</strong> Transparentne ramię łącznika sprawia, że krawędzie diod taśmy COB są maksymalnie wyeksponowane, co zapobiega powstawaniu cieni w miejscu łączenia.</li>
<li style="font-family:inherit; margin-bottom:0;"><strong style="font-family:inherit; color:inherit !important;">Zęby przebijające:</strong> Gwarancja doskonałego kontaktu między ścieżkami miedzianymi a złączką.</li>''',
        "usage_title": "Łączenie resztek i długie linie",
        "usage_text": "Wykorzystaj tę złączkę, gdy potrzebujesz stworzyć długi ciąg taśmy z krótszych odcinków. Jest na tyle wąska, że z łatwością ukryjesz ją we wnętrzu większości profili aluminiowych.",
        "tech_spec": 'Przeznaczona do taśm jednobarwnych o szerokości <strong style="font-family:inherit; color:inherit !important;">8mm</strong>. Maksymalny dopuszczalny prąd: <strong style="font-family:inherit; color:inherit !important;">4A</strong>. Indeks handlowy: <strong style="font-family:inherit; color:inherit !important;">FC8-COB-MONO-TT</strong>.'
    },
    {
        "sku": "FC8-COB-MONO-TP",
        "name": "Złączka do taśmy LED Hippo-M Max SMD/COB mono 8mm taśma-przewód 15cm 5A",
        "badge": "NOWOŚĆ",
        "title": "Gotowe zasilanie z wyprowadzonym przewodem",
        "intro": "Wygodne rozwiązanie łączące cechy wysokoprądowego złącza typu Hippo-M Max oraz gotowego przewodu zasilającego o długości 15 cm. Kompatybilna z taśmami SMD i COB 8mm, obsługuje prądy aż do 5A.",
        "features": '''<li style="font-family:inherit; margin-bottom:6px;"><strong style="font-family:inherit; color:inherit !important;">Przewód 15cm w zestawie:</strong> Nie musisz zarabiać i docinać własnego kabla, złączka posiada zintegrowany czerwono-czarny przewód zasilający.</li>
<li style="font-family:inherit; margin-bottom:6px;"><strong style="font-family:inherit; color:inherit !important;">Wersja wysokoprądowa 5A:</strong> Ulepszone piny i solidny przewód gwarantują stabilne zasilanie dla dłuższych odcinków taśm o wysokiej mocy (nawet 120W przy 24V).</li>
<li style="font-family:inherit; margin-bottom:0;"><strong style="font-family:inherit; color:inherit !important;">Ultra przezroczysta:</strong> Perfekcyjny wybór dla instalacji na bazie COB.</li>''',
        "usage_title": "Ekspresowy montaż zasilacza",
        "usage_text": "Błyskawicznie wyprowadź bieguny do sterownika lub zasilacza z początku taśmy. Wystarczy wsunąć taśmę 8mm w zacisk i zatrzasnąć, a kable podpiąć do odpowiedniego portu zasilającego.",
        "tech_spec": 'Dedykowana dla taśm <strong style="font-family:inherit; color:inherit !important;">8mm</strong>. Wysoka obciążalność do <strong style="font-family:inherit; color:inherit !important;">5A</strong> (zwiększona obciążalność prądowa). Posiada dolutowany przewód <strong style="font-family:inherit; color:inherit !important;">15 cm</strong>. Indeks handlowy: <strong style="font-family:inherit; color:inherit !important;">FC8-COB-MONO-TP</strong>.'
    }
]

def build_accordion(product, index, platform):
    desc_html = create_description(
        product["title"], product["intro"], product["features"], 
        product["usage_title"], product["usage_text"], product["tech_spec"]
    )
    desc_escaped = html.escape(desc_html)
    
    return f"""
<div class="product-accordion" data-model="{product['sku']}">
    <div class="accordion-header" onclick="toggleAccordion(this)">
        <span class="product-model">{index}. {product['name']}</span>
        <div class="product-header-right">
            <span class="product-label-badge" style="background-color: #2563eb;">{product['badge']}</span>
            <span class="chevron">▼</span>
        </div>
    </div>
    <div class="accordion-content">
        <div class="model-block" id="desc-view-{platform}-{product['sku']}">
{desc_html}
        </div>
        <div class="edit-block" id="desc-edit-{platform}-{product['sku']}" style="display: none;">
            <textarea class="edit-textarea" id="textarea-{platform}-{product['sku']}" oninput="onDescriptionInput('{platform}', 'zlaczki', '{product['sku']}')">{desc_escaped}</textarea>
        </div>
        <div class="product-controls">
            <button class="control-btn btn-edit" id="btn-edit-{platform}-{product['sku']}" onclick="toggleEdit('{platform}', 'zlaczki', '{product['sku']}')">Edytuj opis</button>
            <button class="control-btn btn-save" id="btn-save-{platform}-{product['sku']}" onclick="saveDescription('{platform}', 'zlaczki', '{product['sku']}')" style="display: none;">Zapisz opis</button>
            <button class="control-btn btn-copy" onclick="copyDescriptionHtml('{platform}', '{product['sku']}', this)" style="border-color: #f59e0b; color: #f59e0b;" title="Kopiuj opis HTML">Kopiuj opis HTML</button>
            <span class="control-status" id="status-{platform}-{product['sku']}"></span>
        </div>
    </div>
</div>"""

def update_html():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    platforms = ['wapro', 'tim', 'allegro']
    start_index = 18  # Wait, earlier script changed Złączki bezlutowe (12) -> (17), meaning they end at 17. Let's make it start at 18.
    
    # Check how many items currently in zlaczki
    count_matches = re.search(r'Złączki bezlutowe \((\d+)\)', content)
    if count_matches:
        current_count = int(count_matches.group(1))
        content = content.replace(f'Złączki bezlutowe ({current_count})', f'Złączki bezlutowe ({current_count + 4})')
        start_index = current_count + 1
    
    for platform in platforms:
        panel_id = f'<div class="sub-tab-panel" id="{platform}-zlaczki">'
        start_idx = content.find(panel_id)
        
        # Find where to insert (before the end of the panel)
        if platform == 'wapro':
            end_str = '</div>\n</div>\n<!-- ==================== TIM TAB PANEL ==================== -->'
        elif platform == 'tim':
            end_str = '</div>\n</div>\n<!-- ==================== ALLEGRO TAB PANEL ==================== -->'
        else:
            end_str = '</div>\n</div>\n<script>'
            
        end_idx = content.find(end_str, start_idx)
        
        accordions = "\n"
        for i, prod in enumerate(products):
            accordions += build_accordion(prod, start_index + i, platform) + "\n"
            
        content = content[:end_idx] + accordions + content[end_idx:]

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    update_html()
    print("Done!")
