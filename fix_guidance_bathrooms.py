import re

with open("scripts/seo_rules.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("łazienek, ", "").replace(", łazienki", "").replace("łazienki, ", "")

# Fix finish() heading lengths and similarity
finish_fix = '''    for section in sections:
        h = normalize(section["heading"])
        if len(h) < 12:
            h = f"{h} – {code}"
        if len(h) > 65:
            h = h[:63].rsplit(" ", 1)[0]
        section["heading"] = h
        source_p = [normalize(p) for p in section["paragraphs"] if normalize(p)]
        section["paragraphs"] = source_p if source_p else [f"{title}. Sprawdzony wariant z oferty Prescot."]\n'''

content = re.sub(r'for section in sections:\s+if len\(normalize\(section\["heading"\]\)\) < 10:.*?(?=benefits = )', finish_fix, content, flags=re.DOTALL)

with open("scripts/seo_rules.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed guidance bathrooms and finish headings.")
