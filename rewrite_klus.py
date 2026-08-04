import re
import random
import html

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

def get_profile_info(sku):
    if 'A01587' in sku:
        p_type = 'MICRO-NK'
    elif 'A02966' in sku:
        p_type = 'MICRO-PLUS'
    else:
        return None
        
    if sku.endswith('_1'): length = '1-metrowy'
    elif sku.endswith('_2'): length = '2-metrowy'
    elif sku.endswith('_3'): length = '3-metrowy'
    else: length = 'aluminiowy'
    
    if 'A07' in sku: color = 'czarny anodowany'
    elif 'L10' in sku or 'L9010' in sku: color = 'biały lakierowany'
    elif 'NA' in sku: color = 'surowy'
    else: color = 'srebrny anodowany'
    
    return p_type, length, color

templates_title = [
    "Kompatybilność z kloszami Kluś",
    "Dobór odpowiedniego klosza (Brak w zestawie)",
    "Klosze i akcesoria do profilu {p_type}",
    "Ważne info: Klosz sprzedawany oddzielnie",
    "Zbuduj linię światła – dobór osłon",
    "Dedykowane klosze LIGER, KA, HS",
]

templates_desc = [
    "Prezentowany {length} profil {p_type} ({color}) to wyłącznie aluminiowy korpus. <b>Klosz nie wchodzi w skład zestawu</b>. Aby ukończyć instalację, dobierz odpowiednią osłonę z oferty Kluś: polecamy mleczny klosz LIGER-11 (wciskany) dla efektu gładkiej, jednolitej linii światła (bez widocznych punktów), lub przezroczyste klosze KA i HS dla maksymalnej przepustowości świetlnej.",
    
    "Zwracamy uwagę, że w ofercie znajduje się sam profil aluminiowy wariantu {p_type} ({length}, {color}). <b>Wszelkie klosze należy dokupić osobno</b>. Dla zachowania bezpunktowego efektu świetlnego najlepiej sprawdzi się mleczna osłona LIGER-11. W przypadku potrzeby mocniejszego oświetlenia, rekomendujemy transparentne osłony typu KA lub HS.",
    
    "Profil LED {p_type} ({color}, dł. {length}) dostarczamy jako pojedynczy element montażowy – <b>brak klosza w paczce</b>. W celu zamknięcia profilu i ochrony diod należy zastosować kompatybilne klosze Kluś. Do wyboru instalatorów pozostają wersje mleczne (np. LIGER-11, znakomicie maskujący kropki LED) oraz transparentne/szronione (KA, HS) oferujące wyższą jasność.",
    
    "Kupujesz profesjonalny, {length} korpus aluminiowy {p_type} w kolorze: {color}. <b>Pamiętaj, że osłony (klosze) sprzedawane są oddzielnie</b>. Do tego modelu idealnie pasują wsuwane i wciskane osłony z rodziny Kluś. Instalatorzy najczęściej sięgają po mleczny LIGER-11, by ukryć pojedyncze diody LED, lub po serię HS/KA dla większej wydajności świetlnej.",
    
    "Uwaga techniczna: {length} profil {color} z serii {p_type} <b>nie posiada klosza w komplecie</b>. Element ten dobiera się według potrzeb projektowych. Aby uzyskać elegancką, w pełni zblurowaną linię świetlną, rekomendujemy dokupienie mlecznej osłony LIGER-11. Jeżeli zależy Ci na maksymalnym doświetleniu blatu czy wnęki, wybierz przezroczysty klosz KA lub HS.",
]

def generate_html(sku):
    info = get_profile_info(sku)
    if not info: return None
    p_type, length, color = info
    
    t_title = random.choice(templates_title).format(p_type=p_type)
    t_desc = random.choice(templates_desc).format(p_type=p_type, length=length, color=color)
    
    return f"""<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">DOBÓR KLOSZA (KLUŚ)</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">{t_title}</h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">{t_desc}</p>
</section>"""

# Find all profile SKUs
skus = set(re.findall(r'data-model="(A01587[^"]+|A02966[^"]+)"', content))

for sku in skus:
    for platform in ['wapro', 'tim', 'allegro']:
        div_id = f'desc-view-{platform}-{sku}'
        start_tag = f'<div class="model-block" id="{div_id}">'
        start_idx = content.find(start_tag)
        if start_idx != -1:
            start_content_idx = start_idx + len(start_tag)
            
            # Find the end of the block
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
            
            # Find the "PROFIL KLUŚ" section in the block
            # We want to replace it.
            # Look for <section ... >...PROFIL KLUŚ...</section>
            
            new_section = generate_html(sku)
            
            # Use regex to find the section containing "PROFIL KLUŚ"
            match = re.search(r'<section[^>]*>.*?PROFIL KLUŚ.*?</section>', block_content, re.DOTALL)
            if match:
                block_content = block_content[:match.start()] + new_section + block_content[match.end():]
            else:
                # If not found, append before the last section
                sections = [m.start() for m in re.finditer(r'<section', block_content)]
                if len(sections) >= 3:
                    last_sec = sections[-1]
                    block_content = block_content[:last_sec] + new_section + "\n" + block_content[last_sec:]
                else:
                    block_content += "\n" + new_section
            
            content = content[:start_content_idx] + block_content + content[end_idx:]
            
            # Update textarea
            ta_id = f'textarea-{platform}-{sku}'
            ta_start_tag = f'<textarea class="edit-textarea" id="{ta_id}" oninput="onDescriptionInput(\'{platform}\', \'profile\', \'{sku}\')">'
            ta_start = content.find(ta_start_tag)
            if ta_start != -1:
                ta_content_start = ta_start + len(ta_start_tag)
                ta_end = content.find('</textarea>', ta_content_start)
                if ta_end != -1:
                    escaped_html = html.escape(block_content.strip())
                    content = content[:ta_content_start] + escaped_html + content[ta_end:]

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Klus profiles rewriten successfully with SEO variations!")
