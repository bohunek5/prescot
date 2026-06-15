import re
import random

COLOR_VARIANTS = {
    "3000K": {
        "titles": [
            "Przyjemna biel do wnętrz, które mają wyglądać naturalnie",
            "Światło o temperaturze 3K do domowego relaksu",
            "Ciepła tonacja 3000K, idealna do sypialni i salonu",
            "Relaksujące światło o barwie 3000K",
            "Przytulna atmosfera dzięki temperaturze 3K"
        ],
        "texts": [
            "Ciepła biel (3000K) świetnie komponuje się z klasycznymi wnętrzami i materiałami takimi jak drewno czy cegła. Najczęściej wybierana do salonów, sypialni i stref relaksu jako główne lub dekoracyjne źródło światła.",
            "Barwa 3K ociepla wnętrze i sprzyja wyciszeniu. Idealnie nadaje się do hoteli, stref wypoczynkowych w domu oraz jako podświetlenie wnęk i półek w pokojach dziennych.",
            "Temperatura 3000K to sprawdzone rozwiązanie do przestrzeni, w których dominuje funkcja relaksacyjna. Dobry wybór do oświetlenia wieczornego w salonach oraz nad stołem jadalnianym.",
            "Światło o barwie 3K (około 3000 Kelwinów) nadaje pomieszczeniom ciepły, przytulny charakter. Znakomicie eksponuje strukturę drewna i ciepłe kolory ścian."
        ]
    },
    "4000K": {
        "titles": [
            "Czysta, naturalna biel do pracy i ekspozycji",
            "Neutralne oświetlenie 4000K wspierające skupienie",
            "Światło o temperaturze 4K, które nie przekłamuje kolorów",
            "Idealny kompromis: naturalna biel 4K"
        ],
        "texts": [
            "Barwa 4000K gwarantuje czysty, neutralny odcień – bez żółtych ani niebieskich domieszek. Idealna do stref roboczych, gabinetów, przestrzeni komercyjnych oraz nad lustrem do precyzyjnego makijażu.",
            "Światło o temperaturze 4K (4000 Kelwinów) wspiera skupienie i zachowuje naturalne kolory oświetlanych przedmiotów. To najczęstszy wybór do nowoczesnych kuchni, przedpokojów oraz witryn wystawowych.",
            "Neutralna biel 4000K nie męczy wzroku i poprawia koncentrację. Stanowi niezawodny wybór do oświetlenia zadaniowego: w biurach, nad kuchennymi wyspami roboczymi czy w garderobach.",
            "Barwa 4K to optymalny środek między ciepłym a zimnym oświetleniem. Znajduje zastosowanie w minimalistycznych aranżacjach i pomieszczeniach wymagających bardzo dobrej widoczności bez odczucia chłodu."
        ]
    },
    "6000K": {
        "titles": [
            "Mocne, sterylne światło o barwie 6K",
            "Zimna biel dla maksymalnego kontrastu i czystości",
            "Chłodna temperatura 6000K do zadań specjalnych",
            "Barwa 6K – stymulujące i ostre oświetlenie"
        ],
        "texts": [
            "Zimna biel (około 6000K) podbija wrażenie czystości i kontrastu. Sprawdzi się w pomieszczeniach technicznych, garażach, zapleczach, ekspozycjach i surowszych aranżacjach.",
            "Światło o barwie 6K zapewnia doskonałą widoczność detali i podbija wrażenie sterylności. Najlepszy wybór do stanowisk wymagających precyzji oraz miejsc technicznych.",
            "Chłodna tonacja 6K optycznie powiększa przestrzeń i nadaje jej nowoczesny wyraz. Idealna do podświetlania jasnych powierzchni, reklam oraz stref roboczych w warsztatach."
        ]
    },
    "6500K": {
        "titles": [
            "Mocne, sterylne światło o barwie 6.5K",
            "Zimna biel dla maksymalnego kontrastu",
            "Chłodna temperatura 6500K do zadań specjalnych",
            "Barwa 6.5K – stymulujące oświetlenie dzienne"
        ],
        "texts": [
            "Zimna biel (6500K) podbija wrażenie czystości i kontrastu. Sprawdzi się w laboratoriach, warsztatach, halach produkcyjnych i wszędzie tam, gdzie potrzebujesz ostrego widzenia.",
            "Światło o barwie 6.5K gwarantuje doskonałą widoczność najdrobniejszych detali. To idealny odcień do magazynów oraz nowoczesnych, technicznych przestrzeni komercyjnych.",
            "Temperatura 6500K to chłodny, bardzo jasny odcień światła, przypominający światło dzienne. Niezbędna tam, gdzie liczy się bezkompromisowa wyrazistość i sterylność."
        ]
    },
    "2700K": {
        "titles": [
            "Bardzo ciepła barwa 2.7K do wyjątkowo nastrojowych wnętrz",
            "Głębokie, relaksujące światło o temperaturze 2700K",
            "Oświetlenie 2.7K: Atmosfera i przytulność na pierwszym miejscu"
        ],
        "texts": [
            "Ciepła biel 2.7K (2700 Kelwinów) mocno ociepla drewno, kamień, beże i elementy dekoracyjne. Wybierz ją do sypialni, restauracji, hotelu lub ekspozycji, w której światło ma budować klimat.",
            "Barwa 2700K to bardzo ciepły odcień, zbliżony do światła tradycyjnej żarówki. Doskonale sprawdza się w strefach wieczornego relaksu i w miejscach, gdzie całkowicie unikamy technicznego chłodu.",
            "Temperatura 2.7K wprowadza do wnętrza intymną i bardzo przytulną atmosferę. To popularny wybór do klimatycznych kawiarni, domowych salonów oraz designerskich opraw."
        ]
    },
    "2500K": {
        "titles": [
            "Światło, które sprzedaje świeżość pieczywa",
            "Specjalistyczna barwa 2.5K stworzona do ekspozycji wypieków",
            "Złota tonacja 2500K idealna do piekarni i cukierni",
            "Światło 2500K dedykowane do chleba i słodkich wypieków"
        ],
        "texts": [
            "Ten wariant 2.5K jest przygotowany pod ladę piekarniczą, regał z bułkami i ekspozycję wypieków, gdzie kolor produktu decyduje o apetyczności. Ciepłe światło pięknie podbija złotą skórkę chleba, chałek i rogalików.",
            "Specjalistyczna barwa 2500K skutecznie eksponuje świeże wypieki, likwidując blady, marketowy odblask. Dzięki temperaturze 2.5K pieczywo, drożdżówki i ciasta zyskują głęboki, złocisty i wyjątkowo zachęcający wygląd.",
            "Światło o temperaturze 2500K zostało stworzone specjalnie do podkreślania walorów wizualnych pieczywa. Bardzo ciepły, złoty odcień sprawia, że asortyment na ekspozycji wygląda na wyjęty prosto z pieca."
        ]
    },
    "10000K": {
        "titles": [
            "Ekstremalnie zimna barwa 10K do zadań specjalnych",
            "Lodowata biel 10000K dla maksymalnie ostrego efektu"
        ],
        "texts": [
            "Zimna biel 10000K daje wyrazisty, lodowaty charakter światła. Wybierz ją do ekspozycji technicznych, akwariów morskich, efektów specjalnych i akcentów reklamowych.",
            "Barwa 10K to ekstremalnie chłodny odcień, zarezerwowany dla specyficznych zastosowań. Świetnie wygląda w nowoczesnych banerach reklamowych, przy ekspozycji biżuterii czy jako element oświetlenia w specjalistycznych instalacjach."
        ]
    },
    "RGBW + 3000K": {
        "titles": [
            "Pełna paleta kolorów plus ciepła biel 3K",
            "RGBW + 3000K: Multikolor i relaksujące światło w jednym",
            "Zmieniaj kolory lub włącz przyjemne oświetlenie 3K"
        ],
        "texts": [
            "Taśma łączy wielokolorowe diody RGB z osobnym chipem białym 3K (3000K). Możesz ustawić dowolny kolor z palety, a w razie potrzeby przełączyć na naturalne, ciepłe oświetlenie do relaksu.",
            "Wersja RGBW (z białą diodą 3000K) to idealny kompromis. Baw się kolorowym światłem, a gdy potrzebujesz wyciszenia, uruchom oddzielny kanał ciepłej bieli 3K, która stworzy przytulny nastrój.",
            "Dzięki chipowi RGB i dodatkowej diodzie 3K otrzymujesz dwa źródła światła na jednym pasku. Kreuj nieskończoną ilość barw albo ciesz się klasycznym, ciepłym światłem 3000K."
        ]
    },
    "RGBW + 4000K": {
        "titles": [
            "Pełna paleta kolorów plus neutralna biel 4K",
            "RGBW + 4000K: Kolorowa zabawa i światło do pracy",
            "Paleta barw oraz czyste oświetlenie dzienne 4K"
        ],
        "texts": [
            "Wariant łączący paletę RGB z dedykowaną diodą o temperaturze 4K. Pozwala na tworzenie efektownych kolorowych iluminacji, a po przełączeniu na biel dostarcza neutralnego światła wspierającego skupienie.",
            "Taśma RGBW z barwą 4000K to wszechstronność w czystej postaci. Wybierasz dowolny kolor z gamy RGB lub ustawiasz czysty, pozbawiony odcieni żółtego kolor biały 4K – idealny do pracy i codziennego użytku.",
            "Zintegrowana dioda biała 4K zapewnia idealne, naturalne światło wtedy, kiedy go potrzebujesz. Oprócz tego masz dostęp do tysięcy barw z palety RGB, dzięki czemu taśma jest uniwersalna."
        ]
    }
}

def randomize_color_blocks(html_content):
    # Regex to find the color section. We look for <font color="#ffffff">Barwa ... (XXXXK)</font>
    # and then capture the <h3> and <p> tags following it, inside the same <section>.
    
    # We will use a regex that matches the <section>...</section> exactly.
    # Actually, we can just find all matches of the color label and replace the content.
    
    def replacer(match):
        full_match = match.group(0)
        temp_key = match.group(1) # e.g., 3000K, 2500K, RGBW + 3000K
        
        # Clean the key to match dictionary
        key_mapped = temp_key
        if 'RGBW' in full_match:
            if '3000K' in full_match:
                key_mapped = "RGBW + 3000K"
            elif '4000K' in full_match:
                key_mapped = "RGBW + 4000K"
                
        if key_mapped in COLOR_VARIANTS:
            new_title = random.choice(COLOR_VARIANTS[key_mapped]["titles"])
            new_text = random.choice(COLOR_VARIANTS[key_mapped]["texts"])
            
            # Now replace the existing <h3>...</h3> and <p>...</p> inside this section
            # The structure in HTML is roughly:
            # </span>
            # <h3 style="..."> TITLE </h3>
            # <p style="..."> TEXT </p>
            
            # We can replace the contents of h3 and p
            section_html = full_match
            section_html = re.sub(r'(<h3[^>]*>)(.*?)(</h3>)', rf'\g<1>\n    {new_title}\n  \g<3>', section_html, flags=re.DOTALL)
            section_html = re.sub(r'(<p[^>]*>)(.*?)(</p>)', rf'\g<1>\n    {new_text}\n  \g<3>', section_html, flags=re.DOTALL)
            return section_html
            
        return full_match

    # A color block section looks like:
    # <section ...> ... <font ...>Barwa ciepła (3000K)</font> ... <h3>...</h3> ... <p>...</p> ... </section>
    pattern = r'<section[^>]*>.*?<font[^>]*>Barwa [^\(]*\(([\d]+K)\)</font>.*?</section>|<section[^>]*>.*?<font[^>]*>Barwa (RGBW \+ [\d]+K)</font>.*?</section>'
    
    # Let's combine them simply:
    # We will match the entire <section> that contains a <font>Barwa ...</font>
    pattern2 = r'<section[^>]*>[\s\S]*?<font color="#ffffff">Barwa (?:[^\(]*\(([\d]+K)\)|(RGBW \+ [\d]+K))</font>[\s\S]*?</section>'
    
    def unified_replacer(match):
        full_match = match.group(0)
        k_value = match.group(1)
        rgbw_value = match.group(2)
        
        temp_key = k_value if k_value else rgbw_value
        
        if temp_key in COLOR_VARIANTS:
            new_title = random.choice(COLOR_VARIANTS[temp_key]["titles"])
            new_text = random.choice(COLOR_VARIANTS[temp_key]["texts"])
            
            section_html = full_match
            section_html = re.sub(r'(<h3[^>]*>)([\s\S]*?)(</h3>)', rf'\g<1>\n    {new_title}\n  \g<3>', section_html)
            section_html = re.sub(r'(<p[^>]*>)([\s\S]*?)(</p>)', rf'\g<1>\n    {new_text}\n  \g<3>', section_html)
            return section_html
            
        return full_match

    result = re.sub(pattern2, unified_replacer, html_content)
    return result

if __name__ == "__main__":
    test_html = """
    <section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
      <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px;  line-height:1.2;">
        <font color="#ffffff">Barwa ciepła (2500K)</font>
      </span>

      <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
        Miękkie, nastrojowe światło do drewna i ciepłych wnętrz
      </h3>

      <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
        Ciepła biel 2500K ociepla drewno, kamień, beże i elementy dekoracyjne. Wybierz ją do salonu, sypialni, restauracji, hotelu, garderoby lub ekspozycji, w której światło ma budować klimat, a nie techniczny chłód.
      </p>
    </section>
    """
    print(randomize_color_blocks(test_html))
