import re
import random
import html

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

def get_rgb_info(sku):
    sku_upper = sku.upper()
    if 'RGBWW' in sku_upper:
        return "RGBWW", "ciepłej bieli (3000K)"
    elif 'RGBNW' in sku_upper:
        return "RGBNW", "neutralnej bieli (4000K)"
    elif 'RGBCCT' in sku_upper:
        return "RGBCCT", "zmiennej bieli (CCT - od ciepłej po zimną)"
    elif 'RGBW' in sku_upper:
        return "RGBW", "czystej bieli"
    elif 'RGB' in sku_upper:
        return "RGB", None
    return None, None

def generate_rgb_sections(sku):
    tape_type, white_type = get_rgb_info(sku)
    
    if not tape_type:
        return None, None

    if white_type:
        # RGBW / RGBCCT models
        sec2_title = "Dwa światła w jednym: Pełna paleta RGB + mocna biel"
        sec2_desc = f"Taśma łączy w sobie diody RGB z dedykowanymi diodami barwy {white_type}. Dzięki temu możesz korzystać z mocnego, użytkowego światła na co dzień, a wieczorem przełączyć na dowolny kolor z palety RGB. To idealny wybór do salonu, sypialni i stref relaksu, gdzie potrzebujesz zmiennego klimatu z jednej linii światła."
        
        sec3_title = "Uniwersalne zastosowanie w nowoczesnych wnętrzach"
        sec3_desc = "Taśmy wielokolorowe z dodatkową barwą białą to optymalne rozwiązanie do budowy nastroju. Zamiast skupiać się na lumenach, zyskujesz możliwość całkowitej zmiany charakteru pomieszczenia. Sprawdzą się rewelacyjnie w podwieszanych sufitach, zabudowach TV, oświetleniu gamingowym i przytulnym podświetleniu mebli."
    else:
        # Pure RGB models
        sec2_title = "Pełna paleta kolorów RGB do budowy klimatu"
        sec2_desc = "Taśma RGB została zaprojektowana wyłącznie z myślą o dekoracji i tworzeniu nastroju. Dzięki trzem podstawowym kanałom koloru (Czerwony, Zielony, Niebieski) możesz wygenerować tysiące barw. Służy nie do oświetlania roboczego, lecz do efektownego podświetlania i dynamicznej zmiany charakteru wnętrza."
        
        sec3_title = "Idealna do dekoracji i zabudów"
        sec3_desc = "Zapomnij o klasycznym przeliczaniu lumenów – skuteczność taśmy RGB mierzy się efektem wizualnym. Sprawdzi się perfekcyjnie w podwieszanych sufitach, za telewizorem, w strefach rozrywki, barach czy klubach. Świetnie podkreśla krawędzie i detale architektoniczne mocnym, nasyconym kolorem."

    sec2 = f"""<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">Przeznaczenie</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">{sec2_title}</h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">{sec2_desc}</p>
</section>"""

    sec3 = f"""<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">Gdzie sprawdzi się najlepiej</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">{sec3_title}</h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">{sec3_desc}</p>
</section>"""

    return sec2, sec3

# Find all RGB tape SKUs (containing E033 and RGB)
skus = set(re.findall(r'data-model="([^"]*E033[^"]*RGB[^"]*)"', content, re.IGNORECASE))

for sku in skus:
    for platform in ['wapro', 'tim', 'allegro']:
        div_id = f'desc-view-{platform}-{sku}'
        start_tag = f'<div class="model-block" id="{div_id}">'
        start_idx = content.find(start_tag)
        if start_idx != -1:
            start_content_idx = start_idx + len(start_tag)
            
            i = start_content_idx
            div_count = 1
            while i < len(content):
                if content[i:i+4] == '<div':
                    div_count += 1
                    i += 4
                elif content[i:i+6] == '</div>':
                    div_count -= 1
                    if div_count == 0:
                        break
                    i += 6
                else:
                    i += 1
            end_idx = i
            block_content = content[start_content_idx:end_idx]
            
            new_sec2, new_sec3 = generate_rgb_sections(sku)
            if not new_sec2:
                continue
                
            sec_starts = [m.start() for m in re.finditer(r'<section', block_content)]
            sec_ends = [m.end() for m in re.finditer(r'</section>', block_content)]
            
            if len(sec_starts) >= 3:
                before_sec2 = block_content[:sec_starts[1]]
                after_sec3 = block_content[sec_ends[2]:]
                
                block_content = before_sec2 + new_sec2 + "\n" + new_sec3 + after_sec3
                content = content[:start_content_idx] + block_content + content[end_idx:]
                
                ta_id = f'textarea-{platform}-{sku}'
                ta_start_tag = f'<textarea class="edit-textarea" id="{ta_id}" oninput="onDescriptionInput(\'{platform}\', \'profile\', \'{sku}\')">'
                ta_start = content.find(ta_start_tag)
                
                if ta_start == -1:
                    match = re.search(f'<textarea class="edit-textarea" id="{ta_id}"[^>]*>', content)
                    if match:
                        ta_start_tag = match.group(0)
                        ta_start = match.start()
                
                if ta_start != -1:
                    ta_content_start = ta_start + len(ta_start_tag)
                    ta_end = content.find('</textarea>', ta_content_start)
                    if ta_end != -1:
                        escaped_html = html.escape(block_content.strip())
                        content = content[:ta_content_start] + escaped_html + content[ta_end:]

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"RGB/RGBW tapes rewritten successfully. Found SKUs: {skus}")
