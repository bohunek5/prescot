with open("scripts/seo_rules.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace finish function with completely clean, no-internal-code logic
start_fin = content.find("def finish(")
end_fin = content.find("def classify_editorial_rule(")

clean_finish = '''def finish(
    product: dict[str, Any],
    sections: list[dict[str, Any]],
    benefits: list[str],
    applications: list[str],
    checks: list[str],
    notes: list[str],
    specs: list[tuple[str, str]],
) -> dict[str, Any]:
    title = title_for(product)
    meta = meta_for(product, specs)
    cat_root = product.get("categoryRoot", "Prescot")

    def sanitize_field(val: str) -> str:
        if not val:
            return val
        s = str(val)
        s = re.sub(r"(?i)\bidealn\w*(?:\s+(?:do|dla|rozwiązanie|wybór))?\b", "odpowiednie rozwiązanie", s)
        s = re.sub(r"(?i)\bidealn\w*\b", "odpowiedni", s)
        s = re.sub(r"(?i)\brównomiern\w*\b", "ciągłą", s)
        s = re.sub(r"(?i)\bstabiln\w*\b", "pewną", s)
        s = re.sub(r"(?i)\bnajwyższ\w*\s+jakoś\w*\b", "wysoka precyzja", s)
        s = re.sub(r"(?i)\bnp\.\b", "na przykład", s)
        s = re.sub(r"(?i)\bean\s*:\s*\S+", "", s)
        s = re.sub(r"(?i)\bproducent\s*:\s*\S+", "", s)
        s = re.sub(r"(?i)\bdane techniczne\b", "parametry", s)
        s = re.sub(r"(?i)\b(?:pre[-_]\S+|taś\d{5,}|pro\d{5,}|kat\d{5,}|wyp[-_]\S+)\b", "", s)
        return normalize(s)

    for section in sections:
        h = sanitize_field(section['heading'])
        if len(h) < 12:
            h = f"{h} – {cat_root}"
        if len(h) > 65:
            h = h[:63].rsplit(' ', 1)[0]
        section['heading'] = h
        source_p = [sanitize_field(p) for p in section['paragraphs'] if normalize(p)]
        if not source_p:
            source_p = [f"{title}. Sprawdzony wariant z oferty Prescot."]
        section['paragraphs'] = source_p

    def clean_points(items: list[str], max_len: int = 125) -> list[str]:
        res = []
        for x in items:
            s = sanitize_field(x).removesuffix(".")
            if len(s) > max_len:
                s = s[:max_len - 2].rsplit(" ", 1)[0]
            if len(s) >= 5 and s not in res:
                res.append(s)
        return res

    benefits = clean_points(benefits, 120)[:4]
    applications = clean_points(applications, 120)[:4]
    checks = clean_points(checks, 120)[:4]
    notes = clean_points(notes, 120)[:3]

    if len(benefits) < 2:
        benefits.extend(f"{k}: {v}" for k, v in specs[:3] if f"{k}: {v}" not in benefits)
    if len(benefits) < 2:
        benefits.extend(["Wysoka jakość wykonania", "Kompatybilność z systemem"])
    if len(applications) < 2:
        applications.extend(["Oświetlenie domowe, biurowe i komercyjne", "Montaż w dedykowanych profilach i oprawach"])
    if len(checks) < 2:
        checks.extend(["Sprawdź napięcie i moc przed montażem", "Dobierz kompatybilne akcesoria montażowe"])
    if not notes:
        notes.append("Montaż wykonuj przy odłączonym zasilaniu zgodnie ze sztuką instalacyjną")

    wapro_lead = sanitize_field(normalize(f"{title.rstrip('.')}. Dedykowane zastosowanie: {applications[0].lower()}. Główne atuty: {benefits[0]} oraz {benefits[1]}."))
    if len(wapro_lead) > 340:
        wapro_lead = wapro_lead[:338].rsplit(" ", 1)[0] + "."
    if len(wapro_lead) < 90:
        wapro_lead = f"{wapro_lead} Profesjonalny produkt z oferty Prescot do trwałych instalacji."

    tim_lead = sanitize_field(normalize(f"{title}. Profesjonalny produkt z oficjalnej oferty Prescot. Zobacz parametry, zastosowanie i wskazówki montażowe."))
    if len(tim_lead) > 340:
        tim_lead = tim_lead[:338].rsplit(" ", 1)[0] + "."
    if len(tim_lead) < 90:
        tim_lead = f"{tim_lead} Sprawdzony w profesjonalnych instalacjach."

    first_check = re.sub(r"(?i)^(?:przed zakupem )?sprawdź(?: przed zakupem)?:\s*", "", checks[0])
    allegro_lead = sanitize_field(normalize(f"{title.rstrip('.')}. {applications[0]}. Przed zakupem sprawdź: {first_check.lower()}."))
    if len(allegro_lead) > 340:
        allegro_lead = allegro_lead[:338].rsplit(" ", 1)[0] + "."
    if len(allegro_lead) < 90:
        allegro_lead = f"{allegro_lead} Sprawdź wymiary oraz specyfikację."

    return {
        "seo_title": title,
        "meta_description": meta,
        "sections": sections,
        "benefits": benefits[:4],
        "applications": applications[:4],
        "selection_checks": checks[:4],
        "installation_notes": notes[:3],
        "channel_leads": {
            "wapro": wapro_lead,
            "tim": tim_lead,
            "allegro": allegro_lead,
        },
    }
'''

if start_fin != -1 and end_fin != -1:
    content = content[:start_fin] + clean_finish + "\n\n" + content[end_fin:]

with open("scripts/seo_rules.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Applied clean finish without catalog codes.")
