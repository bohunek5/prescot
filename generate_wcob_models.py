#!/usr/bin/env python3
"""
Generator script to add new WCOB LED strips (24WCOB320WW5IP62, 24WCOB320NW5IP62, 24WCOB320W5IP62, 24WCOB280CCT5IP62)
to prescot/index.html across all 4 platforms (WAPRO, TIM, ALLEGRO, SHOPER).
"""
import re
import html

WCOB_MODELS = [
    {
        "id": "24WCOB320WW5IP62",
        "ean": "5905475368349",
        "name_full": "Taśma LED WCOB 24V 320LED 10W/m IP62 3000K Biała Ciepła 5m",
        "badge_label": "WCOB IP62 • 3000K • 10W/m • 1400lm/m • Ra>90 • 5m",
        "cct": "3000K",
        "color_name": "Biała Ciepła (WW)",
        "voltage": "24V",
        "power": "10W/m",
        "power_total": "50W / 5m",
        "current": "0.41 A/m",
        "diodes": "320/m",
        "diode_type": "WCOB (White COB)",
        "cri": "Ra > 90",
        "angle": "180°",
        "ip": "IP62",
        "cut_section": "25mm",
        "dimensions": "5000 x 8 mm",
        "lifespan": "30 000h",
        "temp_range": "-20°C ~ +40°C",
        "energy_class": "E",
        "lumen": "1400lm/m",
        "efficiency": "140lm/W",
        "warranty": "5 lat (60 miesięcy)",
        "dimmable": "TAK (PWM 24V)",
        "max_length_single": "5m",
        "desc_wapro": {
            "h1": "Estetyka White COB i ochrona IP62 — idealnie gładka linia bez żółtego paska",
            "p1": "Taśma <b>WCOB (White COB)</b> to nowa generacja oświetlenia liniowego, która eliminuje największą wadę klasycznych taśm COB — jaskrawożółty pasek luminoforu. W stanie spoczynku taśma prezentuje się jako <b>czysta, elegancka, biała linia</b>, idealnie komponując się z nowoczesną zabudową i profilami bez mlecznego klosza. Gęstość <b>320 diod/m</b> zapewnia w 100% jednolite, bezpunktowe światło o szerokim kącie emisji <b>180°</b> i wysokim współczynniku oddawania barw <b>Ra &gt; 90</b>.",
            "h2": "Zastosowanie w architekturze wnętrz i strefach o podwyższonej wilgotności",
            "p2": "Barwa <b>3000K (ciepła biel)</b> wprowadza przytulny, elegancki klimat, doskonale podkreślając strukturę drewna, forniru, tkanin oraz kamienia naturalnego. Dzięki powłoce silikonowej o klasie szczelności <b>IP62</b> taśma jest zabezpieczona przed kurzem, pyłem i wilgocią, co czyni ją bezkonkurencyjnym wyborem do podświetlenia blatów kuchennych, cokołów, półek łazienkowych, wnęk sufitowych oraz mebli biurowych i hotelowych.",
            "h3": "Parametry elektryczne, termika i wytyczne montażowe",
            "p3": "Napięcie zasilania <b>24V DC</b> oraz prąd <b>0.41 A/m</b> zapewniają wysoką stabilność pracy i minimalizują spadki napięcia na odcinku 5m. Moduł cięcia co <b>25 mm</b> umożliwia precyzyjne dopasowanie do każdego wymiaru wnęki meblowej. Dla zachowania pełnej <b>5-letniej gwarancji</b> taśmę należy montować w profilach aluminiowych pełniących rolę radiatora oraz stosować zasilacze LED z <b>25% zapasem mocy</b> (mnożnik x1.25). Łączenie odcinków zaleca się wykonywać za pomocą stacji lutowniczej kolbowej o temperaturze do 320°C."
        },
        "desc_tim": {
            "h1": "24WCOB320WW5IP62 - profesjonalna taśma LED WCOB 24V 10W/m IP62 do instalacji B2B",
            "p1": "Model <b>24WCOB320WW5IP62</b> to profesjonalne źródło światła liniowego oparte na technologii <b>WCOB (White COB)</b> z gęstością <b>320 diod/m</b> i mocą <b>10W/m</b>. Oferuje strumień świetlny <b>1400 lm/m</b> przy wysokiej sprawności <b>140 lm/W</b> oraz współczynniku oddawania barw <b>Ra &gt; 90</b>. Zoptymalizowana pod kątem instalatorów i projektantów oświetlenia wymagających bezpunktowej linii światła.",
            "h2": "Zastosowanie projektowe: oświetlenie meblowe, wnękowe i strefy wilgotne (IP62)",
            "p2": "Klasa ochrony <b>IP62</b> uzyskana dzięki bezżółtej powłoce silikonowej pozwala na bezpieczny montaż w przestrzeniach narażonych na wilgoć i parę wodną (kuchnie, strefy podszafkowe, łazienki poza strefą bezpośredniego strumienia wody). Ciepła temperatura barwowa <b>3000K</b> gwarantuje naturalne odwzorowanie barw bez zniekształceń materiałowych.",
            "h3": "Wytyczne projektowe i instalacyjne — dobór zasilacza i chłodzenia",
            "p3": "Zasilanie stałonapięciowe <b>24V DC</b>. Maksymalny odcinek jednostronnie zasilany wynosi <b>5 metrów</b>. Moduł cięcia wynosi <b>25mm</b>. Wymagany montaż na podłożu odprowadzającym ciepło (profil aluminiowy LED). Dobór mocy zasilacza: <code>P_zas &gt;= P_taśmy * 1.25</code> (dla 5m zalecany zasilacz min. 65W 24V). Produkt objęty <b>5-letnią gwarancją producenta</b>."
        },
        "desc_allegro": {
            "h1": "Taśma LED WCOB 24V 10W/m IP62 3000K Ciepła 5m — Czysta Linia Światła bez Żółtego Paska",
            "p1": "Szukasz taśmy LED, która po wyłączeniu nie straszy brzydkim, żółtym paskiem? Wybierz technologię <b>WCOB (White COB)</b> marki <b>Prescot LED</b>! Pasek pokryty jest estetyczną białą powłoką silikonową, dzięki czemu prezentuje się nieskazitelnie nawet w płytkich, widocznych profilach. Po włączeniu uzyskujesz <b>idealnie gładką, jednolitą linię światła (320 LED/m)</b> bez żadnych widocznych punktów czy cieni.",
            "h2": "Ciepła barwa 3000K i ochrona IP62 — idealna do kuchni, salonu i łazienki",
            "p2": "Barwa <b>3000K</b> tworzy przytulną, elegancką atmosferę w salonie, sypialni oraz kuchni pod szafkami. Klasa <b>IP62</b> zabezpiecza diody przed zachlapaniem, parą wodną i kurzem — taśmę można łatwo przetrzeć wilgotną szmatką bez ryzyka uszkodzenia elektroniki. Wysoki wskaźnik <b>CRI Ra &gt; 90</b> sprawia, że potrawy, meble i kolory ścian wyglądają naturalnie i soczyście.",
            "h3": "Prosty montaż na taśmie samoprzylepnej i 5 lat gwarancji",
            "p3": "Mocna taśma dwustronna na odwrocie ułatwia montaż w profilu aluminiowym. Taśmę można bezpiecznie ciąć co <b>2.5 cm (25 mm)</b> w wyznaczonych miejscach. Bezpieczne napięcie <b>24V</b> zapobiega przegrzewaniu i spadkom jasności. <b>Aż 5 lat gwarancji</b> daje Ci pewność, że oświetlenie posłuży bezawaryjnie przez długie lata."
        },
        "desc_shoper": {
            "h1": "24WCOB320WW5IP62 - Taśma LED WCOB 24V 320LED 10W/m IP62 3000K Biała Ciepła 5m",
            "p1": "<b>Prescot WCOB 24V IP62 3000K</b> to innowacyjna taśma LED nowej generacji. Dzięki wyeliminowaniu żółtego luminoforu na rzecz jednolitej białej powłoki silikonowej, taśma gwarantuje perfekcyjną estetykę zarówno przy włączonym, jak i wyłączonym oświetleniu. Zapewnia <b>1400 lm/m</b>, gęstość <b>320 diod/m</b> oraz kąt świecenia <b>180°</b>.",
            "h2": "Zastosowanie i korzyści użytkowe",
            "p2": "Dedykowana do oświetlenia podszafkowego, sufitów podwieszanych, mebli kuchennych, garderób i łazienek (ochrona <b>IP62</b>). Ciepła biel <b>3000K</b> wprowadza do wnętrza harmonię i przytulność, a odwzorowanie barw <b>Ra &gt; 90</b> gwarantuje najwyższą jakość wizualną.",
            "h3": "Specyfikacja techniczna i zasady montażu",
            "p3": "Napięcie: <b>24V DC</b>, Moc: <b>10W/m</b>, Cięcie: co <b>25mm</b>, Szerokość: <b>8mm</b>. Wymaga montażu w profilu aluminiowym pełniącym funkcję radiatora. <b>5 lat gwarancji</b> producenta Prescot."
        }
    },
    {
        "id": "24WCOB320NW5IP62",
        "ean": "5905475368356",
        "name_full": "Taśma LED WCOB 24V 320LED 10W/m IP62 4000K Biała Neutralna 5m",
        "badge_label": "WCOB IP62 • 4000K • 10W/m • 1450lm/m • Ra>90 • 5m",
        "cct": "4000K",
        "color_name": "Biała Neutralna (NW)",
        "voltage": "24V",
        "power": "10W/m",
        "power_total": "50W / 5m",
        "current": "0.41 A/m",
        "diodes": "320/m",
        "diode_type": "WCOB (White COB)",
        "cri": "Ra > 90",
        "angle": "180°",
        "ip": "IP62",
        "cut_section": "25mm",
        "dimensions": "5000 x 8 mm",
        "lifespan": "30 000h",
        "temp_range": "-20°C ~ +40°C",
        "energy_class": "D",
        "lumen": "1450lm/m",
        "efficiency": "145lm/W",
        "warranty": "5 lat (60 miesięcy)",
        "dimmable": "TAK (PWM 24V)",
        "max_length_single": "5m",
        "desc_wapro": {
            "h1": "Biel neutralna 4000K i estetyka White COB — wysoka wydajność 145 lm/W",
            "p1": "Model <b>24WCOB320NW5IP62</b> w barwie neutralnej <b>4000K</b> to uniwersalny standard oświetlenia roboczego i dekoracyjnego. Zastosowanie technologii <b>WCOB (White COB)</b> całkowicie usuwa nieestetyczny żółty pasek diodowy, zastępując go estetyczną białą powłoką. Taśma osiąga imponującą jasność <b>1450 lm/m</b> przy klasie energetycznej <b>D</b> oraz skuteczności <b>145 lm/W</b>, zachowując bezwzględną ciągłość linii światła (brak kropek).",
            "h2": "Uniwersalne zastosowanie w strefach roboczych, biurach i łazienkach",
            "p2": "Temperatura barwowa <b>4000K</b> odpowiada naturalnemu światłu dziennemu, sprzyja koncentracji i nie męczy wzroku. Stopień ochrony <b>IP62</b> zabezpiecza taśmę przed kurzem, pyłem i skroploną wilgocią. Rekomendowana do oświetlenia blatów roboczych, wysp kuchennych, luster łazienkowych, ciągów komunikacyjnych, korytarzy oraz nowoczesnych biur i gabinetów.",
            "h3": "Instalacja, termika i wytyczne zasilania 24V",
            "p3": "Zasilanie napięciem <b>24V DC</b> (0.41 A/m) pozwala na bezproblemowe zasilanie odcinków do 5m bez spadku jasności. Precyzyjny moduł cięcia co <b>25 mm</b> ułatwia estetyczny montaż. Bezwzględnie wymagane jest klejenie taśmy na odtłuszczonym profilu aluminiowym (radiatorze) oraz dobranie zasilacza z <b>zapasem 25%</b>. Produkt objęty pełną <b>5-letnią gwarancją producenta</b>."
        },
        "desc_tim": {
            "h1": "24WCOB320NW5IP62 - profesjonalna taśma LED WCOB 24V 10W/m IP62 4000K do projektów",
            "p1": "Taśma LED <b>24WCOB320NW5IP62</b> to wysokosprawne źródło światła liniowego <b>145 lm/W (1450 lm/m)</b> o barwie neutralnej <b>4000K</b>. Wykonana w technologii <b>WCOB</b> z powłoką silikonową <b>IP62</b>, eliminującą żółty pasek i chroniącą przed czynnikami środowiskowymi. Kąt rozsyłu <b>180°</b> i wskaźnik <b>Ra &gt; 90</b> gwarantują najwyższą jakość oświetlenia technicznego.",
            "h2": "Przeznaczenie techniczne: oświetlenie zadaniowe, komercyjne i strefy wilgotne",
            "p2": "Neutralna barwa <b>4000K</b> znajduje zastosowanie w obiektach użyteczności publicznej, handlu, hotelarstwie oraz rezydencjach prywatnych. Klasa <b>IP62</b> chroni komponenty przed osiadaniem kurzu i wilgocią, co podnosi niezawodność instalacji w wymagających warunkach kubaturowych.",
            "h3": "Specyfikacja elektryczna i montażowa dla wykonawców",
            "p3": "Napięcie robocze: <b>24V DC</b>. Prąd: <b>0.41 A/m</b>. Maksymalny odcinek zasilany jednostronnie: <b>5 m</b>. Sekcja cięcia: <b>25 mm</b>. Montaż wyłącznie w profilach aluminiowych LED. Dobór zasilacza o stałym napięciu 24V z min. 25% rezerwą mocy. Produkt objęty <b>5-letnią gwarancją</b>."
        },
        "desc_allegro": {
            "h1": "Taśma LED WCOB 24V 10W/m IP62 4000K Neutralna 5m — Idealna Linia Światła bez Kropek",
            "p1": "Postaw na nowoczesną technologię <b>WCOB (White COB)</b> od <b>Prescot LED</b>! Taśma charakteryzuje się brakiem żółtego paska fosforu — po wyłączeniu widzisz <b>czysty, elegancki biały pasek</b>, który doskonale pasuje do białych mebli i profili. Po włączeniu otrzymujesz <b>idealnie jednolitą linię światła</b> o wysokiej jasności <b>1450 lm/m</b>.",
            "h2": "Neutralna barwa dzienna 4000K i odporność na wilgoć IP62",
            "p2": "Barwa <b>4000K (neutralna biel)</b> to najchętniej wybierane światło do kuchni, biura i łazienki — nie jest ani za żółte, ani za niebieskie. Odwzorowanie kolorów <b>CRI Ra &gt; 90</b> sprawia, że przedmioty wyglądają naturalnie jak w świetle słonecznym. Powłoka <b>IP62</b> zabezpiecza taśmę przed zachlapaniem wodą, parą i kurzem.",
            "h3": "Łatwy montaż, zasilanie 24V i 5 lat gwarancji",
            "p3": "Taśma wyposażona jest w mocny klej montażowy. Możesz ją ciąć co <b>25 mm</b> nożyczkami. Bezpieczne napięcie <b>24V</b> zapewnia długą żywotność i brak nagrzewania. <b>5 lat pełnej gwarancji</b> to pewność bezpiecznego zakupu na lata."
        },
        "desc_shoper": {
            "h1": "24WCOB320NW5IP62 - Taśma LED WCOB 24V 320LED 10W/m IP62 4000K Biała Neutralna 5m",
            "p1": "<b>Prescot WCOB 24V IP62 4000K</b> to nowoczesna taśma LED łącząca technologię ciągłej linii światła WCOB z estetyką białego paska bez żółtego luminoforu. Osiąga znakomitą wydajność <b>1450 lm/m (145 lm/W)</b> przy gęstości <b>320 diod/m</b> i kącie <b>180°</b>.",
            "h2": "Zastosowanie w projektach oświetleniowych",
            "p2": "Uniwersalna neutralna barwa <b>4000K</b> sprawdzi się idealnie pod szafkami kuchennymi, w łazienkach (ochrona <b>IP62</b>), biurach i garderobach. Wskaźnik <b>Ra &gt; 90</b> zapewnia wierne odwzorowanie kolorów otoczenia.",
            "h3": "Dane techniczne i montaż",
            "p3": "Napięcie: <b>24V DC</b>, Moc: <b>10W/m</b>, Moduł cięcia: <b>25mm</b>, Szerokość: <b>8mm</b>. Wymaga instalacji w profilu aluminiowym. Produkt objęty <b>5-letnią gwarancją</b> Prescot."
        }
    },
    {
        "id": "24WCOB320W5IP62",
        "ean": "5905475368363",
        "name_full": "Taśma LED WCOB 24V 320LED 10W/m IP62 6000K Biała Zimna 5m",
        "badge_label": "WCOB IP62 • 6000K • 10W/m • 1350lm/m • Ra>90 • 5m",
        "cct": "6000K",
        "color_name": "Biała Zimna (W / CW)",
        "voltage": "24V",
        "power": "10W/m",
        "power_total": "50W / 5m",
        "current": "0.41 A/m",
        "diodes": "320/m",
        "diode_type": "WCOB (White COB)",
        "cri": "Ra > 90",
        "angle": "180°",
        "ip": "IP62",
        "cut_section": "25mm",
        "dimensions": "5000 x 8 mm",
        "lifespan": "30 000h",
        "temp_range": "-20°C ~ +40°C",
        "energy_class": "E",
        "lumen": "1350lm/m",
        "efficiency": "135lm/W",
        "warranty": "5 lat (60 miesięcy)",
        "dimmable": "TAK (PWM 24V)",
        "max_length_single": "5m",
        "desc_wapro": {
            "h1": "Nowoczesna biel zimna 6000K i estetyka White COB — linia światła hi-tech",
            "p1": "Taśma LED <b>24WCOB320W5IP62</b> w barwie zimnej <b>6000K</b> to rozwiązanie stworzone do nowoczesnych wnętrz, ekspozycji komercyjnych i projektów hi-tech. Dzięki technologii <b>WCOB (White COB)</b> taśma zachowuje perfekcyjną białą kolorystykę paska w stanie spoczynku (brak żółtego zabarwienia), a po włączeniu emituje <b>krystalicznie czystą, jednolitą linię światła (1350 lm/m)</b> bez widocznych punktów diodowych.",
            "h2": "Zastosowanie w nowoczesnej architekturze, gablotach i strefach wilgotnych",
            "p2": "Zimna biel <b>6000K</b> podkreśla kontrast, biel powierzchni, metal, szkło oraz nowoczesne materiały kompozytowe. Silikonowa powłoka ochronna <b>IP62</b> zabezpiecza diody przed wilgocią, kurzem i zabrudzeniami, czyniąc tę taśmę idealną do podświetlenia witryn sklepowych, gablot jubilerskich, łazienek w stylu industrialnym oraz nowoczesnych przestrzeni laboratoryjnych i biurowych.",
            "h3": "Parametry zasilania, trwałość i zalecenia montażowe",
            "p3": "Napięcie robocze <b>24V DC</b> zapewnia stabilną pracę bez spadków napięcia na całej długości 5m. Moduł cięcia co <b>25 mm</b> umożliwia dokładne dopasowanie długości odcinka. Do prawidłowej pracy wymagane jest przyklejenie taśmy do profilu aluminiowego odprowadzającego ciepło oraz zastosowanie zasilacza 24V z <b>25% rezerwą mocy</b>. Gwarancja producenta: <b>5 lat</b>."
        },
        "desc_tim": {
            "h1": "24WCOB320W5IP62 - taśma LED WCOB 24V 10W/m IP62 6000K do instalacji profesjonalnych",
            "p1": "Model <b>24WCOB320W5IP62</b> to przemysłowej jakości taśma LED <b>WCOB</b> o mocy <b>10W/m</b> i barwie zimnej <b>6000K</b>. Generuje <b>1350 lm/m</b> przy skuteczności <b>135 lm/W</b> i kącie emisji <b>180°</b>. Wyposażona w ochronną powłokę silikonową <b>IP62</b> bez żółtego paska luminoforu, zapewniającą wysoką estetykę i odporność środowiskową.",
            "h2": "Zastosowanie projektowe: ekspozycje, witryny, architektura nowoczesna i strefy IP62",
            "p2": "Barwa chłodna <b>6000K</b> o wysokim kontraście dedykowana jest do oświetlenia akcentującego elementy szklane, metalowe i ekspozycyjne oraz do stref o podwyższonej wilgotności wymagających ochrony <b>IP62</b>.",
            "h3": "Specyfikacja techniczna i montaż dla elektroinstalatorów",
            "p3": "Zasilanie: <b>24V DC</b> (0.41 A/m). Długość rolki: <b>5m</b>. Sekcja cięcia: <b>25 mm</b>. Szerokość podłoża: <b>8 mm</b>. Wymagany montaż w profilu aluminiowym LED. Zasilacz 24V DC o mocy min. 65W na 5m rolkę. Produkt objęty <b>5-letnią gwarancją</b>."
        },
        "desc_allegro": {
            "h1": "Taśma LED WCOB 24V 10W/m IP62 6000K Zimna 5m — Nowoczesna Linia Światła bez Żółtego Paska",
            "p1": "Odkryj nowość od <b>Prescot LED</b> — taśmę <b>WCOB (White COB)</b> o barwie zimnej <b>6000K</b>! W odróżnieniu od zwykłych taśm COB, taśma WCOB po wyłączeniu jest <b>elegancko biała</b> — nie ma brzydkiego żółtego paska. Po włączeniu świeci <b>perfekcyjnie gładką, krystalicznie białą linią światła</b> o mocy <b>1350 lm/m</b>.",
            "h2": "Krystaliczna barwa 6000K i odporność IP62 na wilgoć i parę",
            "p2": "Zimna biel <b>6000K</b> nadaje wnętrzom nowoczesny, ekskluzywny charakter. Idealnie eksponuje biżuterię, szkło, białe meble i industrialne dodatki. Klasa <b>IP62</b> chroni pasek przed zachlapaniem wodą i kurzem, co ułatwia utrzymanie go w czystości. Wysokie <b>CRI Ra &gt; 90</b> gwarantuje doskonałą przejrzystość kolorów.",
            "h3": "Łatwy montaż, bezpieczne zasilanie 24V i 5 lat gwarancji",
            "p3": "Pasek posiada mocną taśmę samoprzylepną i moduł cięcia co <b>2.5 cm</b>. Zasilanie <b>24V</b> zapewnia stabilność świecenia i brak przegrzewania. Produkt objęty jest pełną <b>5-letnią gwarancją producenta</b>."
        },
        "desc_shoper": {
            "h1": "24WCOB320W5IP62 - Taśma LED WCOB 24V 320LED 10W/m IP62 6000K Biała Zimna 5m",
            "p1": "<b>Prescot WCOB 24V IP62 6000K</b> to zaawansowana taśma LED nowej technologii WCOB bez żółtego paska. Zapewnia jednolitą linię światła o jasności <b>1350 lm/m (135 lm/W)</b> przy gęstości <b>320 diod/m</b> i kącie <b>180°</b>.",
            "h2": "Zastosowanie w nowoczesnych aranżacjach",
            "p2": "Zimna barwa <b>6000K</b> doskonale sprawdza się w aranżacjach minimalistycznych, gablotach, witrynach oraz pomieszczeniach o podwyższonej wilgotności (klasa <b>IP62</b>). Wskaźnik <b>Ra &gt; 90</b> zapewnia krystaliczną czystość bieli.",
            "h3": "Parametry i montaż",
            "p3": "Napięcie: <b>24V DC</b>, Moc: <b>10W/m</b>, Moduł cięcia: <b>25mm</b>, Szerokość: <b>8mm</b>. Montaż w profilu aluminiowym. <b>5 lat gwarancji</b> Prescot."
        }
    },
    {
        "id": "24WCOB280CCT5IP62",
        "ean": "5905475368370",
        "name_full": "Taśma LED WCOB CCT Tunable White 24V 280LED 17W/m IP62 2600-6000K 5m",
        "badge_label": "WCOB IP62 • CCT 2600-6000K • 17W/m • 1300lm/m • Ra>90 • 5m",
        "cct": "2600-6000K (CCT Tunable White)",
        "color_name": "CCT Tunable White (Regulowana)",
        "voltage": "24V",
        "power": "17W/m",
        "power_total": "85W / 5m",
        "current": "0.7 A/m",
        "diodes": "280/m",
        "diode_type": "WCOB CCT",
        "cri": "Ra > 90",
        "angle": "180°",
        "ip": "IP62",
        "cut_section": "25mm",
        "dimensions": "5000 x 8 mm",
        "lifespan": "50 000h",
        "temp_range": "-20°C ~ +40°C",
        "energy_class": "G",
        "lumen": "1300lm/m",
        "efficiency": "78lm/W",
        "warranty": "5 lat (60 miesięcy)",
        "dimmable": "TAK (ze sterownikiem CCT 24V)",
        "max_length_single": "5m",
        "desc_wapro": {
            "h1": "Płynna regulacja barwy 2600K-6000K i estetyka White COB — światło dopasowane do rytmu dnia",
            "p1": "Taśma LED <b>24WCOB280CCT5IP62</b> łączy technologię <b>Tunable White (CCT)</b> z estetyką <b>WCOB (White COB)</b>. Umożliwia płynną zmianę temperatury barwowej od ciepłej bieli <b>2600K</b>, przez neutralną <b>4000K</b>, aż po motywującą zimną <b>6000K</b> przy zachowaniu <b>100% jednolitej linii światła bez widocznych punktów</b>. W stanie wyłączonym taśma ma estetyczny biały kolor bez żółtego paska luminoforu.",
            "h2": "Zastosowanie w oświetleniu biodynamicznym (HCL) i strefach wilgotnych IP62",
            "p2": "Dzięki możliwości doboru barwy światła taśma wspiera koncepcję Human Centric Lighting (światło ciepłe wieczorem, neutralne i chłodne w ciągu dnia do pracy). Powłoka silikonowa <b>IP62</b> chroni taśmę przed wilgocią i kurzem, dzięki czemu doskonale sprawdza się w luksusowych salonach kąpielowych, kuchniach, sypialniach, strefach SPA oraz apartamentach premium.",
            "h3": "Sterowanie, parametry elektryczne i montaż w profilu aluminiowym",
            "p3": "Moc <b>17 W/m</b> (0.7 A/m przy 24V) zapewnia strumień <b>1300 lm/m</b> o wskaźniku <b>Ra &gt; 90</b>. Do sterowania wymagany jest dedykowany sterownik CCT (2-kanałowy WW/CW 24V DC). Zasilanie max 5m z jednej strony. Ze względu na moc 17W/m bezwzględnie wymagany jest montaż w profilu aluminiowym o odpowiedniej pojemności cieplnej. Gwarancja: <b>5 lat</b>."
        },
        "desc_tim": {
            "h1": "24WCOB280CCT5IP62 - profesjonalna taśma LED WCOB CCT 24V 17W/m IP62 2600-6000K",
            "p1": "Model <b>24WCOB280CCT5IP62</b> to zaawansowane źródło światła <b>WCOB CCT Tunable White</b> o gęstości <b>280 diod/m</b> i mocy <b>17W/m</b>. Zapewnia płynną regulację barwy w zakresie <b>2600K-6000K</b> przy strumieniu <b>1300 lm/m</b>, kącie <b>180°</b> i wskaźniku oddawania barw <b>Ra &gt; 90</b>. Klasa szczelności <b>IP62</b> chroni strukturę przed wilgocią i zanieczyszczeniami.",
            "h2": "Zastosowanie projektowe: oświetlenie dynamiczne CCT, rezydencje i hotele",
            "p2": "Dedykowana do inteligentnych systemów sterowania oświetleniem (DALI, ZigBee, Tuya, MiBoxer CCT). Pozwala na dynamiczne dopasowanie scen świetlnych w przestrzeniach mieszkalnych i komercyjnych z ochroną <b>IP62</b>.",
            "h3": "Wymagania instalacyjne: sterownik CCT, zasilacz 24V i radiator",
            "p3": "Napięcie: <b>24V DC</b> (0.7 A/m). Podłączenie: 3-przewodowe (V+, WW, CW). Moduł cięcia: <b>25 mm</b>. Wymagany zasilacz min. 100W 24V na rolkę 5m (zapas 25%) oraz sterownik CCT 24V PWM. Bezwzględny montaż w profilu aluminiowym. <b>5 lat gwarancji</b>."
        },
        "desc_allegro": {
            "h1": "Taśma LED WCOB CCT 24V 17W/m IP62 2600-6000K 5m — Zmienna Barwa Światła bez Żółtego Paska",
            "p1": "Nie wiesz, czy wybrać barwę ciepłą, neutralną czy zimną? Wybierz taśmę <b>WCOB CCT Tunable White</b> od <b>Prescot LED</b> i zmieniaj barwę pilotem lub aplikacją w zakresie od <b>2600K do 6000K</b>! Technologia <b>WCOB</b> oznacza brak żółtego paska po wyłączeniu oraz <b>idealnie gładką linię światła (280 LED/m)</b> po włączeniu.",
            "h2": "Światło dopasowane do Twojego nastroju i ochrona IP62",
            "p2": "Ciepłe 2600K do wieczornego relaksu, dzienne 4000K do gotowania i pracy, chłodne 6000K do precyzyjnych zadań — wszystko z jednej taśmy! Powłoka silikonowa <b>IP62</b> chroni taśmę przed kurzem, tłuszczem i parą wodną w kuchni i łazience. Wskaźnik <b>CRI Ra &gt; 90</b> gwarantuje naturalne i żywe kolory.",
            "h3": "Proste podłączenie ze sterownikiem CCT i 5 lat gwarancji",
            "p3": "Taśmę można ciąć co <b>25 mm</b>. Do działania taśmy wystarczy podłączyć zasilacz 24V oraz sterownik CCT. Bezpieczne napięcie <b>24V</b> i <b>5 lat pełnej gwarancji producenta</b> gwarantują bezawaryjność i spokój na lata."
        },
        "desc_shoper": {
            "h1": "24WCOB280CCT5IP62 - Taśma LED WCOB CCT 24V 280LED 17W/m IP62 2600-6000K 5m",
            "p1": "<b>Prescot WCOB CCT 24V IP62</b> to innowacyjna taśma LED z płynną regulacją temperatury barwowej (<b>2600K - 6000K</b>). Zastosowanie technologii WCOB eliminuje żółty pasek, oferując nienaganną biel podłoża oraz jednolitą linię światła o jasności <b>1300 lm/m</b>.",
            "h2": "Zastosowanie w inteligentnych domach i strefach wilgotnych",
            "p2": "Idealna do salonów, sypialni, kuchni i łazienek (klasa <b>IP62</b>). Pozwala na dostosowanie barwy światła do pory dnia. Wskaźnik <b>Ra &gt; 90</b> zapewnia najwyższą jakość odwzorowania barw.",
            "h3": "Specyfikacja techniczna i sterowanie",
            "p3": "Napięcie: <b>24V DC</b>, Moc: <b>17W/m</b>, Cięcie: <b>25mm</b>, Szerokość: <b>8mm</b>. Wymaga sterownika CCT 24V oraz montażu w profilu aluminiowym. <b>5 lat gwarancji</b> Prescot."
        }
    }
]

def build_blog_section(is_cct=False):
    guide_3_title = "Jak dobrać sterownik do taśmy CCT?" if is_cct else "Jak dobrać zasilacz do taśmy LED?"
    guide_3_sub = "zasilacz, sterownik i taśma w jednym układzie" if is_cct else "moc W/m, długość odcinka i zapas mocy"
    guide_3_url = "https://www.prescot.com.pl/pl/n/26" if is_cct else "https://www.prescot.com.pl/pl/n/24"

    return f"""<section style="font-family:inherit; margin:18px 0 28px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<div style="font-family:inherit; margin-bottom:18px; background:none !important; background-color:transparent !important; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">Praktyczne poradniki</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
        Dobierz taśmę LED bez zgadywania
      </h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.78; font-size:14px; line-height:1.6;">
        Stały zestaw poradników prowadzi przez barwę, jasność, profil, zasilanie i montaż, czyli decyzje potrzebne przed
        zakupem oraz cięciem taśmy.
      </p>
</div>
<div style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit; align-items:stretch;">
<div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak
          czytać parametry taśmy LED?</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">moc,
          lumeny, CRI, napięcie i IP</small>
<a href="https://www.prescot.com.pl/pl/n/23" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
<font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj
              poradnik</span></font>
</a>
</div>
<div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Klasy
          szczelności IP w praktyce</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">IP62,
          ochrona przed wilgocią w kuchni i łazience</small>
<a href="https://www.prescot.com.pl/pl/n/27" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
<font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj
              poradnik</span></font>
</a>
</div>
<div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">{guide_3_title}</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">{guide_3_sub}</small>
<a href="{guide_3_url}" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
<font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj
              poradnik</span></font>
</a>
</div>
<div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak
          dobrać profil aluminiowy do taśmy LED?</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">profil,
          klosz, chłodzenie i estetyka linii światła</small>
<a href="https://www.prescot.com.pl/pl/n/15" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
<font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj
              poradnik</span></font>
</a>
</div>
</div>
</section>"""

def build_spec_section(model_info):
    return f"""<section class="product-parameters-section" style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;"><span style="font-family:inherit; display:inline-block; margin-bottom:15px; padding:5px 12px; border-radius:999px; background:#475569 !important; background-color:#475569 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;"><font color="#ffffff">Specyfikacja</font></span><div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 5px;"><div style="display: flex; flex-direction: column; min-width: 0; word-break: break-word;"><span style="font-size: 12px; color: #64748b; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">Typ diody</span><span style="font-size: 15px; font-weight: 600; color: inherit;">{model_info['diode_type']}</span></div><div style="display: flex; flex-direction: column; min-width: 0; word-break: break-word;"><span style="font-size: 12px; color: #64748b; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">Napięcie</span><span style="font-size: 15px; font-weight: 600; color: inherit;">{model_info['voltage']}</span></div><div style="display: flex; flex-direction: column; min-width: 0; word-break: break-word;"><span style="font-size: 12px; color: #64748b; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">Barwa</span><span style="font-size: 15px; font-weight: 600; color: inherit;">{model_info['cct']}</span></div><div style="display: flex; flex-direction: column; min-width: 0; word-break: break-word;"><span style="font-size: 12px; color: #64748b; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">Jasność</span><span style="font-size: 15px; font-weight: 600; color: inherit;">{model_info['lumen']}</span></div><div style="display: flex; flex-direction: column; min-width: 0; word-break: break-word;"><span style="font-size: 12px; color: #64748b; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">Moc</span><span style="font-size: 15px; font-weight: 600; color: inherit;">{model_info['power']}</span></div><div style="display: flex; flex-direction: column; min-width: 0; word-break: break-word;"><span style="font-size: 12px; color: #64748b; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">Wydajność</span><span style="font-size: 15px; font-weight: 600; color: inherit;">{model_info['efficiency']}</span></div><div style="display: flex; flex-direction: column; min-width: 0; word-break: break-word;"><span style="font-size: 12px; color: #64748b; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">CRI</span><span style="font-size: 15px; font-weight: 600; color: inherit;">{model_info['cri']}</span></div><div style="display: flex; flex-direction: column; min-width: 0; word-break: break-word;"><span style="font-size: 12px; color: #64748b; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">Stopień ochrony</span><span style="font-size: 15px; font-weight: 600; color: inherit;">{model_info['ip']}</span></div><div style="display: flex; flex-direction: column; min-width: 0; word-break: break-word;"><span style="font-size: 12px; color: #64748b; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">Gwarancja</span><span style="font-size: 15px; font-weight: 600; color: inherit;">{model_info['warranty']}</span></div></div></section>"""

def build_accordion(model_info, platform, item_number):
    m_id = model_info["id"]
    ean = model_info["ean"]
    badge_label = model_info["badge_label"]
    desc_data = model_info[f"desc_{platform}"]
    is_cct = "CCT" in m_id

    badge_1_name = "Seria WCOB IP62" if platform == "wapro" else ("Opis techniczny" if platform == "tim" else ("Gotowy do montażu" if platform == "allegro" else "Taśma LED WCOB"))
    badge_2_name = "Gdzie sprawdzi się najlepiej" if platform == "wapro" else ("Zastosowanie instalacyjne" if platform == "tim" else ("Zalety technologii WCOB" if platform == "allegro" else "Zastosowanie"))
    badge_3_name = "Parametry i montaż" if platform == "wapro" else ("Wytyczne montażu i zasilania" if platform == "tim" else ("Montaż i bezpieczeństwo" if platform == "allegro" else "Wytyczne instalacji"))

    # Construct sections
    sec1 = f"""<section style="font-family:inherit; margin:28px 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">{badge_1_name}</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">{desc_data['h1']}</h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">{desc_data['p1']}</p>
</section>"""

    sec2 = f"""<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">{badge_2_name}</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">{desc_data['h2']}</h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">{desc_data['p2']}</p>
</section>"""

    sec3 = f"""<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">{badge_3_name}</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">{desc_data['h3']}</h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">{desc_data['p3']}</p>
</section>"""

    sec4 = build_blog_section(is_cct=is_cct)
    sec5 = build_spec_section(model_info)

    view_inner = f"{sec1}\n{sec2}\n{sec3}\n{sec4}\n{sec5}"
    textarea_inner = html.escape(f"{sec1}\n{sec2}\n{sec3}\n{sec4}\n{sec5}")

    accordion_html = f"""<div class="product-accordion" data-model="{m_id}">
<button class="product-trigger" onclick="toggleProduct(this)">
<div class="product-info">
<span class="product-model">{item_number}. {m_id}</span>
<span class="product-label-badge">{badge_label}</span>
</div>
<span class="product-arrow">▼</span>
</button>
<div class="product-body">
<div class="model-block" id="desc-view-{platform}-{m_id}">
{view_inner}
</div>
<div class="desc-edit" id="desc-edit-{platform}-{m_id}" style="display: none;">
<textarea class="edit-textarea" id="textarea-{platform}-{m_id}" oninput="onDescriptionInput('{platform}', 'tasmy', '{m_id}')">{textarea_inner}</textarea>
</div>
<div class="product-controls">
<button class="control-btn btn-edit" id="btn-edit-{platform}-{m_id}" onclick="toggleEdit('{platform}', 'tasmy', '{m_id}')">Edytuj opis</button>
<button class="control-btn btn-save" id="btn-save-{platform}-{m_id}" onclick="saveDescription('{platform}', 'tasmy', '{m_id}')" style="display: none;">Zapisz opis</button>
<button class="control-btn btn-copy" onclick="copyDescriptionHtml('{platform}', '{m_id}', this)" style="border-color: #f59e0b; color: #f59e0b;" title="Kopiuj opis HTML">Kopiuj opis HTML</button>
<button class="control-btn btn-ean" onclick="navigator.clipboard.writeText('{ean}'); this.innerText='Skopiowano!'; setTimeout(()=&gt;this.innerText='EAN: {ean}', 2000);" style="border-color: #0ea5e9; color: #0ea5e9;" title="Skopiuj EAN">EAN: {ean}</button>
<span class="control-status" id="status-{platform}-{m_id}"></span>
</div>
</div>
</div>"""
    return accordion_html

print("Generator functions ready.")
