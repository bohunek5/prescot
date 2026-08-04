with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('data-model="PR-MONO-12A"')
end_idx = content.find('</div>\n</div>\n<div class="product-accordion"', idx)
if end_idx == -1:
    end_idx = content.find('data-model="PR-CCT-12A"')
print(content[end_idx-1500:end_idx])
