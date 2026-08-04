import re
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Logo
logo_match = re.search(r'<img[^>]*src="[^"]*prescot[^"]*"[^>]*>', text, re.IGNORECASE)
if logo_match:
    print("LOGO:", logo_match.group(0))

# 2. Sub tabs
panel_start = text.find('id="panel-wapro"')
panel_end = text.find('id="wapro-tasmy"')
print("SUB-TABS:", text[panel_start:panel_end])

# 3. Zlaczki container
zlaczki_start = text.find('id="wapro-zlaczki"')
if zlaczki_start != -1:
    print("Found wapro-zlaczki")

