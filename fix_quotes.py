with open("scripts/seo_rules.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(r"\'", "'")

with open("scripts/seo_rules.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed quotes in seo_rules.py")
