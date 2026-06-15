import re

with open("/Users/karolbohdanowicz/Downloads/TASMY.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. We replace the "Strumień ..." paragraph globally with new narratives.
def narrative_replacer(match):
    lm_str = match.group(2)
    lm = int(lm_str)
    
    if lm <= 330:
        desc = "Delikatne, nastrojowe światło. Użyj tej taśmy tam, gdzie chcesz stworzyć klimat – do podświetlenia cokołów, tyłu telewizora, dekoracyjnych wnęk czy krawędzi łóżka. Daje miękki, nienachalny blask, który relaksuje po zmroku."
    elif lm <= 400:
        desc = "Subtelne oświetlenie funkcyjne. Świetnie sprawdzi się jako podświetlenie półek w garderobie, regale, czy jako łagodne światło orientacyjne na schodach i w korytarzach."
    elif lm <= 460:
        desc = "Złoty środek w oświetleniu meblowym. Wybierz ten wariant, gdy potrzebujesz wyraźnie i wygodnie doświetlić blat roboczy w kuchni, biurko do pracy lub wyeksponować towar w witrynie."
    elif lm >= 1400:
        desc = "Bardzo mocne światło do zadań specjalnych. Stosuj ten wariant jako główne oświetlenie wpuszczane w sufit, nad blatem warsztatowym czy w biurze. Tam, gdzie potrzebujesz maksymalnej widoczności."
    else:
        desc = "Uniwersalne światło do wnętrz mieszkalnych i biurowych. Praktyczny wybór do codziennych zastosowań."
        
    return desc

p_pattern = r'(<p[^>]*>)\s*Strumień (\d+)lm/m.*?(?=</p>)'
html = re.sub(p_pattern, lambda m: m.group(1) + "\n    " + narrative_replacer(m) + "\n  ", html, flags=re.DOTALL)

# Remove any residual " (3m)" text, just in case
html = re.sub(r',\s*wariant cięty z metra \(3m\)', '', html)
html = re.sub(r'wariant cięty z metra \(3m\)', '', html)
html = re.sub(r'Ten wariant cięty z metra.*?podwieszanych\.\s*', '', html, flags=re.DOTALL)

# 2. Sync TIM to WAPRO
tim_pattern = r'(<textarea[^>]*id="textarea-tim-([^"]+)"[^>]*>)(.*?)(</textarea>)'
tim_matches = re.findall(tim_pattern, html, flags=re.DOTALL)

for full_open, sku, inner_html, close_tag in tim_matches:
    wapro_pattern = rf'(<textarea[^>]*id="textarea-wapro-{re.escape(sku)}"[^>]*>)(.*?)(</textarea>)'
    html = re.sub(wapro_pattern, lambda m: m.group(1) + inner_html + m.group(3), html, flags=re.DOTALL)
    
    wapro_div_pattern = rf'(<div class="model-block" id="desc-view-wapro-{re.escape(sku)}">)(.*?)(</div>\s*<div class="edit-block" id="desc-edit-wapro-{re.escape(sku)}")'
    html = re.sub(wapro_div_pattern, lambda m: m.group(1) + "\n" + inner_html + "\n" + m.group(3), html, flags=re.DOTALL)

with open("/Users/karolbohdanowicz/my-ai-agents/prescot/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Processed", len(tim_matches), "products.")
