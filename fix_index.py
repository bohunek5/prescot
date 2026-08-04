import sys

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add sub-tabs to WAPRO
wapro_panel_start = '<!-- ==================== WAPRO TAB PANEL ==================== -->\n<div class="main-tab-panel active" id="panel-wapro">\n<!-- SUB-TABS -->\n'
wapro_sub_tabs = '''<div class="sub-tabs">
<button class="active" onclick="switchSubTab('wapro', 'tasmy', this)"><svg fill="none" height="18" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewbox="0 0 24 24" width="18"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.9 1.2 1.5 1.5 2.5"></path><path d="M9 18h6"></path><path d="M10 22h4"></path></svg> Taśmy LED (22)</button>
<button onclick="switchSubTab('wapro', 'sterowniki', this)"><svg fill="none" height="18" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewbox="0 0 24 24" width="18"><line x1="21" x2="14" y1="4" y2="4"></line><line x1="10" x2="3" y1="4" y2="4"></line><line x1="21" x2="12" y1="12" y2="12"></line><line x1="8" x2="3" y1="12" y2="12"></line><line x1="21" x2="16" y1="20" y2="20"></line><line x1="12" x2="3" y1="20" y2="20"></line><line x1="14" x2="14" y1="1" y2="7"></line><line x1="8" x2="8" y1="9" y2="15"></line><line x1="16" x2="16" y1="17" y2="23"></line></svg> Sterowniki LED (5)</button>
<button onclick="switchSubTab('wapro', 'zasilacze', this)"><svg fill="none" height="18" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewbox="0 0 24 24" width="18"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg> Zasilacze Scharfer (20)</button>
<button onclick="switchSubTab('wapro', 'profile', this)"><svg fill="none" height="18" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewbox="0 0 24 24" width="18"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"></path><path d="M3.27 6.96L12 12.01l8.73-5.05"></path><path d="M12 22.08V12"></path></svg> Profile KLUŚ (21)</button>
<button onclick="switchSubTab('wapro', 'zlaczki', this)"><svg fill="none" height="18" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewbox="0 0 24 24" width="18"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg> Złączki bezlutowe (17)</button>
</div>
'''
html = html.replace(wapro_panel_start, wapro_panel_start + wapro_sub_tabs)

# 2. Fix the missing </div> at the end of wapro-tasmy
# Before: </section></div>\n</div></div>\n<div class="sub-tab-panel" id="wapro-sterowniki">
# It needs an extra </div> to close wapro-tasmy properly.
search_target = '</div></div>\n<div class="sub-tab-panel" id="wapro-sterowniki">'
replace_target = '</div></div>\n</div>\n<div class="sub-tab-panel" id="wapro-sterowniki">'
html = html.replace(search_target, replace_target)

# 3. Inject new products inside wapro-tasmy
with open('new_products.html', 'r', encoding='utf-8') as f:
    new_prods = f.read()

# We want to insert right before the newly added </div> that closes wapro-tasmy
# The new signature is: </div></div>\n</div>\n<div class="sub-tab-panel" id="wapro-sterowniki">
# Let's just find: \n</div>\n<div class="sub-tab-panel" id="wapro-sterowniki">
injection_point = '\n</div>\n<div class="sub-tab-panel" id="wapro-sterowniki">'
if injection_point in html:
    html = html.replace(injection_point, '\n' + new_prods + injection_point)
else:
    print("Injection point not found!")
    sys.exit(1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Fixed WAPRO sub-tabs and injected products.")
