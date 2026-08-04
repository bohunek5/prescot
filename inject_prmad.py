import re
from bs4 import BeautifulSoup

def main():
    print("Loading index.html...")
    with open("index.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
    print("Renaming 'Zasilacze Scharfer' to 'Zasilacze LED'...")
    # Find the buttons for Zasilacze
    for button in soup.find_all('button', onclick=re.compile(r"switchSubTab\('.*', 'zasilacze'")):
        # The button contains text like " Zasilacze Scharfer (20)"
        if button.string:
            # this might not work if it contains svg
            pass
        # better to just replace the text in the raw html later, or navigate children
        for child in button.contents:
            if isinstance(child, str) and "Zasilacze Scharfer" in child:
                # keep the number if possible
                new_str = re.sub(r'Zasilacze Scharfer( \(\d+\))?', r'Zasilacze LED\1', child)
                child.replace_with(new_str)
                
    models = [
        {"sku": "PR-MAD36-1224", "power": "36W", "current": "3A(12V)/1.5A(24V)", "dim": "145 × 50 × 29 mm", "weight": "180g"},
        {"sku": "PR-MAD60-1224", "power": "60W", "current": "5A(12V)/2.5A(24V)", "dim": "145 × 50 × 29 mm", "weight": "200g"},
        {"sku": "PR-MAD100-1224", "power": "100W", "current": "8.3A(12V)/4.16A(24V)", "dim": "176 × 50 × 29 mm", "weight": "310g"},
        {"sku": "PR-MAD150-1224", "power": "150W", "current": "12.5A(12V)/6.25A(24V)", "dim": "199 × 50 × 29 mm", "weight": "390g"},
        {"sku": "PR-MAD200-1224", "power": "200W", "current": "16.6A(12V)/8.3A(24V)", "dim": "218 × 50 × 29 mm", "weight": "460g"},
        {"sku": "PR-MAD300-1224", "power": "300W", "current": "25A(12V)/12.5A(24V)", "dim": "240 × 50 × 29 mm", "weight": "590g"}
    ]
    
    tabs = ['wapro', 'tim', 'allegro', 'shoper']
    
    for tab in tabs:
        panel_id = f"{tab}-zasilacze"
        panel = soup.find('div', id=panel_id)
        if not panel:
            print(f"Warning: Panel {panel_id} not found.")
            continue
            
        for idx, model in enumerate(models):
            sku = model['sku']
            # skip if already exists
            if panel.find('div', attrs={'data-model': sku}):
                continue
            
            # create the html block
            html_content = f"""
<section style="font-family: inherit; margin: 28px 0 18px 0; padding: 22px 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
<span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;">
<span style="color: #ffffff;">Smart Auto-Identify (12V/24V)</span>
</span>
<h3 style="font-family: inherit; margin: 0 0 8px 0; background: none !important; background-color: transparent !important; color: inherit !important; font-size: 22px; line-height: 1.3; font-weight: bold;">Inteligentny Zasilacz LED - Rewolucja w instalacjach</h3>
<p style="font-family: inherit; margin: 0; background: none !important; background-color: transparent !important; color: inherit !important; opacity: .82; font-size: 14px; line-height: 1.65;">
Dzięki innowacyjnemu chipowi Smart Auto-Identification, zasilacz sam rozpoznaje podłączoną taśmę i automatycznie dostosowuje napięcie na poziomie 12V DC lub 24V DC. Wbudowany procesor impulsowy zabezpiecza taśmy przed uszkodzeniem.
</p>
</section>
<section style="font-family: inherit; margin: 0 0 18px 0; padding: 22px 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
<span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;">
<span style="color: #ffffff;">Zalewa Termiczna (Semi-Potted)</span>
</span>
<h3 style="font-family: inherit; margin: 0 0 8px 0; background: none !important; background-color: transparent !important; color: inherit !important; font-size: 22px; line-height: 1.3; font-weight: bold;">Ochrona i absolutnie cicha praca</h3>
<p style="font-family: inherit; margin: 0; background: none !important; background-color: transparent !important; color: inherit !important; opacity: .82; font-size: 14px; line-height: 1.65;">
Wnętrze wypełnione masą silikonowo-epoksydową perfekcyjnie odprowadza ciepło. Pasywne chłodzenie bez wentylatora to 100% bezgłośna praca, idealna do salonu czy sypialni. Ultra-Slim (zaledwie 29 mm) pozwala na montaż w najwęższych szczelinach. Pakiet Smart Protection Suite: OLP, SCP, OTP, OVP chroni instalację na lata.
</p>
</section>
<section style="font-family: inherit; margin: 0 0 28px 0; padding: 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
<span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;">
<span style="color: #ffffff;">Parametry modelu {sku}</span>
</span>
<div style="font-family: inherit; display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; background: none !important; background-color: transparent !important; color: inherit;">
<div style="font-family: inherit; padding: 16px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit;">
<strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Moc wyjściowa</strong>
<small style="font-family: inherit; display: block; color: inherit !important; opacity: .78; font-size: 13px; line-height: 1.45;">
<strong style="font-family: inherit; color: inherit !important;">{model['power']}</strong>
</small>
</div>
<div style="font-family: inherit; padding: 16px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit;">
<strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Wyjście DC</strong>
<small style="font-family: inherit; display: block; color: inherit !important; opacity: .78; font-size: 13px; line-height: 1.45;">
<strong style="font-family: inherit; color: inherit !important;">12V/24V Auto</strong> / {model['current']}
</small>
</div>
<div style="font-family: inherit; padding: 16px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit;">
<strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Wymiar i Waga</strong>
<small style="font-family: inherit; display: block; color: inherit !important; opacity: .78; font-size: 13px; line-height: 1.45;">{model['dim']} / {model['weight']}</small>
</div>
</div>
</section>
"""
            escaped_html = html_content.replace("<", "&lt;").replace(">", "&gt;")
            
            accordion = soup.new_tag("div", attrs={"class": "product-accordion", "data-model": sku})
            
            trigger = soup.new_tag("button", attrs={"class": "product-trigger", "onclick": "toggleProduct(this)"})
            info = soup.new_tag("div", attrs={"class": "product-info"})
            model_span = soup.new_tag("span", attrs={"class": "product-model"})
            model_span.string = f"{idx+21}. {sku}"
            badge_span = soup.new_tag("span", attrs={"class": "product-label-badge"})
            badge_span.string = f"Zasilacz LED Smart Auto 12V/24V {model['power']} Ultra-Slim"
            info.append(model_span)
            info.append(badge_span)
            arrow = soup.new_tag("span", attrs={"class": "product-arrow"})
            arrow.string = "▼"
            trigger.append(info)
            trigger.append(arrow)
            
            body = soup.new_tag("div", attrs={"class": "product-body"})
            
            model_block = soup.new_tag("div", attrs={"class": "model-block", "id": f"desc-view-{tab}-{sku}"})
            model_block.append(BeautifulSoup(html_content, "html.parser"))
            
            edit_block = soup.new_tag("div", attrs={"class": "edit-block", "id": f"desc-edit-{tab}-{sku}", "style": "display: none;"})
            textarea = soup.new_tag("textarea", attrs={
                "class": "edit-textarea", 
                "id": f"textarea-{tab}-{sku}", 
                "oninput": f"onDescriptionInput('{tab}', 'zasilacze', '{sku}')"
            })
            textarea.string = html_content.strip()
            edit_block.append(textarea)
            
            body.append(model_block)
            body.append(edit_block)
            
            accordion.append(trigger)
            accordion.append(body)
            
            panel.append(accordion)
            print(f"Added {sku} to {tab}")

    print("Saving index.html...")
    # writing using string replacement as bs4 can mess up the file structure slightly
    # actually, BS4 modifies the whole file but it should be fine.
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
    
    # Let's also do a raw replacement for "Zasilacze Scharfer (20)" if it wasn't caught
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r'Zasilacze Scharfer( \(\d+\))?', r'Zasilacze LED (26)', content)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
