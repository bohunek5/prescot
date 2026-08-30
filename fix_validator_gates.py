import re

with open("scripts/seo_rules.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Fix title_for to always be 42-70 chars
title_code = '''def title_for(product: dict[str, Any]) -> str:
    name = normalize(product["name"])
    brand = product.get("producer") or "Prescot"
    if len(name) < 40:
        cat = leaf_category(product) if "leaf_category" in globals() else product.get("categoryRoot", "Oświetlenie LED")
        name = f"{name} – {cat}"
    if len(name) < 40:
        name = f"{name} {brand}"
    return name[:72]
'''

# 2. Fix light_guidance without foreign hardcoded numbers
light_guidance_code = '''def light_guidance(color: str, brightness: str = "") -> str:
    lower = normalize(color).casefold()
    level = first_number(brightness)
    if "ciep" in lower or ("k" in lower and (first_number(lower) or 9999) < 3300):
        color_use = "Ciepła barwa światła tworzy przytulny, relaksujący nastrój. Doskonale sprawdza się w salonach, sypialniach, hotelach i restauracjach, świetnie współgrając z drewnem, beżami i naturalnymi materiałami"
    elif "neutral" in lower or ("k" in lower and 3300 <= (first_number(lower) or 0) <= 5000):
        color_use = "Neutralna biel to najbardziej uniwersalne światło dzienne. Nie przekłamuje barw otoczenia i sprzyja koncentracji, dzięki czemu znakomicie pasuje do kuchni, łazienek, biur, korytarzy i blatów roboczych"
    elif "zim" in lower or ("k" in lower and (first_number(lower) or 0) > 5000):
        color_use = "Chłodna biel zapewnia rześkie, nowoczesne światło o wysokim kontraście. Znakomicie sprawdza się w nowoczesnych wnętrzach, strefach technicznych, gabinetach oraz do podświetlania gablot i witryn"
    elif "cct" in lower or "dual white" in lower:
        color_use = "Technologia CCT umożliwia płynną regulację temperatury barwowej od ciepłej bieli po chłodny odcień, pozwalając dopasować nastrój oświetlenia do pory dnia"
    elif "rgb" in lower:
        color_use = "Wielobarwny system RGB pozwala na kreowanie unikalnego nastroju, dynamicznych scen świetlnych oraz akcentowanie architektury nasyconymi kolorami"
    elif lower:
        color_use = f"Wyrazista barwa {color} pozwala na efektowne akcentowanie detali architektonicznych, tworzenie linii dekoracyjnych i nastrojowych podświetleń"
    else:
        color_use = "Odpowiednio dobrana barwa światła podkreśla walory wnętrza i zapewnia wysoki komfort domownikom"

    if level is None:
        return color_use + "."
    if level < 600:
        level_use = "Ten poziom strumienia tworzy subtelną poświatę akcentową do podświetlenia mebli i detali"
    elif level < 1100:
        level_use = "Wydajność ta zapewnia zbalansowane światło łączące efekt dekoracyjny z praktycznym doświetleniem blatów i zabudów"
    elif level < 1600:
        level_use = "Taki strumień dostarcza mocnego, wyraźnego światła do zadań głównych, roboczych i oświetlenia podszafkowego"
    else:
        level_use = "Wysoka jasność gwarantuje intensywne oświetlenie użytkowe do wymagających stref roboczych i komercyjnych"
    return f"{color_use}. {level_use}."
'''

# 3. Replace in content
content = re.sub(r'def title_for\(product: dict\[str, Any\]\) -> str:.*?(?=def meta_for)', title_code + '\n\n', content, flags=re.DOTALL)
content = re.sub(r'def light_guidance\(color: str, brightness: str = ""\) -> str:.*?(?=def light_application)', light_guidance_code + '\n\n', content, flags=re.DOTALL)

# 4. Remove all occurrences of "elimin", "wnęk"
content = content.replace("eliminując", "redukując").replace("eliminuje", "redukuje").replace("eliminacja", "brak konieczności")
content = content.replace("we wnękach", "w zabudowach").replace("wnękach", "zabudowach").replace("we wnęce", "w zabudowie").replace("wnęk", "zabudów")

# 5. In finish() ensure benefits length >= 5
content = content.replace(
    'benefits = list(dict.fromkeys(normalize(x).removesuffix(".") for x in benefits if normalize(x)))[:4]',
    'benefits = [x for x in list(dict.fromkeys(normalize(x).removesuffix(".") for x in benefits if normalize(x))) if len(x) >= 5][:4]'
)
content = content.replace(
    'checks = list(dict.fromkeys(normalize(x).removesuffix(".") for x in checks if normalize(x)))[:4]',
    'checks = [x for x in list(dict.fromkeys(normalize(x).removesuffix(".") for x in checks if normalize(x))) if len(x) >= 5][:4]'
)
content = content.replace(
    'applications = list(dict.fromkeys(normalize(x).removesuffix(".") for x in applications if normalize(x)))[:4]',
    'applications = [x for x in list(dict.fromkeys(normalize(x).removesuffix(".") for x in applications if normalize(x))) if len(x) >= 5][:4]'
)

with open("scripts/seo_rules.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated seo_rules.py with validator gate fixes.")
