# Prescot - baza opisów i kontrola kanału TIM

Statyczny panel opisów produktów dla WAPRO ERP, TIM, Allegro i Shopera. Projekt oddziela dane handlowe od treści: feed Mamezi zasila katalog treści, zdjęć i parametrów pomocniczych, a `https://prescot.wapromag.pl/prescot.xml` jest wyłącznym źródłem ceny, stanu oraz jednostki dla kanału TIM. Cena detaliczna z Mamezi nigdy nie jest używana jako cena TIM. Żaden feed nie nadpisuje opisów zapisanych w projekcie.

Aktualny audyt oraz instrukcja pracy:

- [Raport końcowy TIM / Prescot z 31 sierpnia 2026](docs/TIM-LIVE-AUDYT-2026-08-31.md)
- [Audyt TIM z 30 sierpnia 2026](docs/TIM-AUDYT-2026-08-30.md)
- [Audyt live Panelu Dostawcy TIM z 30 sierpnia 2026](docs/TIM-LIVE-AUDYT-2026-08-30.md)
- [Poradnik obsługi oferty TIM](docs/TIM-PORADNIK.md)

## Najważniejsze zabezpieczenia

- kanał TIM ma jawny zakres zapisany w `config/tim-scope.json`;
- Kaja i Light Prestige są wykluczane po producencie, nazwie oraz kategorii;
- brak EAN, powtórzony EAN, niedodatnia cena źródłowa i wadliwy opis zatrzymują produkt;
- stan 0, otwarty research i problem EPREL kierują produkt do weryfikacji;
- karta EPREL jest eksportowana tylko po dokładnym dopasowaniu identyfikatora modelu z oficjalnym PDF-em;
- pliki `tim-content-*.csv` są paczką treści, a nie szablonem MarketTIM;
- strona publiczna jest budowana z allowlisty, więc stare pliki testowe, logi i skrypty nie trafiają do GitHub Pages.

## Dane i opisy

Katalog obejmuje wyłącznie oferty z `avail="1"` i `basket="1"`. Podstawowym identyfikatorem jest EAN; przy braku lub duplikacie używany jest kod produktu i ID oferty.

Opisy są renderowane z warstwy redakcyjnej `data/seo-descriptions.json`. WAPRO otrzymuje prosty HTML, Shoper rozbudowaną kartę, Allegro osobny układ sprzedażowy, a TIM konserwatywną sekcję z definicją produktu, zastosowaniem, parametrami potwierdzonymi w nazwie oraz zasadami doboru i bezpieczeństwa. Opis TIM nie zawiera tabel, stylów inline, EAN-u, wewnętrznego indeksu Prescot ani proceduralnych instrukcji montażowych. Pole „Indeks handlowy” korzysta wyłącznie z indeksu producenta.

## Podstawowe polecenia

```bash
npm run validate
npm run audit:refs
npm run test:scope
npm run export:tim
npm run validate:tim
npm run build:site
```

Pełna kontrola i czysty build:

```bash
npm run check
```

Aktualizacja katalogu treści z chmury Mamezi:

```bash
python3 scripts/sync_cloud_catalog.py \
  --source "$PRESCOT_MAMEZI_FEED_URL"
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

Przed eksportem TIM zbuduj oddzielną migawkę ceny, stanu i jednostki z `prescot.xml`:

```bash
python3 scripts/sync_cloud_catalog.py \
  --source 'https://prescot.wapromag.pl/prescot.xml' \
  --legacy /dev/null \
  --existing-overrides data/manual-overrides.json \
  --output-dir /tmp/prescot-tim-commercial
node scripts/build_tim_commercial_snapshot.mjs \
  --input /tmp/prescot-tim-commercial/catalog.json \
  --output data/tim-commercial-catalog.json
```

## Podgląd lokalny

```bash
npm run serve
```

Panel jest dostępny pod `http://localhost:8080/`. Test przeglądarkowy korzysta z portu 8765 i sprawdza cztery kanały, wyszukiwanie po EAN, wykluczenie Kaja w TIM, status produktu, bufor edycji oraz błędy konsoli.

## Automatyzacja

Workflow Pages waliduje katalog, buduje wyłącznie katalog `dist` i dopiero wtedy publikuje stronę. Osobny codzienny audyt pobiera feed WAPRO do katalogu tymczasowego i zgłasza różnice; nie zmienia danych w repozytorium ani nie wysyła niczego do TIM.
