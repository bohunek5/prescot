# Prescot — baza opisów produktów

Statyczny panel GitHub Pages z aktywnymi produktami z feedu WAPRO. Katalog jest ładowany z JSON-u, dlatego 3410 produktów nie powiększa DOM-u ani nie blokuje przeglądarki przy starcie.

## Zasady danych

- eksportowane są wyłącznie oferty z `avail="1"` i `basket="1"`;
- podstawowym identyfikatorem jest EAN;
- przy braku albo powtórzeniu EAN-u używany jest kod produktu i ID oferty;
- stare, ręcznie dopracowane opisy są zachowane w `data/manual-overrides.json`;
- pozostałe opisy powstają z nazwy, kategorii, parametrów i tekstu źródłowego, bez dopisywania niepotwierdzonych danych technicznych;
- opis jest dostępny w wariantach Shoper, WAPRO/MAG, TIM i Allegro.

## Aktualizacja katalogu

```bash
python3 scripts/sync_cloud_catalog.py
npm run validate -- --write
```

Skrypt pobiera `https://prescot.wapromag.pl/prescotcloud.xml`, aktualizuje `data/catalog.json` i zachowuje istniejące ręczne nadpisania. Można też wskazać pobrany plik:

```bash
python3 scripts/sync_cloud_catalog.py --source /tmp/prescotcloud.xml
```

## Podgląd lokalny

```bash
npm run serve
```

Panel będzie dostępny pod `http://localhost:8080/`. Walidator sprawdza wszystkie produkty i cztery kanały, w tym identyfikatory, minimalną długość, strukturę sekcji HTML, dokładne duplikaty oraz podstawowe sprzeczności danych.
