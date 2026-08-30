import re

with open("scripts/seo_rules.py", "r", encoding="utf-8") as f:
    code = f.read()

# Let's add full category generators for electrical osprzet and technical parts
new_generators = '''
def electrical_socket_editorial(product: dict[str, Any]) -> dict[str, Any]:
    name = product["name"]
    code = product["code"]
    specs = public_specs(product)[:8]
    is_hermetic = "ip44" in name.lower() or "hermet" in name.lower()
    is_double = "podwójn" in name.lower() or "2x" in name.lower()
    is_surface = "n/t" in name.lower() or "natynk" in name.lower()
    mount = "natynkowy (N/T)" if is_surface else "podtynkowy (P/T)"
    type_desc = "podwójne gniazdo wtyczkowe" if is_double else "pojedyncze gniazdo wtyczkowe"
    ip_desc = "o podwyższonej klasie szczelności IP44 z klapką ochronną" if is_hermetic else "do suchych pomieszczeń wewnętrznych"

    pill1 = "Osprzęt elektroinstalacyjny"
    h1 = f"{name} – pewne zasilanie w instalacji 230V"
    p1 = f"Solidne {type_desc} z uziemieniem przeznaczone do bezpiecznego i trwałego podłączania odbiorników elektrycznych 230V. Zapewnia stabilny styk mechaniczny, wytrzymałą konstrukcję zacisków oraz estetyczny wygląd w każdym pomieszczeniu."

    pill2 = "Przeznaczenie i montaż"
    h2 = f"Montaż {mount} {ip_desc}"
    p2 = f"Produkt przystosowany do montażu {mount}. Wytrzymała obudowa z tworzywa odpornego na zarysowania i promieniowanie UV gwarantuje wieloletnią, bezawaryjną eksploatację w domach, warsztatach, biurach oraz obiektach użyteczności publicznej."

    pill3 = "Bezpieczeństwo i standard"
    h3 = f"Wykonanie z uziemieniem i zgodność z normami"
    p3 = f"Konstrukcja spełnia rygorystyczne normy bezpieczeństwa instalacji elektrycznych. Zapewnia wygodne wprowadzanie przewodów i pewne trzymanie wtyczek."

    sections = [
        {"label": pill1, "heading": h1, "paragraphs": [p1]},
        {"label": pill2, "heading": h2, "paragraphs": [p2]},
        {"label": pill3, "heading": h3, "paragraphs": [p3]},
    ]
    benefits = ["Pewne uziemienie bolcowe", f"Montaż {mount}", "Trwałe tworzywo odporne na UV", "Zgodność z normami 230V"]
    applications = ["Instalacje domowe i biurowe", "Warsztaty, garaże i strefy techniczne", "Puszki i instalacje natynkowe"]
    checks = ["Napięcie znamionowe: 230V AC", "Maksymalne obciążenie prądowe: 16A", "Przekrój podłączanych przewodów instalacyjnych"]
    notes = ["Montaż i podłączenie wykonaj przy całkowicie wyłączonym napięciu zasilania", "Stosuj przewody o odpowiednim przekroju dostosowanym do obciążenia"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def electrical_switch_editorial(product: dict[str, Any]) -> dict[str, Any]:
    name = product["name"]
    code = product["code"]
    specs = public_specs(product)[:8]
    is_double = any(k in name.lower() for k in ("podwójn", "świecznik", "dwugrup", "2-klawisz"))
    is_stair = "schodow" in name.lower()
    is_cross = "krzyżow" in name.lower()
    is_surface = "n/t" in name.lower() or "natynk" in name.lower()
    mount = "natynkowy (N/T)" if is_surface else "podtynkowy (P/T)"
    kind = "schodowy" if is_stair else "krzyżowy" if is_cross else "świecznikowy (podwójny)" if is_double else "jednobiegunowy"

    pill1 = "Łączniki i wyłączniki"
    h1 = f"{name} – komfortowe sterowanie obwodem"
    p1 = f"Precyzyjny łącznik klawiszowy typu {kind} przeznaczony do komfortowego załączania obwodów oświetleniowych i odbiorników 230V. Mechanizm o wyczuwalnym, płynnym skoku gwarantuje niezawodną pracę przez tysiące cykli przełączeń."

    pill2 = "Zastosowanie w układzie"
    h2 = f"Dedykowany do montażu {mount}"
    p2 = f"Doskonale sprawdza się w sterowaniu oświetleniem w domach, korytarzach, klatkach schodowych i obiektach komercyjnych. Zapewnia estetyczne wykończenie ściany oraz ergonomiczne użytkowanie na co dzień."

    pill3 = "Instalacja i parametry"
    h3 = f"Wygodne podłączenie i trwałe zaciski"
    p3 = f"Konstrukcja umożliwia szybkie i pewne podłączenie żył instalacyjnych. Wysokiej jakości materiał nie żółknie pod wpływem światła słonecznego."

    sections = [
        {"label": pill1, "heading": h1, "paragraphs": [p1]},
        {"label": pill2, "heading": h2, "paragraphs": [p2]},
        {"label": pill3, "heading": h3, "paragraphs": [p3]},
    ]
    benefits = [f"Typ łącznika: {kind}", f"Montaż {mount}", "Niezawodny mechanizm przełączający", "Odporność na zarysowania"]
    applications = ["Sterowanie oświetleniem 230V", "Układy schodowe i korytarzowe", "Instalacje mieszkaniowe i komercyjne"]
    checks = ["Funkcja łącznika w schemacie instalacji", "Napięcie znamionowe: 230V", "Dopuszczalne obciążenie toru prądowego"]
    notes = ["Prace montażowe prowadź wyłącznie przy odłączonym napięciu w rozdzielnicy", "Sprawdź poprawność schematu połączeń przed załączeniem bezpiecznika"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def electrical_frame_editorial(product: dict[str, Any]) -> dict[str, Any]:
    name = product["name"]
    code = product["code"]
    specs = public_specs(product)[:8]
    m_holes = re.search(r"(\d+)[-\s]*krotn|(\d+)[-\s]*moduł", name.lower())
    holes = m_holes.group(1) or m_holes.group(2) if m_holes else "1"
    color = product_color(product) or "estetyczne wykończenie"

    pill1 = "Ramki instalacyjne"
    h1 = f"{name} – eleganckie wykończenie osprzętu"
    p1 = f"Dedykowana ramka instalacyjna ({holes}-krotna) w kolorze {color}, stworzona do estetycznego maskowania i montażu modułów gniazd oraz łączników. Zapewnia idealne przyleganie do płaszczyzny ściany i spójny design całego osprzętu."

    pill2 = "Kompatybilność i aranżacja"
    h2 = f"Perfekcyjne dopasowanie do serii modułowej"
    p2 = f"Wykonana z trwałego tworzywa o wysokiej odporności na zarysowania i zabrudzenia. Pozwala na montaż w układzie pionowym lub poziomym w zależności od projektu instalacji."

    pill3 = "Wskazówki montażowe"
    h3 = f"Prosty montaż zatrzaskowy na mechanizmach"
    p3 = f"Precyzyjne zaczepy gwarantują stabilne osadzenie ramki na mostkach mechanizmów bez powstawania nieestetycznych szczelin."

    sections = [
        {"label": pill1, "heading": h1, "paragraphs": [p1]},
        {"label": pill2, "heading": h2, "paragraphs": [p2]},
        {"label": pill3, "heading": h3, "paragraphs": [p3]},
    ]
    benefits = [f"Krotność: {holes}", f"Kolor: {color}", "Montaż pionowy lub poziomy", "Odporność na odbarwienia"]
    applications = ["Maskowanie gniazd i łączników", "Wielokrotne zestawy ścienne", "Aranżacja wnętrz mieszkalnych i biurowych"]
    checks = ["Krotność ramki zgodna z liczbą puszek", "Kompatybilność z serią osprzętu"]
    notes = ["Zatrzaskuj ramkę po ostatecznym dokręceniu mechanizmów do puszek instalacyjnych"]
    return finish(product, sections, benefits, applications, checks, notes, specs)
'''

# Update general_editorial dispatch
old_dispatch = """def general_editorial(product: dict[str, Any]) -> dict[str, Any]:
    rule = classify_editorial_rule(product)
    if rule == "tape":
        return tape_editorial(product)
    if rule == "power":
        return power_editorial(product)
    if rule == "controller":
        return controller_editorial(product)
    if rule == "control_input":
        return control_input_editorial(product)
    if rule == "profile":
        return profile_editorial(product)
    if rule == "profile_cover":
        return profile_cover_editorial(product)
    if rule == "accessory":
        return accessory_editorial(product)
    if rule == "light_source":
        return light_source_editorial(product)
    if rule == "luminaire":
        return luminaire_editorial(product)
    return manufacturer_source_editorial(product, product.get("producer") or "Prescot")"""

new_dispatch = """def general_editorial(product: dict[str, Any]) -> dict[str, Any]:
    rule = classify_editorial_rule(product)
    if rule == "tape":
        return tape_editorial(product)
    if rule == "power":
        return power_editorial(product)
    if rule == "controller":
        return controller_editorial(product)
    if rule == "control_input":
        return control_input_editorial(product)
    if rule == "profile":
        return profile_editorial(product)
    if rule == "profile_cover":
        return profile_cover_editorial(product)
    if rule == "accessory":
        return accessory_editorial(product)
    if rule == "light_source":
        return light_source_editorial(product)
    if rule == "luminaire":
        return luminaire_editorial(product)
    if rule == "electrical_socket":
        return electrical_socket_editorial(product)
    if rule == "electrical_switch":
        return electrical_switch_editorial(product)
    if rule == "electrical_frame":
        return electrical_frame_editorial(product)
    return manufacturer_source_editorial(product, product.get("producer") or "Prescot")"""

if old_dispatch in code:
    code = code.replace(old_dispatch, new_generators + "\n\n" + new_dispatch)
    with open("scripts/seo_rules.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Successfully added electrical osprzet rules and updated dispatch!")
else:
    print("Could not find exact old_dispatch, appending generators.")
    code = code + "\n\n" + new_generators + "\n\n" + new_dispatch
    with open("scripts/seo_rules.py", "w", encoding="utf-8") as f:
        f.write(code)
