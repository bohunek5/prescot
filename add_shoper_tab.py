import os
import requests
import json
import time
from bs4 import BeautifulSoup
import re
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def call_ollama(prompt, system_prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_predict": 4096,
            "num_ctx": 16384
        }
    }
    try:
        t0 = time.time()
        response = requests.post(OLLAMA_URL, json=payload, timeout=240)
        response.raise_for_status()
        res = response.json().get("response", "")
        log(f"Ollama returned {len(res)} chars in {time.time()-t0:.1f}s")
        return res
    except Exception as e:
        log(f"Error calling Ollama: {e}")
        return ""

def main():
    log("Loading index.html...")
    with open("index.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    log("Adding Shoper CSS...")
    style_tag = soup.find('style')
    if style_tag and '.main-tab-btn.shoper' not in style_tag.string:
        shoper_css = """
/* SHOPER TAB */
.main-tab-btn.shoper.active {
    background: #000000;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.main-tab-btn.shoper.active .brand-name {
    color: #ffffff;
}
.shoper-logo img {
    height: 30px;
    object-fit: contain;
    border-radius: 4px;
}
"""
        style_tag.string += shoper_css

    log("Adding Shoper main tab button...")
    main_tabs = soup.find('div', class_='main-tabs')
    if main_tabs and not main_tabs.find('button', class_='shoper'):
        new_btn = soup.new_tag('button', attrs={
            'class': 'main-tab-btn shoper',
            'onclick': "switchMainTab('shoper')"
        })
        logo_div = soup.new_tag('div', attrs={'class': 'brand-logo shoper-logo'})
        img = soup.new_tag('img', attrs={
            'src': 'ikona shoper.svg',
            'alt': 'Shoper',
            'style': 'height: 30px; object-fit: contain; border-radius: 4px;'
        })
        text_div = soup.new_tag('div')
        name_div = soup.new_tag('div', attrs={'class': 'brand-name'})
        name_div.string = "SHOPER"
        text_div.append(name_div)
        
        logo_div.append(img)
        logo_div.append(text_div)
        new_btn.append(logo_div)
        main_tabs.append(new_btn)

    log("Cloning panel-wapro to panel-shoper...")
    panel_wapro = soup.find('div', id='panel-wapro')
    if not panel_wapro:
        log("Error: Could not find panel-wapro")
        return

    if soup.find('div', id='panel-shoper'):
        log("Panel shoper already exists. Updating descriptions only.")
        panel_shoper = soup.find('div', id='panel-shoper')
    else:
        import copy
        panel_shoper = copy.copy(panel_wapro)
        panel_shoper['id'] = 'panel-shoper'
        panel_shoper['class'] = ['main-tab-panel'] # remove active
        
        for tag in panel_shoper.find_all(True):
            if tag.has_attr('id') and 'wapro' in tag['id']:
                tag['id'] = tag['id'].replace('wapro', 'shoper')
            
            if tag.has_attr('onclick'):
                tag['onclick'] = tag['onclick'].replace("'wapro'", "'shoper'")
                
            if tag.has_attr('class') and 'wapro' in tag['class']:
                tag['class'] = [c.replace('wapro', 'shoper') for c in tag['class']]
                
        panels = soup.find_all('div', class_=re.compile(r'main-tab-panel'))
        panels[-1].insert_after(panel_shoper)
        # save intermediate so we don't lose the tab if it crashes
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(str(soup))
        log("Intermediate index.html saved with Shoper tab structure.")

    log("Generating Shoper descriptions via Ollama...")
    shoper_views = panel_shoper.find_all('div', id=re.compile(r'desc-view-shoper-.*'))
    
    total = len(shoper_views)
    log(f"Found {total} products to process.")
    
    system_prompt = (
        "Jesteś zaawansowanym copywriterem e-commerce. "
        "Twoim zadaniem jest stworzenie nowego, unikalnego i silnie konwertującego opisu "
        "produktu dla platformy Shoper. Będziesz miał do dyspozycji 3 wersje tego samego "
        "produktu (z WAPRO, ALLEGRO i TIM). "
        "Wyciągnij najlepsze cechy techniczne i sprzedażowe z tych 3 wersji i "
        "zbuduj profesjonalny opis w czystym HTML. ZACHOWAJ formatowanie w tagach <section> "
        "oraz style CSS. Wypluj TYLKO kod HTML, bez markdown czy wstępów."
    )
    
    count = 0
    TEST_MODE = True
    test_limit = 2
    
    for shoper_view in shoper_views:
        if TEST_MODE and count >= test_limit:
            break
            
        sku_match = re.search(r'desc-view-shoper-(.+)', shoper_view['id'])
        if not sku_match:
            continue
        
        sku = sku_match.group(1)
        log(f"Processing {sku} ({count+1}/{total})...")
        
        wapro_view = soup.find('div', id=f'desc-view-wapro-{sku}')
        allegro_view = soup.find('div', id=f'desc-view-allegro-{sku}')
        tim_view = soup.find('div', id=f'desc-view-tim-{sku}')
        
        wapro_html = wapro_view.decode_contents() if wapro_view else "Brak opisu WAPRO"
        allegro_html = allegro_view.decode_contents() if allegro_view else "Brak opisu ALLEGRO"
        tim_html = tim_view.decode_contents() if tim_view else "Brak opisu TIM"
        
        prompt = (
            f"Stwórz opis Shoper dla produktu SKU: {sku}.\n\n"
            f"--- OPIS WAPRO ---\n{wapro_html}\n\n"
            f"--- OPIS ALLEGRO ---\n{allegro_html}\n\n"
            f"--- OPIS TIM ---\n{tim_html}\n\n"
            f"Wygeneruj tylko kod HTML (np. <section>...<h1>...</h1>...</section>)."
        )
        
        response = call_ollama(prompt, system_prompt)
        
        if response:
            response = response.replace("```html", "").replace("```", "").strip()
            
            sections_to_remove = []
            for child in shoper_view.children:
                if getattr(child, 'name', None) == 'section' and 'product-parameters-section' not in child.get('class', []):
                    sections_to_remove.append(child)
            
            for sec in sections_to_remove:
                sec.decompose()
                
            new_html_soup = BeautifulSoup(response, "html.parser")
            shoper_view.append(new_html_soup)
            
            edit_textarea = soup.find('textarea', id=f'textarea-shoper-{sku}')
            if edit_textarea:
                edit_textarea.string = response
                
            log(f"Updated {sku} successfully.")
        else:
            log(f"Failed to generate for {sku}")
            
        count += 1
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(str(soup))

    log("Done! Check index.html.")

if __name__ == "__main__":
    main()
