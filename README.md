# Prescot — baza opisów produktów

Statyczny panel GitHub Pages z aktywnymi produktami z feedu WAPRO. Katalog i audytowane opisy są ładowane z JSON-u, dlatego 3410 produktów nie powiększa DOM-u ani nie blokuje przeglądarki przy starcie.

## Zasady danych

- eksportowane są wyłącznie oferty z `avail="1"` i `basket="1"`;
- podstawowym identyfikatorem jest EAN;
- przy braku albo powtórzeniu EAN-u używany jest kod produktu i ID oferty;
- stare, ręcznie dopracowane opisy są zachowane w `data/manual-overrides.json`;
- ręczny opis ma zawsze pierwszeństwo przed opisem audytowanym i generatorem awaryjnym;
- pozostałe opisy powstają z nazwy, kodu, EAN-u, kategorii, parametrów i tekstu źródłowego, bez dopisywania niepotwierdzonych danych technicznych;
- konflikty źródeł są rozstrzygane jawnie w `data/source-resolutions.json` i zawierają adresy stron użytych do weryfikacji;
- opis jest dostępny w wariantach Shoper, WAPRO/MAG, TIM i Allegro.

## Aktualizacja katalogu

```bash
python3 scripts/sync_cloud_catalog.py
python3 scripts/build_research_queue.py
python3 scripts/generate_seo_descriptions.py \
  --rules-only \
  --include-manual \
  --include-research-needed \
  --include-source-conflicts \
  --editorial-only \
  --force
npm run validate -- --write
```

Pierwszy skrypt pobiera `https://prescot.wapromag.pl/prescotcloud.xml`, aktualizuje `data/catalog.json` i zachowuje istniejące ręczne nadpisania. Kolejka researchu wskazuje rekordy skąpe lub sprzeczne. Generator buduje warstwę redakcyjną `data/seo-descriptions.json`, a układy HTML dla czterech kanałów są renderowane w przeglądarce przez `description-engine.js`.

Można też wskazać wcześniej pobrany feed:

```bash
python3 scripts/sync_cloud_catalog.py --source /tmp/prescotcloud.xml
```

## Podgląd lokalny

```bash
npm run serve
```

Panel będzie dostępny pod `http://localhost:8080/`. Walidator sprawdza kompletność katalogu i cztery kanały dla każdego produktu: identyfikatory, zakres długości, strukturę sekcji HTML, duplikaty, obce liczby i jednostki, niepotwierdzone twierdzenia oraz sprzeczności z danymi produktu.
