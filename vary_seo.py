import re

def vary_text(html, platform):
    res = html
    
    if platform == 'tim':
        replacements = [
            ("Tu taśma pracuje już jak wyraźne oświetlenie użytkowe.", "W tym wariancie taśma stanowi w pełni funkcjonalne oświetlenie użytkowe."),
            ("Wybierz ją nad blatem, w profilu podszafkowym, nad ladą, w witrynie, przy ekspozycji produktu albo w dłuższej linii meblowej, gdzie światło ma być widoczne nawet przy oświetleniu ogólnym.", "Zalecana do montażu nad blatami roboczymi, w profilach meblowych, witrynach sklepowych oraz jako wyraziste podświetlenie ekspozycji."),
            ("Profil aluminiowy stabilizuje montaż, poprawia chłodzenie i pomaga uzyskać czystą linię światła.", "Zastosowanie profilu aluminiowego gwarantuje optymalne odprowadzanie ciepła i estetyczne wykończenie instalacji."),
            ("Format rolka 5m sprawdza się przy pojedynczej linii światła albo kilku krótszych odcinkach w jednej zabudowie.", "Pięciometrowa rolka to standardowe rozwiązanie do ciągłych linii świetlnych oraz dzielenia na krótsze segmenty."),
            ("Format rolka 50m jest wygodny przy dłuższych, powtarzalnych realizacjach: regałach, zabudowach, kilku pomieszczeniach albo pracy instalacyjnej, gdzie odcinki docinasz dopiero na miejscu.", "Rolka 50-metrowa to optymalny wybór dla instalatorów i większych projektów komercyjnych, minimalizujący ilość odpadów."),
            ("Cięcie wykonuj w oznaczonych polach", "Skracanie taśmy jest możliwe wyłącznie w fabrycznie wyznaczonych miejscach"),
            ("żeby zachować poprawne styki i nie uszkodzić odcinka.", "co zapobiega uszkodzeniu obwodu i gwarantuje prawidłowe zasilanie."),
            ("Zasilacz dobierz pod 24V i łączną długość wszystkich odcinków.", "Wymagane zastosowanie zasilacza 24V o mocy dostosowanej do sumarycznej długości instalacji."),
            ("Zasilacz dobierz pod 12V i łączną długość wszystkich odcinków.", "Wymagane zastosowanie zasilacza 12V o mocy dostosowanej do sumarycznej długości instalacji."),
            ("Ten poziom jasności wybierasz do cokołów, półek, witryn, wnęk, linii nocnych i miękkiego podświetlenia mebli.", "Subtelny poziom jasności dedykowany do oświetlenia akcentującego: wnęk, cokołów, witryn oraz podświetleń nocnych."),
            ("Światło ma prowadzić wzrok i podkreślić kształt, a nie razić ani zastępować lampę roboczą.", "Głównym zadaniem jest tu akcentowanie detali i formy, bez ryzyka olśnienia użytkownika."),
            ("To jasność do dekoracji z realnym efektem: pod półkę, do regału, cokołu, gabloty, wnęki sufitowej albo tła za lustrem.", "Sprawdzona moc do oświetlenia dekoracyjnego w zabudowach meblowych, gablotach, wnękach architektonicznych i przy lustrach."),
            ("Daje widoczne światło, ale nadal pozostaje miękka i nie dominuje wnętrza.", "Zapewnia wyraźny efekt świetlny zachowując przy tym subtelny i nieinwazyjny charakter."),
            ("Taki poziom jasności ma sens w miejscach, gdzie taśma naprawdę ma świecić:", "Wysoka wydajność świetlna predysponuje ten model do wymagających zastosowań:"),
            ("długi blat, mocna ekspozycja, wysoka witryna, zabudowa sufitowa, lada sprzedażowa albo przestrzeń robocza.", "blaty robocze, przestrzenie komercyjne, oświetlenie główne sufitów oraz intensywne podświetlenie ekspozycji."),
            ("Przy tej jasności szczególnie ważny jest profil aluminiowy i dobrze policzone zasilanie.", "Kluczowe dla bezawaryjnej pracy jest zastosowanie profilu odprowadzającego ciepło oraz odpowiedniego doboru zasilacza."),
            ("Ten wariant dobierz do rozbudowanych instalacji, długich odcinków taśm, większych ekspozycji, kilku stref LED i projektów wymagających mocnego zasilania.", "Zasilacz dedykowany do zaawansowanych systemów LED, wielostrefowych układów oraz instalacji o dużym sumarycznym zapotrzebowaniu na moc."),
            ("Najpierw policz sumę mocy wszystkich odcinków taśmy, a dopiero potem wybierz zasilacz.", "Dobór urządzenia powinien opierać się na dokładnym wyliczeniu obciążenia wszystkich podłączonych obwodów."),
            ("Przy pracy ciągłej zostaw zapas, bo zasilacz nie powinien pracować stale na granicy projektu.", "Zaleca się uwzględnienie minimum 15-20% rezerwy mocy dla zachowania optymalnych parametrów pracy ciągłej."),
            ("Hermetyczny zasilacz Scharfer pracuje na stałym napięciu", "Niezawodny zasilacz hermetyczny Scharfer dostarcza stabilne napięcie"),
            ("i zasila taśmy LED, moduły oraz podświetlenia w profilu aluminiowym.", "do zasilania systemów taśmowych LED oraz specjalistycznych modułów oświetleniowych."),
            ("Obudowa IP67 pomaga chronić elektronikę przed wilgocią i kurzem", "Wysoka klasa szczelności IP67 gwarantuje ochronę układów przed wnikaniem pyłu i wody"),
            ("dlatego sprawdzi się w meblach, zabudowach, ekspozycjach oraz miejscach bardziej wymagających niż sucha szafka techniczna.", "co pozwala na instalację w wymagającym środowisku: na zewnątrz, w łazienkach czy wilgotnych piwnicach."),
            ("Ten wariant dobierz do małych odcinków taśmy, krótkich półek, liter reklamowych, lustra, próbnej linii LED albo niewielkiej witryny.", "Kompaktowy model przeznaczony do zasilania krótkich odcinków LED, pojedynczych modułów oraz niewielkich systemów ekspozycyjnych."),
            ("Produkt objęty jest 7-letnią gwarancją producenta.", "Urządzenie posiada 7 lat pełnej gwarancji producenta.")
        ]
        
    elif platform == 'allegro':
        replacements = [
            ("Tu taśma pracuje już jak wyraźne oświetlenie użytkowe.", "Prezentowana taśma doskonale sprawdza się jako mocne oświetlenie użytkowe."),
            ("Wybierz ją nad blatem, w profilu podszafkowym, nad ladą, w witrynie, przy ekspozycji produktu albo w dłuższej linii meblowej, gdzie światło ma być widoczne nawet przy oświetleniu ogólnym.", "Idealny wybór nad blat w kuchni, do podświetlenia witryn, lad sklepowych oraz każdej strefy, która wymaga wyraźnego akcentu świetlnego."),
            ("Profil aluminiowy stabilizuje montaż, poprawia chłodzenie i pomaga uzyskać czystą linię światła.", "Dla najlepszego efektu i długiej żywotności zalecamy montaż w profilu aluminiowym, który dodatkowo chłodzi diody."),
            ("Format rolka 5m sprawdza się przy pojedynczej linii światła albo kilku krótszych odcinkach w jednej zabudowie.", "Taśma sprzedawana w rolce 5-metrowej to uniwersalny format do większości zastosowań domowych i komercyjnych."),
            ("Format rolka 50m jest wygodny przy dłuższych, powtarzalnych realizacjach: regałach, zabudowach, kilku pomieszczeniach albo pracy instalacyjnej, gdzie odcinki docinasz dopiero na miejscu.", "Duża rolka 50-metrowa to oszczędność i wygoda przy większych montażach – tniesz na bieżąco, ile potrzebujesz."),
            ("Cięcie wykonuj w oznaczonych polach", "Pasek można docinać nożyczkami w specjalnie oznaczonych punktach"),
            ("żeby zachować poprawne styki i nie uszkodzić odcinka.", "aby nie uszkodzić diod i zachować gwarancję poprawnego działania."),
            ("Zasilacz dobierz pod 24V i łączną długość wszystkich odcinków.", "Pamiętaj o dobraniu zasilacza na 24V z odpowiednim zapasem mocy dla całego obwodu."),
            ("Zasilacz dobierz pod 12V i łączną długość wszystkich odcinków.", "Pamiętaj o dobraniu zasilacza na 12V z odpowiednim zapasem mocy dla całego obwodu."),
            ("Ten poziom jasności wybierasz do cokołów, półek, witryn, wnęk, linii nocnych i miękkiego podświetlenia mebli.", "Delikatne światło idealne do podświetlania szafek, półek, cokołów w kuchni oraz tworzenia nastroju w sypialni."),
            ("Światło ma prowadzić wzrok i podkreślić kształt, a nie razić ani zastępować lampę roboczą.", "Zapewnia miękki efekt dekoracyjny, który nie męczy oczu i pięknie podkreśla architekturę wnętrza."),
            ("To jasność do dekoracji z realnym efektem: pod półkę, do regału, cokołu, gabloty, wnęki sufitowej albo tła za lustrem.", "Pasek o tej mocy to pewny wybór na oświetlenie dekoracyjne: za lustro, pod szafkę, do regału czy sufitu podwieszanego."),
            ("Daje widoczne światło, ale nadal pozostaje miękka i nie dominuje wnętrza.", "Świeci wyraźnie, tworząc przytulny klimat, który nie przytłacza pozostałych elementów wystroju."),
            ("Taki poziom jasności ma sens w miejscach, gdzie taśma naprawdę ma świecić:", "Pasek o tak dużej mocy wybieraj tam, gdzie potrzebujesz naprawdę jasnego oświetlenia:"),
            ("długi blat, mocna ekspozycja, wysoka witryna, zabudowa sufitowa, lada sprzedażowa albo przestrzeń robocza.", "nad blat kuchenny, do głównego oświetlenia sufitu, nad ladę w sklepie czy do mocnego doświetlenia biura."),
            ("Przy tej jasności szczególnie ważny jest profil aluminiowy i dobrze policzone zasilanie.", "Przy tak mocnej taśmie profil aluminiowy (dla chłodzenia) i mocny zasilacz to absolutna konieczność."),
            ("Ten wariant dobierz do rozbudowanych instalacji, długich odcinków taśm, większych ekspozycji, kilku stref LED i projektów wymagających mocnego zasilania.", "Idealny zasilacz do dużych projektów, oświetlenia całego sufitu lub wielu metrów mocnej taśmy LED w jednym obwodzie."),
            ("Najpierw policz sumę mocy wszystkich odcinków taśmy, a dopiero potem wybierz zasilacz.", "Zawsze przelicz łączny pobór prądu przez wszystkie taśmy, zanim zdecydujesz się na ten model."),
            ("Przy pracy ciągłej zostaw zapas, bo zasilacz nie powinien pracować stale na granicy projektu.", "Zostaw margines bezpieczeństwa – zasilacz będzie służył dłużej, jeśli nie obciążysz go w 100%."),
            ("Hermetyczny zasilacz Scharfer pracuje na stałym napięciu", "Wodoodporny zasilacz marki Scharfer zapewnia stałe napięcie"),
            ("i zasila taśmy LED, moduły oraz podświetlenia w profilu aluminiowym.", "idealnie sprawdzając się do zasilania pasków LED i innych punktów świetlnych."),
            ("Obudowa IP67 pomaga chronić elektronikę przed wilgocią i kurzem", "Szczelna obudowa IP67 chroni urządzenie przed wodą, kurzem i parą"),
            ("dlatego sprawdzi się w meblach, zabudowach, ekspozycjach oraz miejscach bardziej wymagających niż sucha szafka techniczna.", "dzięki czemu możesz go zamontować w łazience, podbitce dachowej czy na zewnątrz budynku."),
            ("Ten wariant dobierz do małych odcinków taśmy, krótkich półek, liter reklamowych, lustra, próbnej linii LED albo niewielkiej witryny.", "Wybierz ten zasilacz do krótkiego kawałka taśmy, podświetlenia jednego lustra czy małej półeczki w salonie."),
            ("Produkt objęty jest 7-letnią gwarancją producenta.", "Kupujesz pewny sprzęt z aż 7-letnią gwarancją.")
        ]
    
    for old, new in replacements:
        res = res.replace(old, new)
        
    return res
