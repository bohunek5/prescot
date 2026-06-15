import re

def vary_text(html, platform):
    res = html
    
    # We maintain the WAPRO style (no BS, technical but accessible)
    # but use synonyms or slight rephrasings for SEO uniqueness.
    
    if platform == 'tim':
        replacements = [
            # Low Brightness (460lm, etc)
            ("Low brightness wybierasz tam, gdzie światło ma być obecne, ale nie agresywne:", "Wariant Low brightness sprawdzi się tam, gdzie światło powinno być widoczne, ale subtelne:"),
            ("w cokołach, półkach, witrynach, wnękach, sypialni, za lustrem albo w nocnej linii komunikacyjnej.", "w podświetleniach cokołów, półkach, witrynach, wnękach, za lustrem czy jako oświetlenie nocne w korytarzach."),
            ("To taśma do efektu i komfortu, nie do prześwietlania całej zabudowy.", "Jest to taśma nastawiona na komfort wizualny, a nie na intensywne rozświetlanie całego pomieszczenia."),
            ("To jasność do dekoracji z realnym efektem:", "Jest to jasność dekoracyjna z wyraźnym efektem:"),
            ("pod półkę, do regału, cokołu, gabloty, wnęki sufitowej albo tła za lustrem.", "do montażu pod półkami, w regałach, cokołach, we wnękach sufitowych czy jako poświata za lustrem."),
            ("Daje widoczne światło, ale nadal pozostaje miękka i nie dominuje wnętrza.", "Zapewnia dostrzegalne światło, jednak pozostaje miękka w odbiorze i nie przytłacza reszty wystroju."),
            ("Format rolka 5m sprawdza się przy pojedynczej linii światła albo kilku krótszych odcinkach w jednej zabudowie.", "Pięciometrowa rolka to dobry wybór dla pojedynczych linii świetlnych lub kilku krótszych odcinków w jednej strefie."),
            ("Cięcie wykonuj w oznaczonych polach co 50mm,", "Cięcie należy wykonywać w wyznaczonych punktach co 50mm,"),
            ("żeby zachować poprawne styki i nie uszkodzić odcinka.", "aby zapewnić stabilne styki i uniknąć uszkodzenia modułu."),
            ("Zasilacz dobierz pod 24V i łączną długość wszystkich odcinków.", "Zasilacz powinien pracować na 24V i być dobrany do sumarycznej długości instalacji."),
            ("Zasilacz dobierz pod 12V i łączną długość wszystkich odcinków.", "Zasilacz powinien pracować na 12V i być dobrany do sumarycznej długości instalacji."),
            ("Format rolka 50m jest wygodny przy dłuższych, powtarzalnych realizacjach:", "Rolka o długości 50m to optymalne rozwiązanie przy większych i powtarzalnych realizacjach:"),
            ("regałach, zabudowach, kilku pomieszczeniach albo pracy instalacyjnej, gdzie odcinki docinasz dopiero na miejscu.", "w rozbudowanych regałach, sufitach podwieszanych i pracach instalatorskich, gdzie wymiar dopasowywany jest bezpośrednio na budowie."),
            
            # Medium/High Brightness
            ("Ten poziom jasności wybierasz do cokołów, półek, witryn, wnęk, linii nocnych i miękkiego podświetlenia mebli.", "Ten stopień jasności dobieraj do podświetlania cokołów, wnęk, półek i tworzenia miękkiego oświetlenia meblowego."),
            ("Światło ma prowadzić wzrok i podkreślić kształt, a nie razić ani zastępować lampę roboczą.", "Światło ma za zadanie akcentować formę, bez oślepiania i zastępowania głównego źródła światła."),
            ("Tu taśma pracuje już jak wyraźne oświetlenie użytkowe.", "W tym przypadku taśma pełni rolę solidnego oświetlenia użytkowego."),
            ("Wybierz ją nad blatem, w profilu podszafkowym, nad ladą, w witrynie, przy ekspozycji produktu albo w dłuższej linii meblowej, gdzie światło ma być widoczne nawet przy oświetleniu ogólnym.", "Zastosuj ją pod szafkami kuchennymi, nad blatem, w witrynach czy przy ekspozycjach, gdzie światło musi być wyraźne nawet w dzień."),
            ("Taki poziom jasności ma sens w miejscach, gdzie taśma naprawdę ma świecić:", "Tak wysoki poziom jasności jest uzasadniony w miejscach, które wymagają realnego oświetlenia:"),
            ("długi blat, mocna ekspozycja, wysoka witryna, zabudowa sufitowa, lada sprzedażowa albo przestrzeń robocza.", "na długich blatach roboczych, w wysokich witrynach, sufitach podwieszanych, ladach sklepowych i przestrzeniach do pracy."),
            ("Przy tej jasności szczególnie ważny jest profil aluminiowy i dobrze policzone zasilanie.", "Przy tak dużej wydajności świetlnej absolutnie konieczny jest profil aluminiowy do chłodzenia oraz odpowiednio dobrany zasilacz."),
            
            # Zasilacze
            ("Hermetyczny zasilacz Scharfer pracuje na stałym napięciu", "Zasilacz hermetyczny marki Scharfer dostarcza stabilne napięcie"),
            ("i zasila taśmy LED, moduły oraz podświetlenia w profilu aluminiowym.", "do poprawnej pracy taśm LED, modułów reklamowych i podświetleń w profilach."),
            ("Obudowa IP67 pomaga chronić elektronikę przed wilgocią i kurzem", "Szczelność na poziomie IP67 zabezpiecza elektronikę przed wodą i zapyleniem"),
            ("dlatego sprawdzi się w meblach, zabudowach, ekspozycjach oraz miejscach bardziej wymagających niż sucha szafka techniczna.", "co pozwala na montaż w łazienkach, ekspozycjach, meblach i na zewnątrz budynków."),
            ("Ten wariant dobierz do małych odcinków taśmy, krótkich półek, liter reklamowych, lustra, próbnej linii LED albo niewielkiej witryny.", "Jest to wariant optymalny dla krótkich odcinków LED, mniejszych podświetleń luster, półek czy liter przestrzennych."),
            ("Ten wariant dobierz do rozbudowanych instalacji, długich odcinków taśm, większych ekspozycji, kilku stref LED i projektów wymagających mocnego zasilania.", "Ten model zalecamy do obszernych instalacji świetlnych, wielostrefowych projektów i długich linii taśmowych."),
            ("Najpierw policz sumę mocy wszystkich odcinków taśmy, a dopiero potem wybierz zasilacz.", "Przed doborem zasilacza zawsze wykonaj bilans mocy wszystkich podłączanych odcinków."),
            ("Przy pracy ciągłej zostaw zapas, bo zasilacz nie powinien pracować stale na granicy projektu.", "Pamiętaj o zachowaniu bezpiecznego zapasu mocy, by unikać pracy ciągłej na maksymalnym obciążeniu."),
            
            ("Produkt objęty jest 7-letnią gwarancją producenta.", "Urządzenie zabezpieczone jest 7-letnią gwarancją producenta."),
            ("Profil aluminiowy stabilizuje montaż, poprawia chłodzenie i pomaga uzyskać czystą linię światła.", "Wykorzystanie profilu aluminiowego ułatwia montaż, chłodzi diody i sprzyja uzyskaniu estetycznej linii świetlnej.")
        ]
        
    elif platform == 'wapro':
        replacements = [
            # Low Brightness
            ("Low brightness wybierasz tam, gdzie światło ma być obecne, ale nie agresywne:", "Wybierz linię Low brightness tam, gdzie zależy Ci na dyskretnym i miękkim efekcie:"),
            ("w cokołach, półkach, witrynach, wnękach, sypialni, za lustrem albo w nocnej linii komunikacyjnej.", "podświetlenie cokołów, otwarte półki, witryny, światło nocne na schodach czy tło za lustrem."),
            ("To taśma do efektu i komfortu, nie do prześwietlania całej zabudowy.", "Zadaniem tej taśmy jest budowanie klimatu i komfortu wizualnego, a nie oświetlanie całego pomieszczenia."),
            ("To jasność do dekoracji z realnym efektem:", "Jest to idealny poziom jasności do tworzenia akcentów świetlnych:"),
            ("pod półkę, do regału, cokołu, gabloty, wnęki sufitowej albo tła za lustrem.", "do wnęk, gablot, półek i regałów, gdzie światło nie może oślepiać."),
            ("Daje widoczne światło, ale nadal pozostaje miękka i nie dominuje wnętrza.", "Zapewnia wyraźny, ale bardzo miękki i relaksujący blask."),
            ("<font color=\"#ffffff\">Low brightness</font>\n  </span>\n\n    Wybierz", "<font color=\"#ffffff\">Low brightness</font>\n  </span>\n\n  <h3 style=\"font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;\">\n    Miękkie światło do tła, detalu i nastroju\n  </h3>\n\n  <p style=\"font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;\">\n    Wybierz"),
            
            # Medium/High Brightness
            ("Ten poziom jasności wybierasz do cokołów, półek, witryn, wnęk, linii nocnych i miękkiego podświetlenia mebli.", "Ten poziom mocy świetlnej jest uniwersalny i sprawdzi się do oświetlania mebli, głębokich witryn i podwieszanych sufitów."),
            ("Światło ma prowadzić wzrok i podkreślić kształt, a nie razić ani zastępować lampę roboczą.", "Jej zadaniem jest wyraźnie doświetlić detale, bez jednoczesnego rażenia w oczy."),
            ("Tu taśma pracuje już jak wyraźne oświetlenie użytkowe.", "Na tym poziomie jasności taśma staje się pełnoprawnym źródłem światła roboczego."),
            ("Wybierz ją nad blatem, w profilu podszafkowym, nad ladą, w witrynie, przy ekspozycji produktu albo w dłuższej linii meblowej, gdzie światło ma być widoczne nawet przy oświetleniu ogólnym.", "Zastosuj ją pod szafkami w kuchni, nad blatem warsztatowym, przy ladach recepcyjnych i wszędzie tam, gdzie potrzebujesz mocnego światła użytkowego."),
            ("Taki poziom jasności ma sens w miejscach, gdzie taśma naprawdę ma świecić:", "Tak duża moc jest dedykowana do miejsc wymagających bardzo mocnego naświetlenia:"),
            ("długi blat, mocna ekspozycja, wysoka witryna, zabudowa sufitowa, lada sprzedażowa albo przestrzeń robocza.", "blaty robocze, główne światło z sufitu podwieszanego czy mocne doświetlenie towaru w sklepie."),
            ("Przy tej jasności szczególnie ważny jest profil aluminiowy i dobrze policzone zasilanie.", "Przy tak wysokich parametrach świetlnych obowiązkowo stosuj profil aluminiowy (do chłodzenia) oraz mocny zasilacz z zapasem."),
            ("<font color=\"#ffffff\">High brightness</font>\n  </span>\n\n    Tak duża", "<font color=\"#ffffff\">High brightness</font>\n  </span>\n\n  <h3 style=\"font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;\">\n    Bardzo mocne światło do zadań specjalnych\n  </h3>\n\n  <p style=\"font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;\">\n    Tak duża"),
            ("<font color=\"#ffffff\">Medium brightness</font>\n  </span>\n\n    Ten poziom", "<font color=\"#ffffff\">Medium brightness</font>\n  </span>\n\n  <h3 style=\"font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;\">\n    Subtelne oświetlenie funkcyjne\n  </h3>\n\n  <p style=\"font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;\">\n    Ten poziom")
        ]
        
    elif platform == 'allegro':
        replacements = [
            # Low Brightness (460lm, etc)
            ("Low brightness wybierasz tam, gdzie światło ma być obecne, ale nie agresywne:", "Model z serii Low brightness polecamy do miejsc, gdzie światło ma tworzyć nastrój, a nie razić w oczy:"),
            ("w cokołach, półkach, witrynach, wnękach, sypialni, za lustrem albo w nocnej linii komunikacyjnej.", "w podświetleniu półek, we wnękach, za lustrem łazienkowym, w cokołach meblowych lub jako nocne światło orientacyjne."),
            ("To taśma do efektu i komfortu, nie do prześwietlania całej zabudowy.", "Taśma ta służy do uzyskania efektu wizualnego i komfortu, bez nadmiernego rozświetlania przestrzeni."),
            ("To jasność do dekoracji z realnym efektem:", "Jest to optymalna jasność do oświetlenia dekoracyjnego z zauważalnym efektem:"),
            ("pod półkę, do regału, cokołu, gabloty, wnęki sufitowej albo tła za lustrem.", "do wklejenia pod półkę, w regałach, we wnękach na suficie, gablotach czy na obrysie lustra."),
            ("Daje widoczne światło, ale nadal pozostaje miękka i nie dominuje wnętrza.", "Emituje zauważalny strumień światła, jednak pozostaje przyjazna dla oka i nie dominuje nad wystrojem."),
            ("Format rolka 5m sprawdza się przy pojedynczej linii światła albo kilku krótszych odcinkach w jednej zabudowie.", "Zwijka o długości 5m to popularny format do wykonywania pojedynczych linii lub do podziału na kilka krótszych fragmentów."),
            ("Cięcie wykonuj w oznaczonych polach co 50mm,", "Moduły należy przecinać w specjalnie oznakowanych miejscach co 50mm,"),
            ("żeby zachować poprawne styki i nie uszkodzić odcinka.", "aby nie doprowadzić do uszkodzenia ścieżek i zachować sprawność taśmy."),
            ("Zasilacz dobierz pod 24V i łączną długość wszystkich odcinków.", "Konieczne jest zastosowanie zasilacza 24V dobranego do całkowitego obciążenia układu."),
            ("Zasilacz dobierz pod 12V i łączną długość wszystkich odcinków.", "Konieczne jest zastosowanie zasilacza 12V dobranego do całkowitego obciążenia układu."),
            ("Format rolka 50m jest wygodny przy dłuższych, powtarzalnych realizacjach:", "Rolka 50-metrowa to format idealny do zastosowań profesjonalnych i długich linii:"),
            ("regałach, zabudowach, kilku pomieszczeniach albo pracy instalacyjnej, gdzie odcinki docinasz dopiero na miejscu.", "przy produkcji oświetlenia do regałów, w ciągach sufitowych i pracach instalacyjnych wymagających elastyczności na miejscu."),
            
            # Medium/High Brightness
            ("Ten poziom jasności wybierasz do cokołów, półek, witryn, wnęk, linii nocnych i miękkiego podświetlenia mebli.", "Taką jasność najlepiej zastosować do dyskretnego podświetlania mebli, półek, witryn, cokołów oraz wnęk."),
            ("Światło ma prowadzić wzrok i podkreślić kształt, a nie razić ani zastępować lampę roboczą.", "Jej celem jest zaakcentowanie konturów i kształtów, bez efektu oślepiania."),
            ("Tu taśma pracuje już jak wyraźne oświetlenie użytkowe.", "W tym wydaniu taśma staje się pełnoprawnym oświetleniem roboczym."),
            ("Wybierz ją nad blatem, w profilu podszafkowym, nad ladą, w witrynie, przy ekspozycji produktu albo w dłuższej linii meblowej, gdzie światło ma być widoczne nawet przy oświetleniu ogólnym.", "Idealnie sprawdza się w profilach pod szafkami kuchennymi, nad blatami, ladami i w mocno doświetlonych witrynach sklepowych."),
            ("Taki poziom jasności ma sens w miejscach, gdzie taśma naprawdę ma świecić:", "Tak mocny strumień świetlny jest wskazany tam, gdzie wymagane jest oświetlenie najwyższej próby:"),
            ("długi blat, mocna ekspozycja, wysoka witryna, zabudowa sufitowa, lada sprzedażowa albo przestrzeń robocza.", "blaty kuchenne, sufity, lady, stanowiska pracy oraz wymagające ekspozycje produktów."),
            ("Przy tej jasności szczególnie ważny jest profil aluminiowy i dobrze policzone zasilanie.", "Przy tych parametrach świetlnych wymagany jest montaż w aluminiowym profilu (odprowadzanie ciepła) i niezawodny zasilacz."),
            
            # Zasilacze
            ("Hermetyczny zasilacz Scharfer pracuje na stałym napięciu", "Model zasilacza hermetycznego Scharfer gwarantuje stałe napięcie"),
            ("i zasila taśmy LED, moduły oraz podświetlenia w profilu aluminiowym.", "niezbędne do prawidłowego funkcjonowania pasków LED i różnego typu podświetleń."),
            ("Obudowa IP67 pomaga chronić elektronikę przed wilgocią i kurzem", "Konstrukcja w klasie IP67 chroni komponenty wewnętrzne przed kurzem oraz wodą"),
            ("dlatego sprawdzi się w meblach, zabudowach, ekspozycjach oraz miejscach bardziej wymagających niż sucha szafka techniczna.", "przez co idealnie nadaje się do łazienek, wymagających zabudów meblowych oraz zastosowań zewnętrznych."),
            ("Ten wariant dobierz do małych odcinków taśmy, krótkich półek, liter reklamowych, lustra, próbnej linii LED albo niewielkiej witryny.", "Zasilacz dedykowany do niewielkich obciążeń, np. zasilania krótkich pasków, pojedynczego lustra, czy małej witrynki."),
            ("Ten wariant dobierz do rozbudowanych instalacji, długich odcinków taśm, większych ekspozycji, kilku stref LED i projektów wymagających mocnego zasilania.", "Wariant zaprojektowany do zasilania rozbudowanych instalacji świetlnych, wymagających projektów sufitowych i długich ciągów LED."),
            ("Najpierw policz sumę mocy wszystkich odcinków taśmy, a dopiero potem wybierz zasilacz.", "Dobór mocy zasilacza zawsze poprzedzaj kalkulacją całkowitego obciążenia podłączanych taśm."),
            ("Przy pracy ciągłej zostaw zapas, bo zasilacz nie powinien pracować stale na granicy projektu.", "Rekomendujemy uwzględnienie przynajmniej 10-15% zapasu mocy, aby sprzęt nie był przeciążany przy długotrwałej pracy."),
            
            ("Produkt objęty jest 7-letnią gwarancją producenta.", "Na ten produkt przysługuje aż 7 lat gwarancji producenta."),
            ("Profil aluminiowy stabilizuje montaż, poprawia chłodzenie i pomaga uzyskać czystą linię światła.", "Montaż w aluminiowym profilu stabilizuje taśmę, obniża jej temperaturę i pomaga w uzyskaniu idealnej linii światła.")
        ]
    
    for old, new in replacements:
        res = res.replace(old, new)
        
    return res
