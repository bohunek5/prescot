#!/usr/bin/env python3
"""
Injector script to safely add WCOB models to index.html
"""
import re
import sys
from generate_wcob_models import WCOB_MODELS, build_accordion

INDEX_PATH = "/Users/karolbohdanowicz/my-ai-agents/prescot/index.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# Make backup
with open(INDEX_PATH + ".bak", "w", encoding="utf-8") as f:
    f.write(html)
print("Backup created at index.html.bak")

# Check existing models to avoid duplicates
existing_models = set(re.findall(r'data-model=\"([^\"]+)\"', html))
print(f"Existing models in index.html: {len(existing_models)}")

# Update sub-tab counters:
# WAPRO: Taśmy LED (78) -> (82)
# TIM: Taśmy LED (34) -> (38)
# ALLEGRO: Taśmy LED (34) -> (38)
# SHOPER: Taśmy LED (78) -> (82)

# First let's check current subtab button texts
# We want to replace Taśmy LED (78) with Taśmy LED (82) in wapro and shoper, and Taśmy LED (34) with Taśmy LED (38) in tim and allegro.
# Let's inspect sub-tabs for each panel:
panels = ['wapro', 'tim', 'allegro', 'shoper']

for plat in panels:
    panel_regex = re.compile(rf'(<div class=\"main-tab-panel[^\"]*\" id=\"panel-{plat}\">[\s\S]*?)(?=<div class=\"main-tab-panel|\Z)')
    m_panel = panel_regex.search(html)
    if not m_panel:
        print(f"ERROR: panel-{plat} not found!")
        sys.exit(1)
    
    panel_content = m_panel.group(1)
    
    # 1. Update subtab button text in this panel
    # find <button class="sub-tab-btn active" onclick="switchSubTab('{plat}', 'tasmy', this)">...Taśmy LED (\d+)...</button>
    subtab_btn_pattern = rf'(onclick=\"switchSubTab\(\'{plat}\',\s*\'tasmy\',\s*this\)\"[^>]*>[\s\S]*?Taśmy LED\s*\()\d+(\))'
    
    def repl_subtab(match):
        new_cnt = "82" if plat in ['wapro', 'shoper'] else "38"
        return f"{match.group(1)}{new_cnt}{match.group(2)}"
    
    panel_content_new = re.sub(subtab_btn_pattern, repl_subtab, panel_content, count=1)
    
    # 2. Append new accordions at the end of tasmy sub-panel in this platform
    # Find the end of id="{plat}-tasmy"
    tasmy_panel_pattern = rf'(<div class=\"sub-tab-panel[^\"]*\" id=\"{plat}-tasmy\">[\s\S]*?)(</div>\s*<div class=\"sub-tab-panel\" id=\"{plat}-sterowniki\")'
    m_tasmy = re.search(tasmy_panel_pattern, panel_content_new)
    if not m_tasmy:
        print(f"ERROR: {plat}-tasmy subpanel boundary not found!")
        sys.exit(1)
    
    tasmy_body = m_tasmy.group(1)
    tasmy_tail = m_tasmy.group(2)
    
    # Check current item numbers in this subpanel
    curr_items = re.findall(r'<span class=\"product-model\">(\d+)\.\s*([^<]+)</span>', tasmy_body)
    start_num = len(curr_items)
    print(f"Platform {plat}: currently has {start_num} items in tasmy panel.")
    
    new_accordions_list = []
    for idx, model_data in enumerate(WCOB_MODELS):
        item_num = start_num + idx + 1
        acc_html = build_accordion(model_data, plat, item_num)
        new_accordions_list.append(acc_html)
    
    injected_accordions = "\n" + "\n".join(new_accordions_list) + "\n"
    
    tasmy_body_updated = tasmy_body + injected_accordions
    panel_content_new = panel_content_new.replace(tasmy_body + tasmy_tail, tasmy_body_updated + tasmy_tail, 1)
    
    # Replace panel in full html
    html = html.replace(panel_content, panel_content_new, 1)
    print(f"Platform {plat}: Successfully injected {len(WCOB_MODELS)} WCOB models (numbers {start_num+1}-{start_num+len(WCOB_MODELS)})!")

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("Saved updated index.html successfully!")
