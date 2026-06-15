import random

file_paths = [
    '/Users/karolbohdanowicz/my-ai-agents/prescot/old_index.html'
]

warm_original = "Ciepła biel 3000K dobrze działa w kuchniach, salonach, sypialniach, restauracjach i zabudowach meblowych. Daje efekt przytulny, ale nadal czytelny, dlatego pasuje zarówno do dekoracji, jak i do spokojnego światła użytkowego."
warm_variations = [
    "Barwa 3000K to klasyczne ciepłe światło. Sprawdza się w strefach wypoczynkowych, sypialniach, salonach oraz przy drewnianych wykończeniach wnętrz. Idealna do budowania relaksującej atmosfery bez utraty funkcjonalności.",
    "Światło o temperaturze 3000K daje przytulny, ciepły efekt. Rekomendowane do oświetlania wnętrz mieszkalnych, restauracji, kawiarni oraz wszędzie tam, gdzie zależy nam na miękkim, nastrojowym świetle.",
    "Ciepła biel (3000K) świetnie komponuje się z klasycznymi wnętrzami i materiałami takimi jak drewno czy cegła. Najczęściej wybierana do salonów, sypialni i stref relaksu jako główne lub dekoracyjne źródło światła.",
    "Barwa ciepła 3000K ociepla wnętrze i sprzyja wyciszeniu. Idealnie nadaje się do hoteli, stref wypoczynkowych w domu oraz jako podświetlenie wnęk i półek w sypialniach czy pokojach dziennych.",
    "Temperatura 3000K to sprawdzone rozwiązanie do przestrzeni, w których dominuje funkcja relaksacyjna. Dobry wybór do oświetlenia wieczornego w salonach, nad stołem jadalnianym oraz w pokojach hotelowych."
]

neutral_original = "Neutralna biel 4000K nie idzie ani w żółty, ani w zimny odcień. Dobrze sprawdza się przy blacie kuchennym, lustrze, biurku, garderobie, regale i ekspozycji, bo pomaga zachować naturalny odbiór kolorów."
neutral_variations = [
    "Neutralna biel (4000K) to uniwersalne światło zbliżone do dziennego. Niezbędna do pracy przy blacie roboczym w kuchni, a także w biurach czy łazienkach, gdzie kluczowe jest wierne oddawanie barw bez przekłamań.",
    "Barwa 4000K gwarantuje czysty, neutralny odcień – bez żółtych ani niebieskich domieszek. Idealna do stref roboczych, gabinetów, przestrzeni komercyjnych oraz nad lustrem do precyzyjnego makijażu.",
    "Światło o temperaturze 4000K wspiera skupienie i zachowuje naturalne kolory oświetlanych przedmiotów. To najczęstszy wybór do nowoczesnych kuchni, przedpokojów, biur oraz sklepów i witryn wystawowych.",
    "Temperatura 4000K to optymalny środek między ciepłym a zimnym oświetleniem. Znajduje zastosowanie w nowoczesnych wnętrzach mieszkalnych, minimalistycznych aranżacjach i pomieszczeniach wymagających bardzo dobrej widoczności.",
    "Neutralne światło 4000K nie męczy wzroku i poprawia koncentrację. Stanowi niezawodny wybór do oświetlenia zadaniowego: w gabinetach, nad kuchennymi wyspami roboczymi, w łazienkach czy garderobach."
]

cold_original = "Zimna biel 6500K podbija wrażenie czystości i kontrastu. Sprawdzi się w pomieszczeniach technicznych, garażach, zapleczach, chłodniejszych aranżacjach, ekspozycjach oraz tam, gdzie zależy Ci na mocnym, jasnym odbiorze powierzchni."
cold_variations = [
    "Zimna biel (6500K) to wyraziste, stymulujące światło o wysokim kontraście. Sprawdza się w garażach, warsztatach, halach produkcyjnych oraz w nowoczesnych przestrzeniach komercyjnych wymagających maksymalnego doświetlenia.",
    "Barwa zimna 6500K zapewnia doskonałą widoczność detali i podbija wrażenie sterylności. Najlepszy wybór do laboratoriów, pomieszczeń technicznych, magazynów oraz stanowisk wymagających precyzyjnej pracy manualnej.",
    "Światło o temperaturze 6500K wyraźnie wyostrza kontury i pobudza do działania. Stosowane najczęściej w oświetleniu technicznym, przemysłowym, witrynach oraz nowoczesnych biurach, magazynach i strefach roboczych.",
    "Temperatura 6500K to chłodny, bardzo jasny odcień światła, przypominający światło dzienne. Niezbędna w warsztatach precyzyjnych i wszędzie tam, gdzie najważniejsza jest absolutna ostrość widzenia.",
    "Zimne oświetlenie 6500K daje poczucie czystości i powiększa optycznie przestrzeń. Idealne do podświetlania banerów, nowoczesnych surowych wnętrz i ekspozycji, gdzie zależy nam na bezkompromisowej wyrazistości."
]

# Randomly replace occurrences
def replace_with_random(text, original, variations):
    parts = text.split(original)
    result = parts[0]
    for part in parts[1:]:
        result += random.choice(variations) + part
    return result

for file_path in file_paths:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = replace_with_random(content, warm_original, warm_variations)
    new_content = replace_with_random(new_content, neutral_original, neutral_variations)
    new_content = replace_with_random(new_content, cold_original, cold_variations)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Replaced text in {file_path}")
