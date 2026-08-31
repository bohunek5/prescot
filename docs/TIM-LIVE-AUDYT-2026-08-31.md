# TIM / Prescot — raport końcowy po pracach live, 31 sierpnia 2026

## Wynik

Oferta została uporządkowana bez zmiany cen, stanów, identyfikatorów, statusów kart ani workflow. Opisy były zapisywane etapami `1 → 10 → reszta`, a po zakończeniu zostały ponownie odczytane z produkcyjnego PIMCORE.

- 2346 unikalnych kart weszło do kontrolowanej kolejki opisów;
- 2345 kart ma opis zgodny z oczekiwanym po niezależnym odczycie live;
- 1 karta, PIMCORE `2116084`, nadal ma poprzedni opis;
- 267 z 272 nazw zostało poprawionych i potwierdzonych live;
- 9 dokładnie dopasowanych modeli ma kompletny zestaw EPREL;
- 93 karty bufora mają opis, a ich statusy `new` lub `new_for_approval` pozostały bez zmian.

W surowej kolejce opisów było 2347 wierszy. Dwa wiersze wskazywały tę samą kartę PIMCORE `9069127`, dlatego poprawny licznik unikalnych kart wynosi 2346.

## Opisy

Wynik odczytu produkcyjnego:

| Grupa | Unikalne karty | Zgodne live | Braki |
|---|---:|---:|---:|
| aktywne, stan dodatni | 1455 | 1455 | 0 |
| aktywne, stan zerowy | 798 | 797 | 1 |
| bufor | 93 | 93 | 0 |
| razem | 2346 | 2345 | 1 |

Opis TIM ma konserwatywny układ: wyjaśnienie produktu, zastosowanie i dobór, potwierdzone parametry oraz ogólne zasady bezpieczeństwa. Nie zawiera EAN-u, wewnętrznego indeksu katalogowego Prescot ani instrukcji krok po kroku. Pole `Indeks handlowy` korzysta z dokładnego kodu producenta, na przykład `LED-Z2P-Ż8`, a nie z indeksu `PRE-...`. Jeżeli źródło podaje jako kod producenta wyłącznie numer EAN, pole jest pomijane, żeby EAN nie trafił do opisu.

Nie dopisywano niepotwierdzonych parametrów. Przy słabym materiale źródłowym opis pozostaje celowo ogólny, zamiast wymyślać moc, wymiary, kompatybilność lub sposób montażu.

Jedyny brak:

- PIMCORE `2116084`, EAN `5903684856824`, indeks handlowy `G-WH1ML`, stan live 0;
- pierwsza kolejka pominęła kartę po chwilowej niezgodności tożsamości/stanu;
- bezpieczna próba ponownego zapisu została odrzucona kodem HTTP 403 przez ochronę CSRF;
- nie obchodzono zabezpieczenia i niczego na karcie nie nadpisano.

## Nazwy

Kolejka objęła 272 aktywne karty:

- 256 nazw osłon z bezsensownym dopiskiem `(bez osłony)`;
- 18 nazw z dopiskiem `wyc` lub `wyc.`;
- dwie karty występowały w obu grupach.

Poprawiono i potwierdzono live 267 nazw. Reguła usuwania `(bez osłony)` działa wyłącznie dla produktów, których nazwa zaczyna się od `Osłona`. Poprawne nazwy profili sprzedawanych bez osłony pozostają bez zmian.

Pięć aktywnych produktów ze stanem dodatnim nadal ma dopisek `wyc`:

- `2398691` — `EH024-050-10-G`;
- `2117292` — `OP-D30-WW60`;
- `2117291` — `OP-D18-WW60`;
- `2167272` — `24E024-100-10-W`;
- `2398694` — `PR024-050-10-B`.

PIMCORE odrzucił zapis nazw, ponieważ dla tych kart wymaga jednocześnie danych energetycznych i dokumentów EPREL. Nie wstawiono podobnego modelu ani fałszywego dokumentu tylko po to, żeby wymusić zapis nazwy.

## Katalog, WAPRO i chmura

Źródła są rozdzielone:

- `prescot.xml` jest wyłącznym źródłem ceny, stanu i jednostki dla TIM;
- feed Mamezi służy do treści, zdjęć i parametrów pomocniczych;
- cena detaliczna z Mamezi nie jest używana jako cena TIM;
- opisy z projektu nie są nadpisywane przez XML.

Migawka WAPRO zawiera 5910 ofert i 3410 aktywnych produktów. Kontrolowany zakres TIM po wykluczeniu Kaja i Light Prestige obejmuje 2651 produktów, w tym 1742 ze stanem dodatnim i 909 ze stanem zerowym. Cały zakres obejmuje Prescot, Prescot LED, KLUŚ, MiLight/MiBoxer, Scharfer oraz uzgodnione profile aluminiowe i PCV.

Porównanie cen miało charakter wyłącznie odczytowy. Dodatnią cenę dało się porównać na 1823 kartach: 433 wartości były zgodne bezpośrednio, a 1390 po uwzględnieniu prezentacji netto/VAT 23%. W tej grupie nie wykryto innej różnicy. Dodatkowo 475 kart miało cenę live TIM równą 0, dla 19 kart bufora pole ceny nie było dostępne, a 29 pozycji nie miało dodatniej ceny źródłowej w `prescot.xml`. Niczego cenowego nie poprawiano ręcznie.

Chmura Mamezi zawierała nadal 3410 aktywnych produktów: 0 dodanych, 0 usuniętych i 3384 rekordy z różnicą względem wcześniejszej migawki. Różnice z chmury nie zmieniają zasady źródła ceny TIM.

## Bufor i brakujące karty

Folder dostawcy zawiera 272 karty bufora. Dokładne dopasowanie po tożsamości produktu pozwoliło uzupełnić opis na 74 kartach `new` i 19 kartach `new_for_approval`. Nie wysłano ich do akceptacji i nie zmieniono statusu.

Dla 72 produktów z zakresu nie znaleziono dokładnej karty w TIM. Z tej grupy 45 ma treść gotową, a 27 wymaga przeglądu. Nowych kart nie utworzono, ponieważ nadal brakuje bezpiecznych mapowań handlowych wymaganych przez TIM, między innymi producenta, kategorii B24, gabarytu i czasu wysyłki.

## EPREL, CE, instrukcje i zdjęcia

- 9 kart ma potwierdzony live komplet: klasa energetyczna, oficjalna etykieta i karta informacyjna produktu;
- 96 pozostałych kart wymaga dokładnej karty informacyjnej właściwego modelu;
- podobne warianty nie zostały podpięte;
- znany zdublowany asset dokładnego dokumentu został usunięty, a prawidłowa relacja pozostała;
- zachowano mapę 11 znanych aktywów CE w PIMCORE;
- lokalny folder TIM zawiera 656 plików PDF, ale masowe podpinanie bez dokładnej mapy model → dokument zostało zatrzymane.

Historyczny arkusz Gemini z 28 sierpnia został zachowany jako snapshot, a nie przedstawiony jako świeży stan live. Obejmuje 5980 kart: 527 kompletnych, 4974 bez karty PDF, 4344 bez CE i 102 bez zdjęcia. Te liczby są punktem wyjścia do dalszego dokładnego mapowania dokumentów.

## Importy

Stan odczytany ponownie 31 sierpnia 2026 o 09:05 CEST:

- proces `4765`, schemat `451`: `Importowanie danych`, 98%, uruchomiony 29 sierpnia o 18:47, nadal bez daty zakończenia;
- procesy `1326` i `1317`: `Przetwarzanie: Wczytywanie`, 100%, nadal bez daty zakończenia;
- schemat `648` „PRESCOT - PILOT 10 CENY 2D 30.08.2026”: oczekuje na akceptację administratora;
- schemat `647`: oczekuje na mapę kategorii użytkownika;
- schemat `646`: błąd pobierania 100%;
- schemat `645`: obecnie oczekuje na akceptację administratora.

Nie uruchomiono nowego importu, nie zaakceptowano żadnego schematu i nie wymuszono zakończenia procesu. Proces `4765` pozostaje główną blokadą dla kolejnego szerokiego importu.

## Pliki końcowe

Pełny arkusz kontrolny jest zapisany w `~/Downloads/TIM_PRESCOT_AUDYT_2026-08-31.xlsx`. Zawiera 11 arkuszy: podsumowanie, katalog 2651 produktów, priorytet 1742 produktów ze stanem dodatnim, opisy live, braki i konflikty, bufor, EPREL, snapshot dokumentów, aktywa CE, poprawki nazw oraz metadane źródeł.

Pliki kolejki i walidatory pozostają w `exports/tim` oraz `scripts`. Publiczna strona `/prescot` nadal pokazuje opisy według platformy, w tym wariant TIM.
