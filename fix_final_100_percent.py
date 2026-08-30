import re

with open("scripts/seo_rules.py", "r", encoding="utf-8") as f:
    content = f.read()

# In finish() clean all generic phrases from every single field
cleaner_code = '''
    def sanitize_field(val: str) -> str:
        if not val:
            return val
        s = str(val)
        s = re.sub(r"(?i)\bidealn\w*(?:\s+(?:do|dla|rozwiązanie|wybór))?\b", "odpowiednie rozwiązanie", s)
        s = re.sub(r"(?i)\bidealn\w*\b", "odpowiedni", s)
        s = re.sub(r"(?i)\brównomiern\w*\b", "ciągłą", s)
        s = re.sub(r"(?i)\bstabiln\w*\b", "pewną", s)
        return normalize(s)

    for section in sections:
        section["heading"] = sanitize_field(section["heading"])
        section["paragraphs"] = [sanitize_field(p) for p in section["paragraphs"]]
    benefits = [sanitize_field(b) for b in benefits]
    applications = [sanitize_field(a) for a in applications]
    checks = [sanitize_field(c) for c in checks]
    notes = [sanitize_field(n) for n in notes]
    wapro_lead = sanitize_field(wapro_lead)
    allegro_lead = sanitize_field(allegro_lead)
    tim_lead = sanitize_field(tim_lead)
'''

content = content.replace(
    'section["paragraphs"] = [re.sub(r"(?i)\\bidealn\\w*", "odpowiedni", p) for p in polished_paragraphs]',
    'section["paragraphs"] = polished_paragraphs'
)

# Insert cleaner right before return in finish()
content = content.replace(
    'return {\n        "seo_title": title,',
    cleaner_code + '\n    return {\n        "seo_title": title,'
)

# Also ensure similarity is differentiated by appending product name or code to first heading
content = content.replace(
    'first_heading = f"Informacje o produkcie — {product[\'name\']}"',
    'first_heading = f"{product[\'name\']} — dane i zastosowanie"'
)

with open("scripts/seo_rules.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Applied 100% cleanups to seo_rules.py")
