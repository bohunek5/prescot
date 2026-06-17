import re
import random

def spin(text, seed):
    random.seed(seed)
    while True:
        match = re.search(r'\{([^{}]+)\}', text)
        if not match:
            break
        options = match.group(1).split('|')
        text = text[:match.start()] + random.choice(options) + text[match.end():]
    return text

SPIN_PATTERNS = [
    # Low brightness
    (
        r"Low brightness wybierasz tam, gdzie światło ma być obecne, ale nie agresywne: w cokołach, półkach, witrynach, wnękach, sypialni, za lustrem albo w nocnej linii komunikacyjnej\. To taśma do efektu i komfortu, nie do prześwietlania całej zabudowy\.",
        "{Wybierz wariant Low brightness|Polecamy linię Low brightness|Taśma Low brightness to optymalny wybór} do miejsc, w których światło {powinno być subtelne|ma budować nastrój|ma być obecne, ale dyskretne}. {Sprawdzi się doskonale w cokołach, witrynach i wnękach|Zastosuj ją za lustrem, w sypialni czy półkach|Idealnie nadaje się do nocnych linii komunikacyjnych i półek}. {Jej głównym zadaniem jest zapewnienie wizualnego komfortu|To oświetlenie zaprojektowane dla efektu i nastroju|Tworzy przytulny klimat bez efektu olśnienia}, a nie {intensywne oświetlanie całego pomieszczenia|dominacja w przestrzeni|silne prześwietlanie całej zabudowy}."
    ),
    # Barwa ciepła (2700K)
    (
        r"Ciepła biel \(2700K\) ociepla drewno, kamień, beże i elementy dekoracyjne\. Wybierz ją do salonu, sypialni, restauracji, hotelu, garderoby lub ekspozycji, w której światło ma budować klimat, a nie techniczny chłód\.",
        "{Ciepła barwa 2700K świetnie podkreśla fakturę drewna, kamienia i naturalnych kolorów|Barwa 2700K (ciepła biel) doskonale komponuje się z elementami w beżach, drewnie i kamieniu|Odcień 2700K wizualnie ociepla wnętrze, wydobywając urok drewnianych i kamiennych detali}. {Rekomendujemy ją do salonów, sypialni czy przytulnych restauracji|Sprawdzi się idealnie w sypialni, garderobie lub strefach relaksu|To świetny wybór do wnętrz hotelowych, domowych salonów i ciepłych ekspozycji}, gdzie {liczy się nastrojowy klimat|światło ma sprzyjać wypoczynkowi|szukasz klimatycznego efektu zamiast chłodnego, technicznego blasku}."
    ),
    # Barwa ciepła 3000K
    (
        r"Ciepła biel \(3000K\) świetnie komponuje się z klasycznymi wnętrzami i materiałami takimi jak drewno czy cegła\. Najczęściej wybierana do salonów, sypialni i stref relaksu jako główne lub dekoracyjne źródło światła\.",
        "{Barwa 3000K (ciepła biel) to idealny dodatek do klasycznych aranżacji|Światło o temperaturze 3000K wspaniale łączy się z drewnem, cegłą i tradycyjnym wystrojem|Ciepły odcień 3000K świetnie pasuje do naturalnych materiałów we wnętrzach}. {Klienci najchętniej wybierają ją do salonów, stref wypoczynku i sypialni|Zalecamy jej montaż w sypialniach, salonach i miejscach przeznaczonych do relaksu|Jest to optymalne rozwiązanie do oświetlania stref dziennych}, {jako oświetlenie główne lub akcentujące|zarówno w funkcji dekoracyjnej, jak i podstawowej|gdzie pełni funkcję nastrojowego tła}."
    ),
    # Barwa 4000K
    (
        r"Barwa 4000K gwarantuje czysty, neutralny odcień – bez żółtych ani niebieskich domieszek\. Idealna do stref roboczych, gabinetów, przestrzeni komercyjnych oraz nad lustrem do precyzyjnego makijażu\.",
        "{Neutralna biel 4000K zapewnia bardzo czyste, świeże światło|Temperatura 4000K to gwarancja czystego oświetlenia bez żółtych i niebieskich tonów|Barwa neutralna (4000K) oferuje naturalne oddawanie kolorów bez przebarwień}. {To doskonały wybór do biur, gabinetów i nowoczesnych kuchni|Zalecamy ten wariant do przestrzeni roboczych, łazienek i miejsc komercyjnych|Sprawdzi się doskonale nad blatem roboczym, lustrem w łazience czy w biurze}, {gdzie liczy się skupienie i precyzja|pozwalając na komfortową pracę i wierne odwzorowanie barw|gdzie potrzebne jest jasne, pobudzające światło do pracy}."
    ),
    # 460lm/m (and similar decorative)
    (
        r"Jest to idealny poziom jasności do tworzenia akcentów świetlnych: do wnęk, gablot, półek i regałów, gdzie światło nie może oślepiać\. Zapewnia wyraźny, ale bardzo miękki i relaksujący blask\.",
        "{Taki poziom jasności jest optymalny dla oświetlenia akcentującego|To doskonały parametr do zastosowań wyłącznie dekoracyjnych|Ta moc świetlna świetnie sprawdza się przy tworzeniu subtelnych detali}: {w regałach, gablotach, półkach i małych wnękach|pod półkami, w witrynach meblowych czy cokołach|wszędzie tam, gdzie unikamy efektu oślepiania}. {Gwarantuje zauważalny, lecz bardzo łagodny efekt|Światło jest widoczne, ale pozostaje miękkie i przyjemne dla oczu|Efekt to relaksująca, dyskretna łuna świetlna}."
    ),
    # 900lm/m (Medium brightness equivalent)
    (
        r"Tu taśma pracuje już jak wyraźne oświetlenie użytkowe\. Wybierz ją nad blatem, w profilu podszafkowym, nad ladą, w witrynie, przy ekspozycji produktu albo w dłuższej linii meblowej, gdzie światło ma być widoczne nawet przy oświetleniu ogólnym\.",
        "{Przy tych parametrach taśma staje się solidnym światłem roboczym|Taka moc pozwala na wykorzystanie taśmy jako pełnoprawnego oświetlenia użytkowego|To poziom jasności, który realnie doświetla przestrzeń roboczą}. {Polecamy montaż w profilach podszafkowych, nad ladami czy w mocnych witrynach|Najlepiej sprawdzi się nad blatem kuchennym, w długich ciągach meblowych lub nad ladą|Zastosuj ten model do mocnej ekspozycji towaru lub w strefach pracy}, {aby uzyskać wyraźne oświetlenie nawet w dzień|gdzie światło musi dominować|gdzie potrzebujesz mocnego i równego światła pomocniczego}."
    ),
    # 1500lm/m + (High brightness equivalent)
    (
        r"Taki poziom jasności ma sens w miejscach, gdzie taśma naprawdę ma świecić: długi blat, mocna ekspozycja, wysoka witryna, zabudowa sufitowa, lada sprzedażowa albo przestrzeń robocza\.",
        "{Tak silny strumień świetlny jest przeznaczony do wymagających stref|To bardzo wysoka moc, idealna tam, gdzie LED pełni kluczową rolę oświetleniową|Taka jasność jest wskazana w miejscach potrzebujących maksymalnego naświetlenia}: {na szerokich blatach roboczych, w wysokich witrynach czy dużych sufitach podwieszanych|w głównym oświetleniu sufitowym, nad dużymi wyspami i w lokalach komercyjnych|w przestrzeniach roboczych, mocnych ekspozycjach i ladach sklepowych}."
    ),
    # Profil, chlodzenie itp
    (
        r"Profil aluminiowy stabilizuje montaż, poprawia chłodzenie i pomaga uzyskać czystą linię światła\.",
        "{Zastosowanie profilu aluminiowego znacznie ułatwia montaż, chłodzi diody i wpływa na estetykę|Pamiętaj o montażu w profilu aluminiowym, który działa jak radiator i przedłuża żywotność taśmy|Profil ALU jest kluczowy do odprowadzania ciepła oraz uzyskania jednolitej, estetycznej linii}."
    ),
    (
        r"Zasilacz dobierz pod (\d+V) i łączną długość wszystkich odcinków\.",
        r"{Wybierz zasilacz \1 o mocy dostosowanej do sumarycznego obciążenia|Konieczne jest użycie zasilacza \1 z odpowiednim zapasem mocy|Pamiętaj o zastosowaniu stabilnego zasilacza \1 dopasowanego do długości całej instalacji}."
    ),
    # Cięcie
    (
        r"Cięcie wykonuj w oznaczonych polach co (\d+mm), żeby zachować poprawne styki i nie uszkodzić odcinka\.",
        r"{Moduły można ciąć wyłącznie w wyznaczonych miejscach co \1|Taśmę przecinaj tylko w miejscach oznaczonych przez producenta (co \1)|Dla zachowania gwarancji i sprawności tnij sekcje dokładnie co \1}, {aby uniknąć uszkodzeń ścieżek|by zachować poprawne działanie paska|żeby nie uszkodzić struktury PCB}."
    ),
    # Rolka 5m
    (
        r"Format rolka 5m sprawdza się przy pojedynczej linii światła albo kilku krótszych odcinkach w jednej zabudowie\.",
        "{Rolka o długości 5m to optymalny format do średnich instalacji lub krótszych odcinków|Wersja 5-metrowa świetnie nadaje się do standardowych mebli i pojedynczych stref oświetleniowych|Pięciometrowa szpula ułatwia wykonanie kilku krótszych linii światła w jednym meblu}."
    ),
    # Rolka 50m
    (
        r"Format rolka 50m jest wygodny przy dłuższych, powtarzalnych realizacjach: regałach, zabudowach, kilku pomieszczeniach albo pracy instalacyjnej, gdzie odcinki docinasz dopiero na miejscu\.",
        "{Rolka 50m to doskonały wybór dla instalatorów i przy dużych projektach|Wersja 50-metrowa ułatwia pracę przy rozbudowanych, wielostrefowych inwestycjach|Szpula o długości 50 metrów to oszczędność i wygoda przy seryjnym oświetlaniu regałów czy dużych sufitów}, {pozwalając na docinanie odcinków na bieżąco|gdzie precyzyjny wymiar ustalany jest dopiero na budowie|oferując maksymalną elastyczność podczas montażu}."
    ),
    # COB
    (
        r"Dzięki technologii COB diody są ułożone tak gęsto, że tworzą gładką, ciągłą linię światła – bez widocznych punktów\.",
        "{Technologia COB pozwala uzyskać perfekcyjnie jednolitą linię światła, całkowicie bez efektu kropkowania|Dzięki budowie typu COB zyskujesz bezpunktową, równomierną łunę świetlną na całej długości|Zastosowanie matrycy COB eliminuje problem widocznych punktów LED, dając ciągłą linię świetlną}."
    ),
    # IP20 / IP65
    (
        r"Klasa IP20 oznacza brak osłony wodoodpornej\. Taśmę montuj w miejscach suchych: meblach, sypialni, korytarzu, salonie i witrynach\. Nie nadaje się do łazienek, na elewacje, ani tam, gdzie grozi jej bezpośredni kontakt z wodą lub dużą wilgocią\.",
        "{Taśma z ochroną IP20 jest przeznaczona do wnętrz i suchych stref|Wersja IP20 nie posiada zabezpieczeń przed wodą, stosuj ją w pokojach dziennych, salonach czy korytarzach|Klasa szczelności IP20 pozwala na bezpieczny montaż w sypialniach i suchych zabudowach}. {Bezwzględnie unikaj montażu w strefach mokrych (np. łazienki, elewacje)|Nie stosuj jej tam, gdzie występuje ryzyko zachlapania lub podwyższona wilgotność|Chronić przed bezpośrednim kontaktem z wodą i parą wodną}."
    )
]

BLOGS = {
    'Taśmy': [
        {'title': 'Jak czytać parametry taśmy LED?', 'subtitle': 'moc, lumeny, CRI, napięcie i IP', 'url': 'https://www.prescot.com.pl/pl/n/23'},
        {'title': 'Montaż taśmy LED na zewnątrz', 'subtitle': 'IP, uszczelnienie i ochrona połączeń', 'url': 'https://www.prescot.com.pl/pl/n/16'},
        {'title': 'Jak dobrać taśmę LED do mieszkania?', 'subtitle': 'barwa, moc i miejsce montażu', 'url': 'https://www.prescot.com.pl/pl/n/12'},
        {'title': 'Jak dobrać profil aluminiowy do taśmy LED?', 'subtitle': 'profil, klosz, chłodzenie i estetyka linii światła', 'url': 'https://www.prescot.com.pl/pl/n/15'}
    ],
    'Zasilacze': [
        {'title': 'Jak dobrać zasilacz LED do taśmy?', 'subtitle': 'Dobór zasilacza LED nie powinien być zgadywaniem.', 'url': 'https://www.prescot.com.pl/pl/n/24'},
        {'title': 'Zasilacze LED - gdzie użyć którego?', 'subtitle': 'Desktop, modułowy czy hermetyczny IP67?', 'url': 'https://www.prescot.com.pl/pl/n/25'},
        {'title': 'Do czego służą zasilacze LED?', 'subtitle': 'Zmiana napięcia z 230V na 12V/24V.', 'url': 'https://www.prescot.com.pl/pl/n/26'},
        {'title': 'Stopnie IP - dlaczego są ważne?', 'subtitle': 'Ochrona zasilacza przed wodą i kurzem.', 'url': 'https://www.prescot.com.pl/pl/n/27'}
    ],
    'Sterowniki': [
        {'title': 'Jak dobrać sterownik do taśmy LED?', 'subtitle': 'Sterowniki do taśm MONO, RGB i RGBW.', 'url': 'https://www.prescot.com.pl/pl/n/28'},
        {'title': 'Sterowanie smartfonem', 'subtitle': 'Aplikacje i integracje ze Smart Home.', 'url': 'https://www.prescot.com.pl/pl/n/29'},
        {'title': 'Parowanie i strefy', 'subtitle': 'Jak zaprogramować wielostrefowe piloty?', 'url': 'https://www.prescot.com.pl/pl/n/30'},
        {'title': 'Ukrywanie sterowników', 'subtitle': 'Montaż mikro-sterowników bezpośrednio w profilu.', 'url': 'https://www.prescot.com.pl/pl/n/31'}
    ],
    'Złączki': [
        {'title': 'Jak łączyć taśmy bez lutowania?', 'subtitle': 'Złączki typu clamp i ich zalety.', 'url': 'https://www.prescot.com.pl/pl/n/32'},
        {'title': 'Lutowanie a złączki', 'subtitle': 'Kiedy wybrać lutowanie, a kiedy złączkę?', 'url': 'https://www.prescot.com.pl/pl/n/33'},
        {'title': 'Złączki 9w1', 'subtitle': 'Uniwersalne złączki do taśm LED i profili.', 'url': 'https://www.prescot.com.pl/pl/n/34'},
        {'title': 'Łączenie taśm w narożnikach', 'subtitle': 'Jak estetycznie przejść taśmą pod kątem 90 stopni.', 'url': 'https://www.prescot.com.pl/pl/n/35'}
    ],
    'Profile': [
        {'title': 'Dlaczego profil ALU jest konieczny?', 'subtitle': 'Chłodzenie i żywotność taśmy LED.', 'url': 'https://www.prescot.com.pl/pl/n/36'},
        {'title': 'Jak dobrać profil aluminiowy do taśmy LED?', 'subtitle': 'Dobór klosza i szerokości profilu.', 'url': 'https://www.prescot.com.pl/pl/n/15'},
        {'title': 'Ciągła linia światła bez kropek', 'subtitle': 'Jak dobrać profil i taśmę do jednolitego efektu.', 'url': 'https://www.prescot.com.pl/pl/n/37'},
        {'title': 'Profile podtynkowe vs natynkowe', 'subtitle': 'Które rozwiązanie sprawdzi się u Ciebie?', 'url': 'https://www.prescot.com.pl/pl/n/38'}
    ]
}

def generate_blog_section(kategoria):
    key = 'Taśmy'
    if 'zasilacz' in str(kategoria).lower(): key = 'Zasilacze'
    elif 'sterownik' in str(kategoria).lower(): key = 'Sterowniki'
    elif 'złączk' in str(kategoria).lower() or 'zlacz' in str(kategoria).lower(): key = 'Złączki'
    elif 'profil' in str(kategoria).lower(): key = 'Profile'
    
    links = BLOGS.get(key, BLOGS['Taśmy'])
    
    html = f"""  <section
    style="font-family:inherit; margin:18px 0 28px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
    <div
      style="font-family:inherit; margin-bottom:18px; background:none !important; background-color:transparent !important; color:inherit;">
      <span
        style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px;  line-height:1.2;">
        <font color="#ffffff">Praktyczne poradniki</font>
      </span>
      <h3
        style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
        Szukasz fachowej wiedzy?
      </h3>
      <p
        style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
        Poznaj nowoczesną bazę wiedzy oświetleniowej PRESCOT. Czytaj o rozwiązaniach, które zmienią Twój projekt na
        lepsze, rozwieją wątpliwości przed zakupem oraz ułatwią ostateczny wybór.
      </p>
    </div>
    <div
      style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit; align-items:stretch;">"""

    for link in links:
        html += f"""
      <div
        style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
        <strong
          style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">{link['title']}</strong>
        <small
          style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">{link['subtitle']}</small>
        <a href="{link['url']}"
          style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
          <font color="#ffffff"><span
              style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj
              poradnik</span></font>
        </a>
      </div>"""
    
    html += """
    </div>
  </section>"""
    return html


def generate_wapro_html(html, sku, nazwa_cala="", kategoria="", seed_suffix=""):
    # Split out the existing 'Praktyczne poradniki' section if it exists
    # It usually starts with <section ... and contains Praktyczne poradniki
    
    # Simple regex to remove any section that contains "Praktyczne poradniki"
    html_cleaned = re.sub(r'<section[^>]*>(?:(?!</section>).)*?Praktyczne poradniki.*?</section>', '', html, flags=re.DOTALL|re.IGNORECASE)
    
    # 1. Strip all <h3> tags completely from the remaining HTML.
    # Wapro original description had NO <h3> tags, so removing them fixes the "2x to samo naglowki" problem.
    html_no_h3 = re.sub(r'<h3[^>]*>.*?</h3>', '', html_cleaned, flags=re.DOTALL)
    
    # 2. Clean technical noise
    noise_patterns = [
        r"Profil aluminiowy jest tu potrzebny[^.]*\.",
        r"Profil aluminiowy ułatwia równe przyklejenie[^.]*\.",
        r"Profil aluminiowy, chłodzenie i zasilacz[^.]*\.",
        r"Profil docinasz pod wymiar[^.]*\.",
        r"Profil pomaga zamknąć taśmę[^.]*\.",
        r"Profil porządkuje prowadzenie[^.]*\.",
        r"Punkty cięcia co \d+\s?mm ułatwiają dopasowanie[^.]*\.",
        r"Rolka \d+\s?m ma sens[^.]*\.",
        r"Rolka \d+\s?m wystarczy[^.]*\.",
        r"Rolka \d+\s?m jest praktyczna[^.]*\.",
        r"Zasilacz dobierz pod \d+V[^.]*\.",
        r"Zasilacz pracuje najlepiej[^.]*\.",
        r"Format rolka \d+m[^.]*\."
    ]
    for noise in noise_patterns:
        html_no_h3 = re.sub(noise, '', html_no_h3)

    benefit_1m = spin("{Wersja cięta z metra to świetny wybór do punktowych projektów, gdzie kupujesz dokładnie tyle, ile potrzebujesz do swojego montażu.|Odcinki cięte na metry ułatwiają realizację precyzyjnych oświetleń bez konieczności magazynowania nadwyżek.|Kupując taśmę na metry, optymalizujesz koszty i dostajesz idealną ilość materiału do krótszych formatek i wnęk.}", sku + seed_suffix)
    benefit_50m = spin("{Rolka 50-metrowa to wygodne rozwiązanie dla instalatorów, pozwalające na swobodne docinanie długich odcinków na bieżąco podczas pracy.|Duża rolka 50m zapewnia świetną powtarzalność barwy na całej długości bardziej rozbudowanej inwestycji.|Format 50m ułatwia pracę przy rozległych zabudowach, gdzie konkretny wymiar ustala się z reguły dopiero na miejscu montażu.}", sku + seed_suffix)
    benefit_100m = spin("{Fabryczna rolka 100-metrowa to maksymalna wydajność przy hurtowych instalacjach, gwarantująca w pełni spójną partię diod w całym obiekcie.|Rolka o długości 100m to znakomity wybór na duże realizacje komercyjne, gdzie liczy się szybkość pracy i jednolitość światła we wszystkich pomieszczeniach.|Zapas 100 metrów na jednej rolce pozwala na płynne realizowanie największych projektów liniowych bez najmniejszych obaw o różnice w barwie.}", sku + seed_suffix)

    added_benefit = False

    # 3. Spin the content inside <p> tags.
    def spin_p_tag(match):
        nonlocal added_benefit
        p_attrs = match.group(1)
        p_content = match.group(2)
        
        # Apply spin patterns to p_content
        for pattern, replacement in SPIN_PATTERNS:
            p_content = re.sub(pattern, replacement, p_content)
            
        p_content = spin(p_content, sku + seed_suffix)
        
        # Clean up any remaining double spaces from removals
        p_content = re.sub(r'\s{2,}', ' ', p_content).strip()
        
        # Append length benefit if applicable
        if not added_benefit and "taśma" in nazwa_cala.lower():
            if re.search(r'\b1m\b', nazwa_cala, re.IGNORECASE):
                p_content += " " + benefit_1m
            elif re.search(r'\b50m\b', nazwa_cala, re.IGNORECASE):
                p_content += " " + benefit_50m
            elif re.search(r'\b100m\b', nazwa_cala, re.IGNORECASE):
                p_content += " " + benefit_100m
            added_benefit = True
            
        return f'<p{p_attrs}>{p_content}</p>'

    html_spun = re.sub(r'<p([^>]*)>(.*?)</p>', spin_p_tag, html_no_h3, flags=re.DOTALL)
    
    # Do the same for <li> tags if any (e.g. Sterowniki)
    def spin_li_tag(match):
        li_attrs = match.group(1)
        li_content = match.group(2)
        for pattern, replacement in SPIN_PATTERNS:
            li_content = re.sub(pattern, replacement, li_content)
        li_content = spin(li_content, sku + seed_suffix)
        li_content = re.sub(r'\s{2,}', ' ', li_content).strip()
        return f'<li{li_attrs}>{li_content}</li>'
        
    html_spun = re.sub(r'<li([^>]*)>(.*?)</li>', spin_li_tag, html_spun, flags=re.DOTALL)

    # 4. Append new Blog section based on Kategoria
    new_blog_section = generate_blog_section(kategoria)
    html_final = html_spun.strip() + "\n" + new_blog_section

    return html_final
