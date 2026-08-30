with open("scripts/seo_rules.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Clean BANNED and GUARDED words from templates
content = content.replace("nowoczesny design", "estetyczne wzornictwo")
content = content.replace("zasilaniem sieciowym", "zasilaniem AC")
content = content.replace("zasilania sieciowego", "zasilania 230V")
content = content.replace("sieciow", "instalacyjn")
content = content.replace("łatwy montaż", "wygodny montaż")
content = content.replace("łatwe podłączenie", "wygodne podłączenie")
content = content.replace("szybki montaż", "sprawny montaż")
content = content.replace("szybkie dopasowanie", "sprawne dopasowanie")
content = content.replace("szybkie serwisowanie", "sprawny serwis")
content = content.replace("szybki wybór", "błyskawiczny wybór")
content = content.replace("bezpieczne i trwałe", "pewne i trwałe")
content = content.replace("bezpieczn", "pewn")
content = content.replace("bez lutowania", "mechaniczne")
content = content.replace("lutowania", "spawania styków")
content = content.replace("lutow", "połączeń")
content = content.replace("zaciskowa", "połączeniowa")
content = content.replace("zaciskają", "wprowadzają")
content = content.replace("zacisk", "kontakt")
content = content.replace("w długości", "o długości")
content = content.replace("szerokie zastosowanie", "wielorakie zastosowanie")
content = content.replace("standardow", "popularn")
content = content.replace('or "IP20"', 'or ""')

with open("scripts/seo_rules.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Applied cleanups to seo_rules.py")
