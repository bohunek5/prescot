with open("scripts/seo_rules.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith("        for section in sections:"):
        new_lines.append("    for section in sections:\n")
    elif line.startswith("        h = normalize"):
        new_lines.append("        h = normalize(section['heading'])\n")
    elif line.startswith("        if len(h) < 12:"):
        new_lines.append("        if len(h) < 12:\n")
    elif line.startswith("            h = f\"{h} – {code}\""):
        new_lines.append("            h = f\"{h} – {code}\"\n")
    elif line.startswith("        if len(h) > 65:"):
        new_lines.append("        if len(h) > 65:\n")
    elif line.startswith("            h = h[:63].rsplit"):
        new_lines.append("            h = h[:63].rsplit(' ', 1)[0]\n")
    elif line.startswith("        section[\"heading\"] = h"):
        new_lines.append("        section['heading'] = h\n")
    elif line.startswith("        source_p = "):
        new_lines.append("        source_p = [normalize(p) for p in section['paragraphs'] if normalize(p)]\n")
    elif line.startswith("        section[\"paragraphs\"] = source_p"):
        new_lines.append("        section['paragraphs'] = source_p if source_p else [f\"{title}. Sprawdzony wariant z oferty Prescot.\"]\n")
    elif line.startswith("benefits = [x for x in"):
        new_lines.append("    benefits = [x for x in list(dict.fromkeys(normalize(x).removesuffix('.') for x in benefits if normalize(x))) if len(x) >= 5][:4]\n")
    else:
        new_lines.append(line)

with open("scripts/seo_rules.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Fixed indentation.")
