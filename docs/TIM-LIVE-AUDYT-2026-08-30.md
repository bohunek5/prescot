# Audyt live Panelu Dostawcy TIM — 30 sierpnia 2026

## Wniosek

Treści opisów są przygotowane i sprawdzone, ale produkcyjne wgrywanie zostało świadomie zatrzymane. W TIM nadal działa proces `4765` na 98%, a nowym produktom brakuje potwierdzonych danych handlowych i mapowań. Uruchomienie kolejnego importu albo uzupełnienie ceny „na oko” byłoby ryzykowne.

Nie uruchomiono importu, nie zapisano zmian na kartach, nie wysłano pliku i nie wymuszono otwarcia zablokowanej karty.

## Zakres odczytu

Audyt wykonano na zalogowanej sesji Panelu Dostawcy TIM i PIMCORE. Użyto wyłącznie odczytu panelu, danych projektu, bieżącego feedu WAPRO, historycznych plików TIM oraz oficjalnych instrukcji przysłanych przez TIM.

Odczyt głównego folderu dostawcy PIMCORE wykonano w 21 stronach po 250 rekordów:

- 5180 bezpośrednich kart w głównym folderze aktywnego katalogu;
- 0 nieudanych stron odczytu;
- starsze karty znajdujące się w zagnieżdżonych folderach są dodatkowo uzgadniane z wcześniejszym eksportem TIM, dlatego liczby 5180 nie należy traktować jako pełnego licznika wszystkich historycznych kart dostawcy.

## WAPRO i chmura Prescot

Są dwa różne feedy i nie wolno mieszać ich cen:

- `prescotcloud.xml` zasila katalog opisów i zawiera cenę sklepową;
- `prescot.xml` jest źródłem aktywnego schematu TIM `451`, zawiera cenę przeznaczoną dla tego kanału, stan i jednostkę.

Opisy są utrzymywane w tym projekcie i nie są nadpisywane przez żaden z tych plików.

- 5910 ofert w XML;
- 3410 aktywnych produktów;
- 3384 aktywne produkty z EAN i 26 bez EAN;
- 2 powtórzone numery EAN obejmujące 4 produkty;
- 3410 produktów ma przygotowane cztery warianty opisu: WAPRO, TIM, Allegro i Shoper;
- sprawdzono 13 640 opisów;
- aktualny katalog `prescotcloud.xml` był zgodny z kopią używaną do generowania opisów: 0 dodanych, 0 usuniętych i 0 zmienionych produktów podczas kontroli.

Świeżo pobrany `prescot.xml` również miał 5910 ofert i 3410 aktywnych produktów. W docelowym zakresie 2651 produktów 2629 pozycji udało się dopasować po EAN; 2578 miało dodatnią cenę TIM, 51 cenę niedodatnią, 2624 jednostkę, a 5 brak jednostki. Wspólne produkty obu feedów różniły się ceną w 2851 przypadkach, co potwierdza, że cena sklepowa nie może trafiać do TIM.

Między odczytami feedów były około dwie godziny różnicy, dlatego zmiany stanu i pojedyncze różnice asortymentu są tylko sygnałem do ponownego porównania przed importem, a nie dowodem błędu synchronizacji.

## Zakres oferty TIM

Do kontrolowanego kanału TIM należy 2651 aktywnych produktów: Prescot, Prescot LED, KLUŚ, MiLight/MiBoxer, Scharfer oraz uzgodnione profile aluminiowe i PCV. W zakresie jest 911 profili.

Kaja i Light Prestige są wykluczone po producencie, nazwie oraz kategorii. Walidator kolejki 1/10/500 potwierdził 0 takich rekordów.

## Katalog aktywny, bufor i nowe produkty

Po połączeniu manifestu opisów, historycznego eksportu TIM, pełnego odczytu głównego folderu aktywnego i bufora:

- 694 gotowe opisy dotyczą kart rozpoznanych jako aktywne;
- 692 z nich dostały ID PIMCORE przed kontrolą kolizji;
- 688 kart ma jednoznaczne, unikatowe ID PIMCORE i może wejść do bezpiecznej kolejki aktualizacji opisu;
- 4 rekordy wskazujące 2 wspólne ID PIMCORE zostały wykluczone jako niejednoznaczne;
- 2 dalsze aktywne dopasowania nie mają wystarczającego ID do aktualizacji;
- bufor dostawcy zawiera 272 karty, z czego 33 mają gotowy opis;
- 307 produktów z obrazami pozostaje kandydatami na nowe po odjęciu znanych kart aktywnych i bufora.

Liczba 307 jest kolejką kandydatów, a nie zgodą na masowe dodanie. Przed każdym nowym produktem trzeba jeszcze potwierdzić EAN i kod producenta w całym TIM, ponieważ stara lub przemianowana karta może nie zostać wykryta samym porównaniem nazwy.

Bufor zawiera między innymi 168 nazw KLUŚ i 15 MiLight/MiBoxer, ale również po jednym produkcie Light Prestige i Kaja. Te dwa ostatnie pozostają wykluczone. Karta w buforze ze stanem `new`, bez indeksu TIM i z `productAvailableForSale=nie` nie jest jeszcze wdrożonym produktem.

## Pilot aktualizacji opisu istniejącej karty

Pierwsza bezpieczna merytorycznie karta:

- PIMCORE: `2116879`;
- indeks TIM: `0001-00015-94132`;
- EAN: `5903684853625`;
- kod producenta: `LED-Z2P-Ż8`;
- nazwa: „Gniazdo 2-pin czarne przewód 8cm 24awg”;
- stan live podczas kontroli: 852 szt.;
- cena katalogowa netto live: 0,41 zł;
- aktualny `prescot.xml`: stan 852 szt. i cena kanału 0,50 zł;
- karta aktywna, dostępna w sprzedaży, ze zdjęciem i kategorią.

Ten produkt był wcześniej błędnie wybrany jako „nowy”. Odczyt live potwierdził, że już istnieje, więc generator został poprawiony i nie utworzy duplikatu. Różnica 0,41/0,50 zł może być związana z jeszcze niezakończonym procesem `4765`; bez raportu końcowego nie należy zgadywać wyniku. Pilot obejmuje wyłącznie nowe pole opisu i nie powinien zmieniać ceny, stanu, nazwy ani identyfikatorów.

Karta PIMCORE `1343341` była zgłoszona jako otwarta przez konto `info@prescot.com.pl`. Nie użyto opcji wymuszonego otwarcia. Bez jednoznacznej zgody nie należy przerywać żadnej aktywnej sesji edycyjnej.

## Standard opisów TIM

Generator dostosowano do oficjalnego poradnika TIM z wiadomości e-mail. Każdy opis ma trzy warstwy:

1. proste wyjaśnienie, czym jest produkt;
2. zastosowanie i dobór;
3. konkretne parametry w punktach.

Dodatkowo opis zawiera praktyczne wskazówki instalacyjne. Kod producenta jest oddzielony od wewnętrznego indeksu katalogowego Prescot. Usunięto EAN z treści, tabele, style inline i administracyjne dane karty. Wykryto i usunięto także 70 zbyt ogólnych zdań zastępczych; walidator blokuje ich powrót.

## Pilot nowego produktu

Pierwszym rzeczywiście nowym kandydatem jest:

- EAN: `5902280338710`;
- nazwa: „Profil Led MICRO-PLUS 2m anodowany KLUŚ”;
- kod producenta: `A02966A_2`;
- stan źródłowy WAPRO: 2163 szt.;
- cena sklepowa z `prescotcloud.xml`: 21,30 zł;
- cena kanału TIM z `prescot.xml`: 14,00 zł;
- jednostka z `prescot.xml`: `szt.`.

Podłączenie właściwego feedu rozwiązało cenę i jednostkę bez zgadywania. Budowa pliku nadal została prawidłowo zatrzymana z pięcioma problemami:

- brak nazwy producenta dokładnie z listy TIM;
- brak ID producenta TIM;
- brak ID kategorii B24;
- brak gabarytu;
- brak czasu wysyłki;

Do pola ceny TIM trafia 14,00 zł bezpośrednio z `prescot.xml`, a nie 21,30 zł z feedu sklepowego. Historyczne arkusze z 2022 roku i próbka aktywnych kart nie pokazują stałego przelicznika, dlatego jedynym automatycznym źródłem ceny dla tej kolejki jest aktualny feed TIM.

## Schematy i procesy importu

Schemat `645` „PRESCOT - TOP CORE BAZA 2026” ma 2038 błędów na 2038 rekordów, 37 z 95 mapowań kategorii, 4 z 21 producentów i brak mapowania jednostek. Nie może zostać zaakceptowany ani uruchomiony.

Schemat `451` „Dodanie produktów 19.02” wskazuje na szeroki feed `https://prescot.wapromag.pl/prescot.xml`. Panel pokazuje 5797 rekordów z ostatniego przetworzenia, natomiast świeży plik miał już 5910 ofert. Nie nadaje się do pilota 1/10/500, bo nie ogranicza źródła do kontrolowanej partii i jego zapisany licznik jest nieaktualny względem obecnego źródła.

Stan potwierdzony ponownie 30 sierpnia 2026 o 15:15 czasu polskiego:

- proces `4765`, uruchomiony 29 sierpnia o 18:47 na schemacie `451`: `IMPORTING`, 98%, brak daty zakończenia;
- proces `4547`: zakończony 13 sierpnia;
- procesy `1326` i `1317`: `PROCESSING / PARSE 100%` od listopada 2025 roku.

Nie wykonano wymuszonego zakończenia ani ponownego uruchomienia żadnego procesu. Dopóki `4765` nie zostanie wyjaśniony, nie należy uruchamiać kolejnego importu produktów.

## EPREL

- 12 produktów ma dokładne dopasowanie modelu i może dostać zweryfikowany link;
- 8 wymaga dokumentu producenta potwierdzającego wariant;
- 197 ma niezgodny model i link pozostaje zablokowany.

Brak pewnego powiązania EPREL nie jest uzupełniany przez podobieństwo nazwy.

## Co jest przygotowane do następnego etapu

1. Aktualizacja opisu jednej istniejącej, potwierdzonej live karty PIMCORE `2116879`.
2. Po kontroli wyniku — partia 10 opisów.
3. Po drugim wyniku bez błędów — partia do 500 opisów z unikatowymi ID.
4. Osobno: 33 opisy kart z bufora, po sprawdzeniu statusu każdej karty.
5. Osobno: nowe produkty, zaczynając od jednego, dopiero po uzupełnieniu wszystkich pól handlowych i utworzeniu wąskiego schematu.

## Przygotowane pliki

Katalog `exports/tim/pilots` zawiera:

- `active-description-pilot-1.csv`, `active-description-pilot-10.csv`, `active-description-pilot-500.csv`;
- `active-description-pilot.json` z wynikiem dopasowań i listą kolizji;
- `pilot-1-commercial.csv`, `pilot-10-commercial.csv`, `pilot-500-commercial.csv` dla nowych produktów;
- `pilot-content.json` z opisami i zdjęciami kandydatów.

Pliki nowych produktów są materiałem roboczym. Zabezpieczenie odmawia utworzenia XML, dopóki brakuje wymaganych danych handlowych.

Gotowy projekt wiadomości do wsparcia znajduje się w `docs/TIM-WIADOMOSC-DO-WSPARCIA.md`. Nie został wysłany.
