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
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": 2048,
            "num_ctx": 4096
        }
    }
    try:
        t0 = time.time()
        # Zwiększony timeout, ale dzięki tekstowi będzie szybciej
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
        res = response.json().get("response", "")
        log(f"Ollama returned {len(res)} chars in {time.time()-t0:.1f}s")
        return res
    except Exception as e:
        log(f"Error calling Ollama: {e}")
        return ""

def get_clean_text(soup_element):
    if not soup_element:
        return ""
    # Extract only text, separated by space, ignoring HTML tags
    return soup_element.get_text(separator=' ', strip=True)

def main():
    log("Loading index.html...")
    with open("index.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    panel_shoper = soup.find('div', id='panel-shoper')
    if not panel_shoper:
        log("Error: panel-shoper not found. Run structure script first.")
        return

    shoper_views = panel_shoper.find_all('div', id=re.compile(r'desc-view-shoper-.*'))
    total = len(shoper_views)
    log(f"Found {total} products to process.")
    
    system_prompt = (
        "Jesteś zaawansowanym copywriterem e-commerce (SEO, CRO) z wieloletnim doświadczeniem. "
        "Otrzymujesz surowe dane i cechy produktu (z trzech różnych źródeł: Wapro, Allegro, TIM). "
        "Twoim zadaniem jest zsyntetyzowanie tych informacji i stworzenie jednego, wysoce konwertującego, "
        "angażującego i poprawnego językowo opisu produktu dla sklepu Shoper. "
        "OPIS MUSI BYĆ SFORMATOWANY W CZYSTYM HTML. "
        "Użyj struktury: <section> na główny kontener, w środku <h2> dla nagłówków sekcji, <p> dla akapitów, <ul><li> dla list zalet. "
        "Brak lania wody, konkretne korzyści. Zwróć TYLKO kod HTML, bez bloku kodu (bez znaczników ```html i ```). "
        "Nie pisz żadnego wstępu ani podsumowania."
    )
    
    count = 0
    
    for shoper_view in shoper_views:
        sku_match = re.search(r'desc-view-shoper-(.+)', shoper_view['id'])
        if not sku_match:
            continue
        
        sku = sku_match.group(1)
        
        # Check if it was already processed (if there is a proper section)
        # For our case we will process all to be sure, or check if it has shoper specific content.
        # Since it was cloned from wapro, the edit_textarea will have WAPRO content initially.
        edit_textarea = soup.find('textarea', id=f'textarea-shoper-{sku}')
        if edit_textarea and "WAPRO" not in edit_textarea.text and len(edit_textarea.text) > 100:
            # Maybe already processed? We'll reprocess anyway to be sure, or skip?
            pass
            
        log(f"Processing {sku} ({count+1}/{total})...")
        
        wapro_view = soup.find('div', id=f'desc-view-wapro-{sku}')
        allegro_view = soup.find('div', id=f'desc-view-allegro-{sku}')
        tim_view = soup.find('div', id=f'desc-view-tim-{sku}')
        
        wapro_text = get_clean_text(wapro_view) if wapro_view else "Brak"
        allegro_text = get_clean_text(allegro_view) if allegro_view else "Brak"
        tim_text = get_clean_text(tim_view) if tim_view else "Brak"
        
        prompt = (
            f"Stwórz opis Shoper dla produktu (SKU: {sku}).\n\n"
            f"--- INFO Z WAPRO ---\n{wapro_text[:1500]}\n\n"
            f"--- INFO Z ALLEGRO ---\n{allegro_text[:1500]}\n\n"
            f"--- INFO Z TIM ---\n{tim_text[:1500]}\n\n"
            f"Wygeneruj ostateczny HTML (tylko tagi HTML)."
        )
        
        response = call_ollama(prompt, system_prompt)
        
        if response:
            response = response.replace("```html", "").replace("```", "").strip()
            # If the model didn't wrap in <section>, wrap it
            if not response.startswith("<section"):
                response = f"<section>\n{response}\n</section>"
                
            sections_to_remove = []
            for child in shoper_view.children:
                if getattr(child, 'name', None) == 'section' and 'product-parameters-section' not in child.get('class', []):
                    sections_to_remove.append(child)
            
            for sec in sections_to_remove:
                sec.decompose()
                
            new_html_soup = BeautifulSoup(response, "html.parser")
            shoper_view.append(new_html_soup)
            
            if edit_textarea:
                edit_textarea.string = response
                
            log(f"Updated {sku} successfully.")
        else:
            log(f"Failed to generate for {sku}")
            
        count += 1
        
        # Save incrementally every 5 products to avoid losing progress
        if count % 5 == 0:
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(str(soup))
            log("Saved intermediate index.html")

    # Final save
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
    log("All products processed and saved to index.html.")
    
    # Auto commit and push
    log("Pushing to git...")
    os.system('git add index.html')
    os.system('git commit -m "Auto-generated Shoper descriptions via AI combine"')
    os.system('git push')
    log("Done. Sleeping.")

if __name__ == "__main__":
    main()
