import re

with open("scripts/seo_rules.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix lead lengths in finish()
content = re.sub(
    r'wapro_lead = normalize\(f"\{title\.rstrip\(\'\.\'\)\}\. \{benefits\[0\]\} oraz \{benefits\[1\]\}\."\)',
    'wapro_lead = normalize(f"{title.rstrip(\'.\')}. Zastosowanie: {applications[0].lower()}. Główne cechy: {benefits[0]} oraz {benefits[1]}.")',
    content
)
content = re.sub(
    r'allegro_lead = normalize\(f"\{applications\[0\]\}\. Przed zakupem sprawdź: \{first_check\.lower\(\)\}\."\)',
    'allegro_lead = normalize(f"{title.rstrip(\'.\')}. {applications[0]}. Przed zakupem sprawdź: {first_check.lower()}.")',
    content
)

# Remove "równomier", "stabiln", "idealn" from template sentences in seo_rules.py
content = content.replace("równomierną emisję światła", "ciągłą emisję światła")
content = content.replace("równomierny strumień", "ciągły strumień")
content = content.replace("równomierną linię", "ciągłą linię")
content = content.replace("idealnie równą", "ciągłą")
content = content.replace("idealnie", "estetycznie")
content = content.replace("idealn", "precyzyjn")
content = content.replace("stabilną pracę", "niezawodną pracę")
content = content.replace("stabilne zasilanie", "zasilanie DC")
content = content.replace("stabilny zapłon", "pewny zapłon")
content = content.replace("stabilne napięcie", "stałe napięcie")
content = content.replace("stabilne światło", "pewne światło")
content = content.replace("stabilne i efektywne", "efektywne")
content = content.replace("stabilne", "pewne")
content = content.replace("stabiln", "pewn")

with open("scripts/seo_rules.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patched seo_rules.py successfully.")
