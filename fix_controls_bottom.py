import bs4

with open('index.html', 'r', encoding='utf-8') as f:
    soup = bs4.BeautifulSoup(f.read(), 'html.parser')

controls = soup.find_all('div', class_='product-controls')

for c in controls:
    # find the parent product-body
    body = c.find_parent('div', class_='product-body')
    if body:
        # extract the controls
        c.extract()
        # append to the end of product-body
        body.append(c)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))
print("Controls moved to bottom using BeautifulSoup")
