# Poradnik obsługi oferty Prescot w TIM

## 1. Zasada nadrzędna

Feed Mamezi zasila katalog treści, zdjęć i parametrów pomocniczych. `https://prescot.wapromag.pl/prescot.xml` zasila aktywny schemat TIM i jest wyłącznym źródłem ceny kanału TIM, stanu oraz jednostki. Cena detaliczna Mamezi nie może trafić do TIM. Opisy są utrzymywane w tym projekcie. Żaden plik z katalogu `exports/tim` nie jest automatycznie wysyłany do TIM.

Status `ready` znaczy „opis przeszedł kontrolę treści”. Nie znaczy „produkt jest gotowy do wgrania w MarketTIM”. Oficjalny import wymaga aktualnego szablonu i pól, których nie ma w feedzie WAPRO.

## 2. Odświeżenie katalogu

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

Po odświeżeniu uruchom pełny zestaw kontroli:

```bash
npm run check
```

Jeżeli pobrano nowy eksport kart, raport procesu lub plik źródłowy TIM, odtwórz także audyt wejść:

```bash
node scripts/audit_tim_inputs.mjs \
  --panel-export /sciezka/do/exportu-kart.csv \
  --import-report /sciezka/do/raportu-importu.csv \
  --master-xml /sciezka/do/pliku-zrodlowego.xml
```

Wynik trafia domyślnie do `exports/tim/source-audit`. Raport nie zmienia danych w TIM.

## 3. Zakres TIM

Plik `config/tim-scope.json` jest jedynym miejscem definiującym zakres. Obecna reguła dopuszcza Prescot, Prescot LED, KLUŚ, Milight/MiBoxer, Scharfer i całą kategorię profili LED. Kaja oraz Light Prestige mają pierwszeństwo jako reguła wykluczająca.

Nie zmieniaj zakresu tylko dlatego, że producent jest błędnie zapisany w XML. Przykładowy profil PCV opisany jako MeanWell pozostaje w zakresie po kategorii, ale wymaga korekty danych producenta.

## 4. Statusy produktu

- `ready` - opis nie ma blokad ani ostrzeżeń i może być przeniesiony do aktualnego szablonu TIM;
- `review` - opis istnieje, ale produkt ma otwarty research, stan 0, pusty opis źródłowy albo problem EPREL;
- `blocked` - produkt ma brak lub duplikat EAN, cenę źródłową 0 albo wadliwy opis;
- `out_of_scope` - produkt nie należy do oferty TIM.

Powody są widoczne na każdej karcie w kanale TIM oraz w `data/tim-status.json`.

## 5. Edycje opisów i lokalny bufor

1. Otwórz kanał TIM i produkt.
2. Sprawdź blokady w sekcji „Kontrola TIM”.
3. Kliknij „Edytuj opis”.
4. Zapis przejdzie kontrolę struktury TIM.
5. Kliknij „Eksportuj edycje”, aby pobrać bufor JSON.
6. Na innym komputerze wybierz „Importuj bufor”.

Bufor jest zapisany w `localStorage` przeglądarki. Wyczyszczenie danych witryny usuwa go, dlatego po każdej większej sesji trzeba wykonać eksport JSON.

Aby zastosować bufor podczas budowania paczki treści, najpierw odśwież `data/tim-commercial-catalog.json` z `prescot.xml`, a potem uruchom:

```bash
node scripts/export_tim_catalog.mjs \
  --commercial-catalog data/tim-commercial-catalog.json \
  --edits /sciezka/do/prescot-opisy-YYYY-MM-DD.json
node scripts/validate_tim_export.mjs
```

## 6. Paczka treści TIM

```bash
npm run export:tim
npm run validate:tim
```

Powstaną:

- `tim-content-ready.csv` - opisy gotowe do mapowania;
- `tim-content-review.csv` - kolejka decyzji;
- `tim-content-blocked.csv` - rekordy zatrzymane;
- `tim-content-all.csv` - cały zakres;
- `tim-manifest.json` - pełny ślad decyzji;
- `TIM-RAPORT.md` - podsumowanie.

Pliki mają kolumny ceny, stanu i jednostki z aktualnej migawki `prescot.xml`. Eksport nie uruchamia importu i pozostaje paczką kontrolną, dopóki nie ma pełnego mapowania MarketTIM.

Opis TIM musi zawierać: proste wyjaśnienie produktu, zastosowanie i dobór, potwierdzone parametry w punktach oraz zasady doboru i bezpieczeństwa. Walidator odrzuca tabele, style inline, EAN, wewnętrzny indeks katalogowy, znacznik `wyc.`, brak indeksu handlowego producenta i proceduralne instrukcje montażowe.

## 7. Trzy osobne kolejki wdrożeniowe

Nie mieszaj aktualizacji istniejących kart, bufora i nowych produktów w jednym pliku.

1. **Aktywne karty** — wymagają jednoznacznego ID PIMCORE; zmieniany jest tylko opis.
2. **Bufor TIM** — każdą kartę trzeba sprawdzić pod kątem statusu `new`, zwrotu administratora i braków.
3. **Nowe produkty** — wymagają pełnej kontroli EAN, kodu producenta, ceny netto TIM, producenta, jednostki, B24, gabarytu i czasu wysyłki.

Kolejki 1/10/500 buduje się dopiero z pełnego odczytu głównego folderu aktywnego i bufora:

```bash
node scripts/prepare_tim_pilot_queue.mjs \
  --buffer-audit /sciezka/do/pelnego-odczytu-bufora.json \
  --active-audit /sciezka/do/pelnego-odczytu-katalogu.json \
  --active-object-audit /sciezka/do-potwierdzonej-karty-pilota.json \
  --tim-feed /sciezka/do/aktualnego-prescot.xml
```

Generator wyklucza Kaja i Light Prestige po wcześniejszym manifeście zakresu, odrzuca znane aktywne karty z kolejki nowych produktów oraz usuwa z partii aktualizacji wszystkie kolizje ID PIMCORE. Dopasowanie samej nazwy nie jest wystarczające do masowego dodania nowych produktów.

Cena, stan i jednostka dla nowego produktu mogą zostać uzupełnione automatycznie wyłącznie z aktualnego `prescot.xml`. Cena detaliczna z Mamezi nie może być kopiowana do ceny TIM.

Nigdy nie używaj opcji wymuszonego otwarcia karty, jeśli panel zgłasza aktywną edycję, bez wyraźnej zgody właściciela sesji.

## 8. Przygotowanie oficjalnego importu produktów

Zawsze pobierz aktualny szablon MarketTIM z panelu. Stare arkusze z 2022 roku służą tylko jako dokumentacja procesu.

Przed zapisaniem CSV trzeba uzupełnić i sprawdzić:

- ID PIMCORE dla aktualizowanego produktu albo identyfikator dostawcy dla nowego;
- producenta dokładnie z listy TIM;
- indeks producenta;
- unikatowy 13-cyfrowy EAN albo oficjalną ścieżkę „nie mam EAN”;
- jednostkę zgodną z fakturą;
- cenę sprzedaży netto dla TIM;
- VAT, walutę i ewentualny PKWiU;
- nazwę do 128 znaków, z podstawowymi parametrami i kodem producenta na końcu;
- gabaryt i czas wysyłki;
- kategorię produktu i trzy poziomy B24;
- opis z `tim-content-ready.csv`.

Szablon produktu nie importuje multimediów ani ETIM. Po zapisaniu CSV UTF-8 trzeba uruchomić import MarketTIM, a następnie pobrać raport z zakładki Processes. Nie przechodź dalej, jeśli raport ma błędy mapowania.

## 9. Multimedia

Zdjęcia i dokumenty są osobnym importem. Według instrukcji TIM:

- zdjęcia mają format JPG, minimum 300 x 300 px, białe tło i brak znaków wodnych;
- certyfikaty, deklaracje zgodności, instrukcje, rysunki techniczne i karty katalogowe mają format PDF;
- paczka ZIP zawiera multimedia i szablon importu multimediów;
- produkt wskazuje się indeksem TIM albo ID PIMCORE;
- dozwolone akcje to dodanie lub usunięcie pliku.

Po imporcie ponownie pobierz raport procesu. Brak pliku w master XML nie dowodzi, że pliku nie ma już na karcie TIM, dlatego nie usuwaj multimediów na podstawie samego XML.

## 10. ETIM i EPREL

ETIM uzupełniaj tylko na podstawie danych technicznych produktu. Brak danych zostaw pusty; nie zgaduj wartości.

Link EPREL wolno przenieść tylko, gdy status w manifeście wynosi `verified_exact_model`. Status `review_variant_model` wymaga dokumentu producenta, a `blocked_model_mismatch` oznacza zakaz użycia tego powiązania.

Odświeżenie kandydatów EPREL z pliku źródłowego wygląda tak:

```bash
node scripts/import_eprel_candidates.mjs --master-xml /sciezka/do/pliku.xml
env -u NODE_TLS_REJECT_UNAUTHORIZED node scripts/download_eprel_candidates.mjs
PYTHONPYCACHEPREFIX=/tmp/prescot-pycache python3 scripts/verify_eprel_models.py
```

## 11. Bufor TIM/PIMCORE

Nowy produkt po wysłaniu do akceptacji ma stan „do zatwierdzenia” i pozostaje w buforze TIM. Po akceptacji dostaje indeks TIM i przechodzi do Katalogu Głównego jako aktywny. Produkt zwrócony przez administratora pozostaje w buforze z komentarzem.

Istniejącej karty nie należy nadpisywać jak nowego produktu. Zmiana opisu, ceny, zdjęcia lub danych przechodzi przez wniosek o zmianę. Wycofanie również jest wnioskiem; wcześniej można ustawić stan 0, aby produkt nie był sprzedawany.

## 12. Kontrola przed uruchomieniem importu

Nie uruchamiaj importu, dopóki wszystkie odpowiedzi nie brzmią „tak”:

1. Czy plik zawiera tylko Prescot, KLUŚ, Milight/MiBoxer, Scharfer i uzgodnione profile?
2. Czy Kaja oraz Light Prestige mają 0 rekordów?
3. Czy EAN-y są prawidłowe i unikatowe?
4. Czy cena jest ceną netto dla TIM, a nie ceną sklepową z WAPRO?
5. Czy producent, jednostka i B24 korzystają z aktualnych list TIM?
6. Czy nazwy spełniają limit 128 znaków?
7. Czy EPREL ma dokładny model albo został świadomie pominięty?
8. Czy multimedia i ETIM mają osobne, poprawne paczki?
9. Czy walidator lokalny i raport poprzedniego testowego importu mają 0 błędów?
10. Czy zapisano kopię pliku i manifestu przed uruchomieniem?

Pierwszy import po naprawie powinien być małym pilotem, nie pełną paczką. Po jego akceptacji można zwiększać partię, zachowując raport każdego procesu.
