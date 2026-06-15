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
        "{Rolka o długości 5m to optymalny format do średnich instalacji lub krótszych odcinków|Wersja 5-metrowa świetnie nadaje się do standardowych mebli i pojedynczych stref oświetleniowych|Pięciometrowa zwijka ułatwia wykonanie kilku krótszych linii światła w jednym meblu}."
    ),
    # Rolka 50m
    (
        r"Format rolka 50m jest wygodny przy dłuższych, powtarzalnych realizacjach: regałach, zabudowach, kilku pomieszczeniach albo pracy instalacyjnej, gdzie odcinki docinasz dopiero na miejscu\.",
        "{Rolka 50m to doskonały wybór dla instalatorów i przy dużych projektach|Wersja 50-metrowa ułatwia pracę przy rozbudowanych, wielostrefowych inwestycjach|Zwijka o długości 50 metrów to oszczędność i wygoda przy seryjnym oświetlaniu regałów czy dużych sufitów}, {pozwalając na docinanie odcinków na bieżąco|gdzie precyzyjny wymiar ustalany jest dopiero na budowie|oferując maksymalną elastyczność podczas montażu}."
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

def generate_wapro_html(html, sku):
    # DONT STRIP SECTIONS. The user wants the original visual layout, but WITHOUT <h3> tags, 
    # and WITH spun text inside the <p> tags.
    
    # 1. Strip all <h3> tags completely.
    # Wapro original description had NO <h3> tags, so removing them fixes the "2x to samo naglowki" problem.
    html_no_h3 = re.sub(r'<h3[^>]*>.*?</h3>', '', html, flags=re.DOTALL)
    
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

    # 3. Spin the content inside <p> tags.
    def spin_p_tag(match):
        p_attrs = match.group(1)
        p_content = match.group(2)
        
        # Apply spin patterns to p_content
        for pattern, replacement in SPIN_PATTERNS:
            p_content = re.sub(pattern, replacement, p_content)
            
        p_content = spin(p_content, sku)
        
        # Clean up any remaining double spaces from removals
        p_content = re.sub(r'\s{2,}', ' ', p_content).strip()
        
        return f'<p{p_attrs}>{p_content}</p>'

    html_spun = re.sub(r'<p([^>]*)>(.*?)</p>', spin_p_tag, html_no_h3, flags=re.DOTALL)
    
    # Do the same for <li> tags if any (e.g. Sterowniki)
    def spin_li_tag(match):
        li_attrs = match.group(1)
        li_content = match.group(2)
        for pattern, replacement in SPIN_PATTERNS:
            li_content = re.sub(pattern, replacement, li_content)
        li_content = spin(li_content, sku)
        li_content = re.sub(r'\s{2,}', ' ', li_content).strip()
        return f'<li{li_attrs}>{li_content}</li>'
        
    html_spun = re.sub(r'<li([^>]*)>(.*?)</li>', spin_li_tag, html_spun, flags=re.DOTALL)

    return html_spun
