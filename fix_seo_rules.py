import re

with open("scripts/seo_rules.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Clean finish() fallbacks
content = content.replace(
    'applications.extend([f"Dobór według kategorii: {product[\'category\'].split(\'/\')[-1]}", f"Identyfikacja wariantu po kodzie {code}"])',
    'applications.extend(["Montaż w profilu aluminiowym lub na przygotowanym podłożu", "Oświetlenie główne, zadaniowe lub dekoracyjne"])'
)
content = content.replace(
    'checks.extend([f"Porównaj pełny indeks handlowy {code}", f"Zweryfikuj EAN {product[\'ean\']} przed zamówieniem"])',
    'checks.extend(["Sprawdź wymiary oraz warunki montażu", "Przed podłączeniem potwierdź zgodność elementów instalacji"])'
)
content = content.replace(
    'wapro_lead = normalize(f"{title.rstrip(\'.\')}. Najważniejsze dane: {benefits[0].lower()} oraz {benefits[1].lower()}. Indeks handlowy: {code}.")',
    'wapro_lead = normalize(f"{title.rstrip(\'.\')}. {benefits[0]} oraz {benefits[1]}.")'
)
content = content.replace(
    'allegro_lead = normalize(f"{applications[0]}. Przed zakupem sprawdź: {first_check.lower()}. Indeks handlowy: {code}.")',
    'allegro_lead = normalize(f"{applications[0]}. Przed zakupem sprawdź: {first_check.lower()}.")'
)

# 2. Clean tape_editorial
content = re.sub(
    r'first_text = f"Model \{code\} ma elastyczny laminat S-Shape przeznaczony do łuków, liter, zaokrągleń i dekoracyjnych linii światła\. Format produktu to \{format_label\}\."',
    r'first_text = f"Taśma LED S-Shape ma elastyczny laminat przeznaczony do łuków, liter, zaokrągleń, nieregularnych kształtów i dekoracyjnych linii światła. {sentence_case(format_label)} pozwala dopasować materiał do założeń projektu."',
    content
)
content = re.sub(
    r'first_text = f"Model \{code\} wykorzystuje technologię White COB: po wyłączeniu widoczna jest biała powierzchnia zamiast intensywnie żółtego paska luminoforu\.\s*\{f\'Układ \{leds\} tworzy równą linię światła\. \' if leds else \'\'\}Format handlowy: \{format_label\}\."',
    r'first_text = f"Taśma LED z serii White COB po wyłączeniu prezentuje estetyczną białą powierzchnię zamiast żółtego paska luminoforu. {f\'Układ {leds} tworzy idealnie równą linię światła. \' if leds else \'\'}{sentence_case(format_label)} ułatwia montaż w nowoczesnych instalacjach."',
    content
)
content = re.sub(
    r'first_text = f"Taśma COB \{code\} tworzy jednolitą linię bez wyraźnych punktów świetlnych\.\s*\{f\'Zasilanie \{voltage\} ułatwia planowanie odcinków\. \' if voltage else \'\'\}Format produktu: \{format_label\}\."',
    r'first_text = f"Taśma LED COB tworzy jednolitą linię światła bez widocznych pojedynczych punktów świetlnych. {f\'Zasilanie {voltage} ułatwia stabilną pracę na dłuższych odcinkach. \' if voltage else \'\'}{sentence_case(format_label)} określa długość przygotowaną do montażu."',
    content
)
content = re.sub(
    r'first_text = f"Model \{code\} jest taśmą \{color_name or cct or \'wielokanałową\'\} i wymaga sterownika zgodnego z układem kanałów\. Napięcie zasilania to \{voltage or \'wartość wskazana dla modelu\'\}, a format produktu to \{format_label\}\."',
    r'first_text = f"Taśma LED {color_name or cct or \'wielokanałowa\'} umożliwia dynamiczną zmianę barwy lub koloru światła przy użyciu kompatybilnego sterownika. {f\'Napięcie {voltage} zapewnia optymalne zasilanie. \' if voltage else \'\'}{sentence_case(format_label)} określa ilość taśmy w zestawie."',
    content
)
content = re.sub(
    r'first_text = f"Model \{code\} to taśma \{diode or \'LED\'\} o zasilaniu \{voltage or \'określonym dla wariantu\'\}\.\s*\{f\'Gęstość \{leds\} wpływa na rozstaw punktów światła\. \' if leds else \'\'\}Format produktu: \{format_label\}\."',
    r'first_text = f"Taśma LED {series} {diode or \'\'} to sprawdzone źródło światła do oświetlenia liniowego, sufitowego i meblowego. {f\'Zasilanie {voltage} oraz gęstość {leds} zapewniają równomierną emisję światła. \' if voltage and leds else \'\'}{sentence_case(format_label)} ułatwia dopasowanie długości."',
    content
)

# Clean headings in tape_editorial
content = content.replace('first_heading = f"Ciągła linia światła w modelu {code}"', 'first_heading = "Ciągła linia światła bez widocznych punktów LED"')
content = content.replace('first_heading = f"Sterowana barwa światła w wariancie {code}"', 'first_heading = "Sterowana barwa światła dopasowana do nastroju"')
content = content.replace('first_heading = f"Taśma {series} w wariancie {code}"', 'first_heading = f"Wysokiej jakości linia światła z serii {series}"')
content = content.replace('brightness_heading = f"Moc {power} i przeznaczenie wariantu {code}" if power else f"Przeznaczenie modelu {code}"', 'brightness_heading = f"Moc {power} i wysoka wydajność świetlna" if power else "Optymalna jasność do pracy i dekoracji"')
content = content.replace('color_heading = f"Miejsce użycia i format {format_label}"', 'color_heading = "Gdzie najlepiej sprawdzi się ten wariant"')
content = content.replace('f"Dobierając model {code}, porównaj moc na metr, gęstość diod oraz rolę planowanego oświetlenia. Parametry tego wariantu identyfikuje pełna nazwa produktu."', '"Dobierając taśmę LED, porównaj moc na metr, gęstość diod oraz przeznaczenie oświetlenia — użytkowe lub dekoracyjne."')
content = content.replace('f"Model {code} stosuj w oświetleniu liniowym po dobraniu zasilacza, profilu i warunków pracy do danych tego wariantu."', '"Taśmę stosuj w oświetleniu liniowym po dobraniu zgodnego zasilacza, profilu aluminiowego i odpowiedniego odprowadzania ciepła."')

with open("scripts/seo_rules.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated seo_rules.py successfully.")
