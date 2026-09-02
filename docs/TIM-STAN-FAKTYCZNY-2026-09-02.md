# TIM — stan faktyczny 2 września 2026, godz. 21:40

Raport opiera się na ponownym odczycie zalogowanego Panelu Dostawcy TIM oraz pełnym audycie kart PIMCORE. Nie zakłada, że zapisany plik lub wykonany wcześniej skrypt oznacza zmianę widoczną w TIM.

## Ocena widoczna obecnie w Panelu Dostawcy

- ocena ogólna: **3/5**;
- zarządzanie produktem: **3/5**;
- realizacja zamówień: **5/5**;
- potwierdzenia terminów realizacji dostaw: **1/5**;
- warunki handlowe: **5/5**.

Składowe „Zarządzania produktem”:

- certyfikaty: **1/5** — TIM wymaga ponad 92% do oceny 5;
- oferta TIM względem cennika: **5/5** — próg ponad 90% jest spełniony;
- karty katalogowe: **1/5** — TIM wymaga ponad 92% do oceny 5;
- dostępność magazynowa: **2/5** — TIM wymaga ponad 90% do oceny 5.

## Oferta Prescot w PIMCORE

- aktywne i opublikowane karty: **2008**;
- aktywne, opublikowane i ze stanem dodatnim: **980**;
- aktywne ze stanem dodatnim i opisem: **980/980**;
- aktywne ze stanem dodatnim i zdjęciem: **980/980**;
- aktywne ze stanem dodatnim i EAN-em: **980/980**;
- aktywne karty ze stanem 0 i bez opisu: **117**;
- karty katalogowe przy stanie dodatnim: **806/980**;
- CE przy stanie dodatnim: **784/980** po uwzględnieniu ośmiu końcowo zweryfikowanych zapisów;
- instrukcje przy stanie dodatnim: **10/980**.

Jeżeli TIM liczy wszystkie 2008 aktywnych i opublikowanych kart, bieżące udziały wynoszą około 58,6% dla kart katalogowych i 72,9% dla CE. To wyjaśnia ocenę 1 mimo znacznego uzupełnienia dokumentów przy produktach ze stanem dodatnim.

## Jakość opisów

- wszystkie 980 produktów ze stanem dodatnim ma wypełnione pole opisu;
- 209 taśm ma nowy, zaakceptowany naturalny układ;
- 758 pozycji nadal ma wcześniejszy opis szablonowy/generatywny;
- podany wcześniej adres na porcie 881 nie odpowiada obecnie na komputerze;
- działający port 8081 renderuje wariant TIM, ale jego bieżący generator dla części produktów nadal daje zbyt ogólną treść. Nie wolno kopiować go masowo bez zamrożenia i kontroli wersji.

Wśród 117 pustych kart ze stanem 0 nie ma ani jednej pozycji, którą obecny katalog pozwala bezpiecznie dopasować jednocześnie po EAN-ie i indeksie handlowym. Są tam stare produkty obcych marek, stare karty bez EAN-u oraz duplikaty nowych kart. Masowe wstawienie opisów tylko po podobnej nazwie grozi opisaniem niewłaściwego wariantu.

## Dokumenty wykonane i potwierdzone

- 403 nowe relacje kart katalogowych zapisane dzisiaj: 246 profili i 157 akcesoriów;
- 806/980 produktów z dodatnim stanem ma obecnie kartę katalogową;
- 784/980 produktów z dodatnim stanem ma CE po końcowych zapisach;
- ceny, stany, nazwy, EAN-y i workflow nie były zmieniane przy zapisach dokumentów i opisów;
- problem z ceną zamówienia inną niż cena ofertowa został zgłoszony przez TIM do działu technicznego.

## Co trzeba zrobić, aby dojść do 5

1. Ustalić właściwy mianownik TIM: wszystkie karty widoczne czy tylko aktualnie oferowane. Dane wskazują, że TIM liczy również dużą część kart ze stanem 0.
2. Podjąć kontrolowaną decyzję dla kart ze stanem 0: wycofać stare duplikaty i obce marki albo pozostawić je i uzupełnić dokumentację. Sam opis nie poprawi wskaźnika certyfikatów, kart ani dostępności.
3. Doprowadzić CE oraz karty katalogowe do ponad 92% grupy liczonej przez TIM, z buforem do 94–95%.
4. Doprowadzić udział oferty ze stanem i wysyłką 24 h do ponad 90%.
5. W potwierdzeniach terminów dostaw osiągnąć ponad 90% potwierdzonych terminów i ponad 95% zgodności z terminem.

## Plan dalszej pracy

- audyt ETIM wszystkich 980 pozycji ze stanem dodatnim i wybór kart mających mniej niż cztery uzupełnione cechy;
- pilot jednej karty: uzupełnienie wyłącznie czterech parametrów potwierdzonych nazwą i katalogiem, następnie ponowny odczyt;
- partia 10 po pozytywnym pilocie, potem kolejne jednoznaczne pozycje;
- rozdzielenie 117 pustych opisów na: duplikaty do wycofania, obce marki do wycofania, produkty Prescot/KLUŚ do bezpiecznego uzupełnienia;
- dalsze uzupełnianie kart i CE, liczone względem faktycznego mianownika TIM;
- końcowy ponowny odczyt panelu, PIMCORE i raport różnic.

Arkusz kontrolny: `TIM_STAN_FAKTYCZNY_2026-09-02_2140.xlsx` w folderze Pobrane.
