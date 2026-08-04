import re
import random

def rewrite_klus():
    with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    def get_profile_info(sku):
        if 'A01587' in sku:
            return 'MICRO-NK'
        elif 'A02966' in sku:
            return 'MICRO-PLUS'
        return 'KLUŚ'

    def generate_klosze_section(sku):
        p_type = get_profile_info(sku)
        
        # We need a professional, B2B tone.
        titles = [
            f"Kompatybilność z osłonami Kluś: LIGER, HS i KA",
            f"Dobór kloszy (brak w zestawie): System LIGER / HS / KA",
            f"Akcesoria optyczne (Klosze sprzedawane osobno)"
        ]
        
        texts = [
            f"Oferowany profil {p_type} stanowi bazowy profil aluminiowy. Klosze (osłony) nie wchodzą w skład zestawu i należy je nabyć osobno, co pozwala na precyzyjne dopasowanie parametrów świetlnych do wymogów projektu. System jest w pełni kompatybilny z osłonami mlecznymi LIGER-11 (rekomendowanymi do uzyskania ciągłej linii światła bez widocznych punktów), oraz kloszami przezroczystymi KA i HS, które zapewniają maksymalną transmisję światła i zminimalizowane straty lumenów.",
            f"Z uwagi na modułowy charakter systemu KLUŚ, osłona (klosz) nie jest dostarczana w komplecie z profilem {p_type}. Do architektonicznych instalacji oświetleniowych rekomendujemy zastosowanie kloszy mlecznych LIGER-11, które w połączeniu z odpowiednio gęstą taśmą LED eliminują efekt olśnienia i zapewniają gładką linię światła. Dla aplikacji technicznych, wymagających maksymalnej wydajności, dostępne są kompatybilne klosze transparentne KA i HS.",
            f"Profil aluminiowy {p_type} wymaga skompletowania z odpowiednią osłoną – klosze nie są elementem zestawu. System KLUŚ oferuje pełną kompatybilność z kloszem wciskanym LIGER-11 (wersja mleczna, optymalnie rozpraszająca światło i niwelująca zjawisko olśnienia) oraz transparentnymi osłonami HS i KA. Dobór odpowiedniego klosza pozwala na precyzyjne zarządzanie strumieniem świetlnym i kątem rozsyłu w docelowej instalacji."
        ]
        
        title = random.choice(titles)
        text = random.choice(texts)
        
        return f"""<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">DOBÓR KLOSZA (KLUŚ)</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">{title}</h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">{text}</p>
</section>"""

    # We want to replace the THIRD section in blocks that contain "PROFIL KLUŚ"
    # Wait, the safest way is to find blocks for models starting with "A01587" or "A02966"
    
    # Split content by accordion blocks
    blocks = re.split(r'(<div class="product-accordion" data-model="[^"]+">)', content)
    
    new_content = blocks[0]
    
    for i in range(1, len(blocks), 2):
        block_header = blocks[i]
        block_body = blocks[i+1]
        
        # Extract sku
        sku_match = re.search(r'data-model="([^"]+)"', block_header)
        sku = sku_match.group(1) if sku_match else ""
        
        if "A01587" in sku or "A02966" in sku:
            # We are in a Kluś block.
            # We want to replace the third <section ... > ... </section> inside <div class="model-block" ...>
            
            # Find the model block
            model_block_match = re.search(r'(<div class="model-block" id="desc-view-wapro-[^"]+">)(.*?)(</div>\s*<div class="edit-block")', block_body, re.DOTALL)
            if model_block_match:
                prefix = model_block_match.group(1)
                sections_content = model_block_match.group(2)
                suffix = model_block_match.group(3)
                
                # Split sections
                sections = re.findall(r'<section.*?</section>', sections_content, re.DOTALL)
                
                if len(sections) >= 3:
                    # Replace the third section
                    sections[2] = generate_klosze_section(sku)
                    
                    # Reconstruct the model block content
                    new_sections_content = "".join(sections)
                    
                    # Ensure we keep the "Praktyczne poradniki" section which might be the 4th section or outside?
                    # Wait, "Praktyczne poradniki" is a <section> as well!
                    # Let's check how many sections there are. Usually 4 (3 content + 1 poradniki).
                    # Actually, we can just replace sections[2].
                    
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
    rewrite_klus()
