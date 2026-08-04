import re
import random

def rewrite_rgbw():
    with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    def generate_technical_rgbw_sections(sku):
        sku_upper = sku.upper()
        
        # Determine features based on sku
        is_rgbww = 'RGBWW' in sku_upper
        is_rgbnw = 'RGBNW' in sku_upper
        is_rgbw = 'RGBW' in sku_upper and not (is_rgbww or is_rgbnw)
        is_rgbcct = 'RGBCCT' in sku_upper
        is_rgb = 'RGB' in sku_upper and not (is_rgbw or is_rgbww or is_rgbnw or is_rgbcct)

        if is_rgbww:
            tech_type = "RGB + Ciepła Biel (3000K)"
            white_desc = "dedykowany obwód dla barwy ciepłej bieli (3000K), zapewniający wysoki wskaźnik oddawania barw (CRI) dla oświetlenia bazowego"
        elif is_rgbnw:
            tech_type = "RGB + Neutralna Biel (4000K)"
            white_desc = "zintegrowany kanał neutralnej bieli (4000K), oferujący czyste, użytkowe światło bez zanieczyszczeń kolorystycznych charakterystycznych dla mieszania barw z palety RGB"
        elif is_rgbcct:
            tech_type = "RGB + CCT (Tunable White)"
            white_desc = "podwójny obwód bieli (Ciepła i Zimna), umożliwiający płynną regulację temperatury barwowej CCT niezależnie od strumienia RGB"
        elif is_rgbw:
            tech_type = "RGBW (4-kanałowa)"
            white_desc = "niezależny, dedykowany kanał białego światła dla precyzyjnego oświetlenia architektonicznego"
        else:
            tech_type = "RGB (Pełne widmo barw)"
            white_desc = "optymalizację pod kątem płynnego mieszania barw (Color Mixing) i nasycenia dla dynamicznych scen świetlnych"

        titles_s2 = [
            f"Zaawansowana technologia 4-kanałowa: {tech_type}",
            f"Architektura wieloobwodowa: {tech_type}",
            f"Specyfikacja układu scalonego: {tech_type}"
        ]
        
        texts_s2 = [
            f"Taśma oparta na architekturze wielokanałowej, integrująca pełną paletę RGB oraz {white_desc}. Rozdzielenie strumienia światła białego od kolorowego eliminuje zjawisko 'brudnej bieli', typowe dla standardowych taśm RGB. Zastosowanie selekcjonowanych diod gwarantuje wysoką sprawność świetlną kanału białego, idealną do zadań użytkowych, podczas gdy moduł RGB służy do budowy akcentów i scen w automatyce budynkowej.",
            f"Zaprojektowana z myślą o profesjonalnych instalacjach systemów Smart Home i DALI. Model ten łączy nasycone barwy palety RGB oraz {white_desc}. Takie rozwiązanie sprzętowe pozwala zredukować liczbę niezbędnych zasilaczy i taśm w profilu, gwarantując bezproblemowe przejście z trybu oświetlenia architektonicznego na dynamiczne iluminacje bez kompromisów jakościowych w parametrach świetlnych.",
            f"Wieloobwodowa struktura laminatu umożliwia niezależne sterowanie kanałami. Produkt charakteryzuje się implementacją modułu RGB oraz {white_desc}. Precyzyjny dobór komponentów zapewnia jednolitą chrominancję na całej długości rolki, a zwiększona zawartość miedzi na PCB skutecznie redukuje spadki napięcia, co jest kluczowe w rozbudowanych liniach światła z użyciem 4- i 5-kanałowych sterowników PWM."
        ]
        
        titles_s3 = [
            "Optymalizacja pod zaawansowane systemy sterowania",
            "Kompatybilność ze sterownikami PWM / DALI / KNX",
            "Integracja w instalacjach wielostrefowych"
        ]
        
        texts_s3 = [
            "Instalacja wymaga zastosowania dedykowanych, wielokanałowych sterowników LED (PWM) o wysokiej częstotliwości taktowania (np. seria MiBoxer lub profesjonalne aktory KNX/DALI). Taśma zachowuje pełną liniowość ściemniania i mieszania barw w pełnym zakresie od 1% do 100%, całkowicie redukując efekt migotania (flickering-free) przy odpowiednim wysterowaniu, co stanowi krytyczny wymóg w obiektach komercyjnych i hotelowych.",
            "Taśma jest przystosowana do ciągłej pracy z obciążeniem pulsacyjnym, typowym dla kontrolerów RGBW. Odpowiedni przekrój ścieżek transmisyjnych (ścieżki anodowe i katodowe) pozwala na realizację wielometrowych instalacji przy zachowaniu spójności świetlnej. Wymaga podłączenia pod specjalistyczne sterowniki stałonapięciowe kompatybilne z systemami nadrzędnymi, zapewniającymi 100% płynności podczas tranzycji barw i dimmowania.",
            "Dzięki wielokanałowej topologii, taśma sprawdza się w projektach, gdzie wymagana jest zmiana charakterystyki oświetleniowej w zależności od harmonogramu, np. za pomocą systemów zarządzania budynkiem (BMS). Podział na autonomiczne obwody wymaga starannego doboru jednostki sterującej. Profil taśmy umożliwia precyzyjne adresowanie w wielostrefowych środowiskach instalacyjnych, zachowując restrykcyjne wymogi dotyczące emisji cieplnej w oprawach z aluminium."
        ]

        # For pure RGB, slightly adjust text if needed
        if is_rgb:
            texts_s2 = [
                "Zastosowanie dedykowanych struktur półprzewodnikowych dla barwy czerwonej, zielonej i niebieskiej pozwala na uzyskanie ponad 16 milionów kombinacji kolorystycznych przy zastosowaniu profesjonalnych mikrokontrolerów. Laminat o zwiększonej gęstości ścieżek zasilających zapewnia stabilność temperaturową dla pełnego spektrum, co bezpośrednio przekłada się na żywotność luminoforu i brak odchyłek kolorometrycznych w długich obwodach.",
                "Model oparty wyłącznie na diodach typu RGB, dedykowany do instalacji wymagających nasyconych, mocnych akcentów kolorystycznych i oświetlenia efektowego. Każdy chip (Red, Green, Blue) charakteryzuje się wyrównaną degradacją prądową, zapewniającą równomierny spadek strumienia w czasie. System wymaga zastosowania 3-kanałowych kontrolerów PWM dla optymalnego renderowania barw w przestrzeni architektonicznej."
            ]

        sec2_content = f"""<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">BUDOWA I TECHNOLOGIA</font>
</span><h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">{random.choice(titles_s2)}</h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">{random.choice(texts_s2)}</p>
</section>"""

        sec3_content = f"""<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">STEROWANIE I INTEGRACJA</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">{random.choice(titles_s3)}</h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">{random.choice(texts_s3)}</p>
</section>"""
        
        return sec2_content, sec3_content

    # Split content by accordion blocks
    blocks = re.split(r'(<div class="product-accordion" data-model="[^"]+">)', content)
    
    new_content = blocks[0]
    
    for i in range(1, len(blocks), 2):
        block_header = blocks[i]
        block_body = blocks[i+1]
        
        sku_match = re.search(r'data-model="([^"]+)"', block_header)
        sku = sku_match.group(1) if sku_match else ""
        
        # Only rewrite if it's a TAPE with RGB in the SKU. Ignore FC10 connectors.
        # "PR-RGB" or "E033...RGB"
        if 'RGB' in sku.upper() and 'FC10' not in sku.upper() and ('E033' in sku.upper() or 'PR-' in sku.upper()):
            
            # Find the model block
            model_block_match = re.search(r'(<div class="model-block" id="desc-view-wapro-[^"]+">)(.*?)(</div>\s*<div class="edit-block")', block_body, re.DOTALL)
            if model_block_match:
                prefix = model_block_match.group(1)
                sections_content = model_block_match.group(2)
                suffix = model_block_match.group(3)
                
                # Split sections
                sections = re.findall(r'<section.*?</section>', sections_content, re.DOTALL)
                
                if len(sections) >= 3:
                    # Replace the 2nd and 3rd sections
                    sec2, sec3 = generate_technical_rgbw_sections(sku)
                    sections[1] = sec2
                    sections[2] = sec3
                    
                    new_sections_content = "".join(sections)
                    
                    # Replace in block_body
                    old_full_model_block = model_block_match.group(0)
                    new_full_model_block = prefix + new_sections_content + suffix
                    block_body = block_body.replace(old_full_model_block, new_full_model_block)
                    
                    # Now update the textarea content too
                    textarea_match = re.search(r'(<textarea[^>]+>)(.*?)(</textarea>)', block_body, re.DOTALL)
                    if textarea_match:
                        ta_prefix = textarea_match.group(1)
                        ta_suffix = textarea_match.group(3)
                        
                        import html
                        encoded_content = html.escape(new_sections_content, quote=False)
                        new_textarea = ta_prefix + encoded_content + ta_suffix
                        
                        block_body = block_body.replace(textarea_match.group(0), new_textarea)
                        
        new_content += block_header + block_body

    with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == "__main__":
    rewrite_rgbw()
