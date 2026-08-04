import sys

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('new_products.html', 'r', encoding='utf-8') as f:
    new_prods = f.read()

# Find the start of wapro-sterowniki
target_str = '<div class="sub-tab-panel" id="wapro-sterowniki">'
idx = html.find(target_str)
if idx == -1:
    print("Could not find wapro-sterowniki!")
    sys.exit(1)

# Backtrack to the last </div> before idx
before = html[:idx]
after = html[idx:]

# The last few characters of 'before' should be </div></div>\n
# We want to insert the new products INSIDE the sub-tab-panel wapro-tasmy, so we insert before the last </div>.
last_div_idx = before.rfind('</div>')
if last_div_idx == -1:
    print("Could not find </div>")
    sys.exit(1)

# Let's just insert new_prods exactly before the last </div>
new_html = before[:last_div_idx] + '\n' + new_prods + '\n' + before[last_div_idx:] + after

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Injected new products successfully.")
