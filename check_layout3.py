with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('id="desc-edit-wapro-PR-MAD36-1224"')
end_idx = content.find('</div>\n</div>\n<div class="product-accordion"', idx)
print(content[idx:end_idx+200])
