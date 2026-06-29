import hashlib
import re
from bs4 import BeautifulSoup

def get_category(sku):
    if sku.startswith(('WZ-', 'V1', 'T1', 'V2', 'RT1', 'RT6', 'DIM-')) or 'RGB' in sku and len(sku) < 10 or sku.startswith('PR-'):
        return 'sterowniki'
    if sku.startswith(('SC-', 'LRS-', 'RS-', 'SCH-')):
        return 'zasilacze'
    if sku.startswith(('B8547', '18032', 'A01587', 'A02966')):
        return 'profile'
    if sku.startswith(('FC10', 'FC8', 'ZLC', 'M4-')):
        return 'zlaczki'
    return 'tasmy'

blog_html_tasmy = """
<div class="blog-grid" style="font-family:inherit; margin-top: 28px; background:none !important; background-color:transparent !important; color:inherit;">
    <h3 style="font-family:inherit; margin:0 0 16px 0; font-size:22px; font-weight:700;">Baza Wiedzy - Prescot</h3>
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; align-items:stretch;">
        <div style="min-height:190px; padding:18px; border:1px solid currentColor; border-radius:12px; display:flex; flex-direction:column;">
            <strong style="display:block; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak czytać parametry taśmy LED?</strong>
            <small style="display:block; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">moc, lumeny, CRI, napięcie i IP</small>
            <a href="https://www.prescot.com.pl/pl/n/23" style="display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; font-weight:700; font-size:14px;">Czytaj poradnik</a>
        </div>
        <div style="min-height:190px; padding:18px; border:1px solid currentColor; border-radius:12px; display:flex; flex-direction:column;">
            <strong style="display:block; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Montaż taśmy LED na zewnątrz</strong>
            <small style="display:block; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">IP, uszczelnienie i ochrona połączeń</small>
            <a href="https://www.prescot.com.pl/pl/n/16" style="display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; font-weight:700; font-size:14px;">Czytaj poradnik</a>
        </div>
        <div style="min-height:190px; padding:18px; border:1px solid currentColor; border-radius:12px; display:flex; flex-direction:column;">
            <strong style="display:block; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać taśmę LED do mieszkania?</strong>
            <small style="display:block; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">barwa, moc i miejsce montażu</small>
            <a href="https://www.prescot.com.pl/pl/n/12" style="display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; font-weight:700; font-size:14px;">Czytaj poradnik</a>
        </div>
        <div style="min-height:190px; padding:18px; border:1px solid currentColor; border-radius:12px; display:flex; flex-direction:column;">
            <strong style="display:block; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać profil aluminiowy do taśmy LED?</strong>
            <small style="display:block; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">profil, klosz, chłodzenie i estetyka linii światła</small>
            <a href="https://www.prescot.com.pl/pl/n/15" style="display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; font-weight:700; font-size:14px;">Czytaj poradnik</a>
        </div>
    </div>
</div>
"""

blog_html_zasilacze = """
<section style="font-family:inherit; margin:18px 0 0 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<div style="font-family:inherit; margin-bottom:18px; background:none !important; background-color:transparent !important; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">Praktyczne poradniki</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
      Dobierz zasilacz LED bez zgadywania
    </h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.78; font-size:14px; line-height:1.6;">
      Sprawdź krótkie poradniki, które pomogą dobrać moc, typ obudowy, napięcie i stopień ochrony IP do konkretnej instalacji LED.
    </p>
</div>
<div style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit; align-items:stretch;">
<div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Do czego służą zasilacze LED?</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">taśmy LED, moduły LED i sterowniki</small>
<a href="https://www.prescot.com.pl/pl/n/26" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
<font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
</a>
</div>
<div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Zasilacze LED - gdzie użyć którego?</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">desktop, gniazdkowy, siatkowy, slim i hermetyczny</small>
<a href="https://www.prescot.com.pl/pl/n/25" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
<font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
</a>
</div>
<div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać zasilacz LED do taśmy?</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">moc W/m, długość taśmy i zapas mocy</small>
<a href="https://www.prescot.com.pl/pl/n/24" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
<font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
</a>
</div>
<div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Stopnie IP - dlaczego to ważne?</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">IP20, IP33, IP44 i <strong style="font-family:inherit; color:inherit !important;">IP67</strong> w praktyce</small>
<a href="https://www.prescot.com.pl/pl/n/27" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
<font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
</a>
</div>
</div>
</section>
"""

blog_html_sterowniki = """
<section style="font-family:inherit; margin:18px 0 28px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<div style="font-family:inherit; margin-bottom:18px; background:none !important; background-color:transparent !important; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px;  line-height:1.2;">
<font color="#ffffff">Praktyczne poradniki</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
      Baza wiedzy o oświetleniu LED
    </h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.78; font-size:14px; line-height:1.6;">
      Przeczytaj nasze poradniki, aby uniknąć błędów przy doborze komponentów i montażu.
    </p>
</div>
<div style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit; align-items:stretch;">
<div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać zasilacz do taśmy LED?</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">obliczanie mocy i dobór napięcia</small>
<a href="https://www.prescot.com.pl/pl/n/18" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
<font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
</a>
</div>
<div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Rodzaje sterowników LED</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">RF, Wi-Fi i dobór do typu taśmy</small>
<a href="https://www.prescot.com.pl/pl/n/20" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
<font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
</a>
</div>
<div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak łączyć taśmy LED bez lutowania?</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">szybkozłączki, stabilność i profilowanie</small>
<a href="https://www.prescot.com.pl/pl/n/19" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
<font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
</a>
</div>
</div>
</section>
"""

def generate_desc(category, sku, badge_text=""):
    blocks = []
    
    if category == 'sterowniki':
        badge_lower = badge_text.lower()
        sku_upper = sku.upper()
        
        # We need completely customized blocks for each controller model to avoid repetition
        if 'rgbcct' in badge_lower or 'rgbcct' in sku_upper:
            # 5-channel model
            blocks.append((
                "KONTROLA RGB+CCT (5w1)",
                "Najbardziej zaawansowany kontroler 5-kanałowy",
                "Odbiornik dedykowany do obsługi taśm wielokolorowych z regulacją bieli (RGB+CCT). Pozwala na płynne wybieranie dowolnego koloru z palety RGB oraz jednoczesne precyzyjne sterowanie temperaturą barwową światła białego (od 2700K do 6500K) i jego jasnością."
            ))
            blocks.append((
                "FUNKCJE I PARAMETRY",
                "Specyfikacja i możliwości w pigułce",
                "<ul><li style='margin-bottom:8px;'><b>Zasilanie uniwersalne:</b> Obsługa taśm LED 12V oraz 24V DC o łącznym prądzie obciążenia do 15A.</li><li style='margin-bottom:8px;'><b>Automatyczna retransmisja:</b> Zwiększenie zasięgu sterowania poprzez bezprzewodowe przekazywanie sygnału radiowego między odbiornikami (do 30m).</li><li style='margin-bottom:0;'><b>Zabezpieczenie przed zanikiem:</b> Opcjonalny tryb 'Do Not Disturb' zapobiegający niekontrolowanemu włączeniu światła po powrocie zasilania w sieci.</li></ul>"
            ))
            blocks.append((
                "SYSTEM INTEGRACJI",
                "Swoboda łączenia i sterowania strefowego",
                "Sterownik pracuje w standardzie komunikacji radiowej RF 2.4GHz. Można go bez problemu sparować z pilotami strefowymi (zarówno przenośnymi, jak i ściennymi) i przypisać do wybranej grupy urządzeń, tworząc zsynchronizowany system oświetlenia w całym domu."
            ))
        elif 'rgbw' in badge_lower or 'rgbw' in sku_upper:
            # 4-channel model
            blocks.append((
                "STEROWANIE RGB+W (4-kanałowe)",
                "Pełen kolor oraz dedykowany kanał bieli",
                "Kontroler dedykowany do taśm LED RGBW. Umożliwia niezależne miksowanie kolorów z palety RGB oraz włączenie czystego światła białego (ciepłego, neutralnego lub zimnego w zależności od podłączonej taśmy), dając idealny balans między dekoracją a oświetleniem użytkowym."
            ))
            blocks.append((
                "ZALETY INSTALACYJNE",
                "Wysoka sprawność i bezpieczna eksploatacja",
                "<ul><li style='margin-bottom:8px;'><b>Moc pod kontrolą:</b> Prąd wyjściowy 12A/15A pozwala na podpięcie długich linii taśmy bez strat na stabilności sygnału.</li><li style='margin-bottom:8px;'><b>Sygnał bez barier:</b> Wykorzystanie szyfrowanej częstotliwości radiowej 2.4GHz zapewnia doskonały zasięg nawet przez ściany i zabudowy meblowe.</li><li style='margin-bottom:0;'><b>Cicha praca (PWM):</b> Zaawansowane ściemnianie metodą modulacji szerokości impulsów eliminuje efekt brzęczenia i migotania diod.</li></ul>"
            ))
            blocks.append((
                "EKOSYSTEM STREFOWY",
                "Elastyczne przypisywanie urządzeń",
                "Jedno kliknięcie pozwala powiązać kontroler z jednym lub kilkoma pilotami. Umożliwia to wygodną obsługę tego samego obwodu np. za pomocą pilota przy łóżku oraz włącznika dotykowego na ścianie przy wejściu do pokoju."
            ))
        elif 'rgb' in badge_lower or 'rgb' in sku_upper:
            # 3-channel model
            blocks.append((
                "KONTROLA RGB (3-kanałowa)",
                "Efektowne zarządzanie trójkolorową paletą barw",
                "Model stworzony z myślą o klasycznych taśmach LED RGB. Pozwala na płynne przechodzenie między kolorami podstawowymi, regulację nasycenia barw oraz uruchamianie automatycznych programów dynamicznych (przejścia płynne, skokowe, stroboskopowe)."
            ))
            blocks.append((
                "PARAMETRY I WYDAJNOŚĆ",
                "Niezawodne serce instalacji kolorowej",
                "<ul><li style='margin-bottom:8px;'><b>Wygodne zaciski:</b> Solidne terminale śrubowe ułatwiają szybkie i trwałe podłączenie przewodów sekcji R, G, B oraz zasilania.</li><li style='margin-bottom:8px;'><b>Retransmisja RF:</b> Każdy odbiornik działa jako repeater, przekazując sygnał do kolejnego kontrolera w odległości do 30m.</li><li style='margin-bottom:0;'><b>Pamięć ostatniego stanu:</b> Po wyłączeniu zasilania (np. przełącznikiem ściennym) odbiornik zapamiętuje ostatnio ustawiony kolor i jasność.</li></ul>"
            ))
            blocks.append((
                "PILOTY I INTEGRACJA",
                "Zbuduj wygodne sterowanie radiowe",
                "Sterownik współpracuje z pełną gamą nadajników RF 2.4GHz. Pozwala to na stworzenie instalacji wielostrefowej, w której jednym pilotem zmieniasz kolory w całym salonie, kuchni i wnękach sufitowych jednocześnie lub niezależnie."
            ))
        elif 'cct' in badge_lower or 'cct' in sku_upper:
            # 2-channel model
            blocks.append((
                "ZARZĄDZANIE BIELĄ CCT",
                "Regulacja temperatury barwowej światła białego",
                "Dedykowany sterownik do taśm LED o zmiennej barwie białej (CCT / Multiwhite). Umożliwia precyzyjne i płynne przejście od bardzo ciepłego światła (np. 2700K sprzyjającego relaksowi) do rześkiej, chłodnej bieli (np. 6500K pobudzającej do pracy)."
            ))
            blocks.append((
                "FUNKCJONALNOŚĆ I BEZPIECZEŃSTWO",
                "Inteligentne rozwiązania sterujące",
                "<ul><li style='margin-bottom:8px;'><b>Bezskokowa regulacja:</b> Płynne mieszanie barw poprzez dokładne sterowanie dwoma kanałami (ciepłym i zimnym).</li><li style='margin-bottom:8px;'><b>Auto-rettransmisja sygnału:</b> Urządzenia mogą przekazywać sygnał radiowy między sobą (do 30m), co pozwala na budowę ogromnych stref świetlnych.</li><li style='margin-bottom:0;'><b>Tryb 'Do Not Disturb':</b> Inteligentna funkcja, która zapobiega samoistnemu włączeniu świateł po chwilowym zaniku zasilania w nocy.</li></ul>"
            ))
            blocks.append((
                "ŁĄCZENIE W GRUPY",
                "Strefowe zarządzanie oświetleniem w domu",
                "Odbiornik można bezprzewodowo łączyć z wieloma pilotami strefowymi i sterownikami ściennymi. Pozwala to na pełną swobodę w aranżacji wnętrz i dopasowanie systemu sterowania do indywidualnych przyzwyczajeń domowników."
            ))
        else:
            # 1-channel model (MONO)
            blocks.append((
                "PRECYZYJNE ŚCIEMNIANIE MONO",
                "Płynna regulacja jasności taśm jednokolorowych",
                "Klasyczny sterownik ściemniający przeznaczony do jednokolorowych taśm LED (MONO). Oferuje super płynne rozjaśnianie i ściemnianie w zakresie od 1% do 100% bez efektu gwałtownych skoków jasności w najniższych rejestrach."
            ))
            blocks.append((
                "NIEZAWODNOŚĆ I STABILNOŚĆ",
                "Sprawdzona konstrukcja radiowa",
                "<ul><li style='margin-bottom:8px;'><b>Częstotliwość PWM:</b> Wysoka częstotliwość sterowania całkowicie eliminuje migotanie diod na nagraniach wideo i chroni wzrok przed zmęczeniem.</li><li style='margin-bottom:8px;'><b>Duża obciążalność prądowa:</b> Bezpieczna praca z długimi odcinkami taśm dzięki dopuszczalnemu prądowi wyjściowemu 12A/15A.</li><li style='margin-bottom:0;'><b>Repeater sygnału:</b> Bezprzewodowa synchronizacja pozwala na jednorodne ściemnianie wielu odbiorników bez układania dodatkowych kabli.</li></ul>"
            ))
            blocks.append((
                "ZARZĄDZANIE RADIOWE RF",
                "Prosta konfiguracja i elastyczny zasięg",
                "Komunikacja w standardzie RF 2.4GHz gwarantuje stabilną pracę bez zakłóceń na dystansie do 30m. Urządzenie można sparować z wieloma pilotami lub przyciskami bezprzewodowymi, co pozwala na wygodne sterowanie światłem z dowolnego punktu w pokoju."
            ))
        
    elif category == 'zasilacze':
        badge_lower = badge_text.lower()
        sku_lower = sku.lower()
        
        w_match = re.search(r'(\d+)W', badge_text, re.IGNORECASE)
        watt = f" {w_match.group(1)}W" if w_match else ""
        watt_raw = f"{w_match.group(1)}W" if w_match else "mocy"
        
        v_match = re.search(r'(\d+)V', badge_text, re.IGNORECASE)
        if not v_match:
            v_match = re.search(r'-(\d+)$', sku)
        volt = f"{v_match.group(1)}V DC" if v_match else "stabilnym napięciem"
        
        # Use deterministic hash of SKU to vary descriptions (using hashlib to get uniform distribution)
        sku_hash = int(hashlib.md5(sku.encode('utf-8')).hexdigest(), 16)
        var_idx = sku_hash % 3
        
        # 1. Zasilanie / Blok 1
        if var_idx == 0:
            pill_1 = "STABILNE NAPIĘCIE"
            head_1 = f"Dedykowana moc {watt_raw} do systemów LED"
            desc_1 = f"Profesjonalny zasilacz stałonapięciowy o wydajności prądowej dopasowanej do nowoczesnych systemów oświetlenia. Stabilizuje napięcie wyjściowe na stałym poziomie {volt}, co skutecznie chroni diody przed przegrzaniem i gwarantuje równomierny strumień świetlny na całej długości taśmy."
        elif var_idx == 1:
            pill_1 = f"REALNA MOC {watt_raw}"
            head_1 = f"Stabilne zasilanie instalacji {volt}"
            desc_1 = f"Zaawansowana konstrukcja eliminująca wahania napięcia, które są główną przyczyną przyspieszonego zużycia półprzewodników. Zasilacz dostarcza realne {watt_raw} mocy ciągłej, zapobiegając uciążliwemu migotaniu światła nawet przy maksymalnym obciążeniu."
        else:
            pill_1 = "KONTROLA PRĄDU"
            head_1 = f"Sprawność energetyczna i rezerwa {watt_raw}"
            desc_1 = f"Wysokiej klasy układ zasilający dostarczający prąd o stabilnym parametrze {volt}. Optymalnie zestrojona elektronika zapobiega nagłym spadkom napięcia na końcu linii LED, gwarantując identyczną jasność diod w każdym punkcie montażowym."
        blocks.append((pill_1, head_1, desc_1))
        
        # 2. Bezpieczeństwo / Blok 2
        if var_idx == 0:
            pill_2 = "ZABEZPIECZENIA AKTYWNE"
            head_2 = "Kompletna ochrona przed uszkodzeniem"
            desc_2 = "Wbudowane układy zabezpieczające automatycznie odcinają napięcie w przypadku wykrycia zwarcia (SCP) lub przeciążenia (OLP). Zabezpiecza to całą podpiętą linię LED przed uszkodzeniem i minimalizuje ryzyko awarii."
        elif var_idx == 1:
            pill_2 = "BEZPIECZEŃSTWO SYSTEMU"
            head_2 = "Potrójna ochrona prądowa i termiczna"
            desc_2 = "Urządzenie wyposażono w bezpieczniki automatyczne, które natychmiast reagują na stany zwarciowe i przeciążenia. Stały monitoring temperatury wewnętrznej chroni zasilacz przed przegrzaniem przy montażu w zamkniętych przestrzeniach."
        else:
            pill_2 = "OCHRONA INSTALACJI"
            head_2 = "Automatyczne układy zabezpieczające"
            desc_2 = "Praca pod stałym nadzorem elektroniki. W razie wykrycia zwarcia lub przeciążenia, zasilacz przechodzi w tryb impulsowej ochrony (tzw. hiccup mode). Po usunięciu przyczyny problemu urządzenie samoczynnie wraca do standardowego trybu pracy."
        blocks.append((pill_2, head_2, desc_2))
        
        # 3. Przewaga Scharfer / Blok 3
        if var_idx == 0:
            pill_3 = "7 LAT GWARANCJI"
            head_3 = "Szczelna konstrukcja Scharfer IP67"
            desc_3 = "W pełni zalana hermetyczna obudowa zapewnia bezkompromisową odporność na pył i wodę (klasa IP67). Idealny wybór do łazienek, kuchni oraz na zewnątrz. Aluminiowy korpus doskonale odprowadza ciepło bez hałaśliwych wentylatorów, zapewniając bezgłośną pracę. Producent udziela aż 7-letniej gwarancji."
        elif var_idx == 1:
            pill_3 = "KLASA PROJEKTOWA 7Y"
            head_3 = "Cicha praca i aluminiowa obudowa"
            desc_3 = "Scharfer słynie z doskonałej filtracji tętnień, co eliminuje problem pisków cewek. Metalowa konstrukcja w klasie szczelności IP67 umożliwia montaż w miejscach narażonych na wilgoć. Wyprowadzone fabrycznie przewody ułatwiają i przyspieszają montaż w puszkach instalacyjnych, a 7 lat gwarancji potwierdza najwyższą klasę sprzętu."
        else:
            pill_3 = "MARKA SCHARFER"
            head_3 = "Bezpieczny montaż i pasywne chłodzenie"
            desc_3 = "Solidny, metalowy korpus IP67 działa jak wydajny radiator, odprowadzając ciepło pasywnie i bezgłośnie. Całkowity brak generowanego hałasu podnosi komfort codziennego użytkowania. Fabryczne okablowanie pozwala na sprawny montaż we wnękach sufitowych lub gablotach. Bezpieczeństwo inwestycji potwierdza 7 lat gwarancji."
        blocks.append((pill_3, head_3, desc_3))

    elif category == 'profile':
        blocks.append((
            "PROFIL KLUŚ",
            "Fundament trwałego systemu LED",
            "Profil aluminiowy renomowanej marki KLUŚ to absolutny niezbędnik każdej profesjonalnej instalacji. Pełni kluczową funkcję radiatora – skutecznie odprowadza ciepło z nagrzewających się diod LED. Pamiętaj: bez odpowiedniego aluminiowego profilu, żywotność każdej, nawet najlepszej taśmy ulega drastycznemu skróceniu!"
        ))
        blocks.append((
            "RODZAJE I ZASTOSOWANIE",
            "Profile wpuszczane i nawierzchniowe",
            "W ofercie posiadamy dwa najpopularniejsze warianty profili KLUŚ: wpuszczane oraz nawierzchniowe. Profile wpuszczane wtapiają się we frezowane płyty meblowe czy GK, tworząc zlicowaną linię. Nawierzchniowe przykręca lub przykleja się błyskawicznie pod szafkami czy we wnękach."
        ))
        blocks.append((
            "IDEALNA LINIA ŚWIATŁA",
            "Klosz i rozproszenie (Brak w zestawie)",
            "Profil wymaga zastosowania odpowiedniego klosza (osłony), który jest sprzedawany oddzielnie. Klosze mleczne doskonale rozpraszają światło, niwelując efekt \"kropkowania\" i tworząc gładką linię świetlną. Osłony transparentne oferują z kolei maksymalną przepuszczalność światła. Warto zaznaczyć, że do profili serii MICRO oraz MICRO-NK pasują standardowe klosze wsuwane (np. typu HS, KA), natomiast mleczny LIGER-11 to klosz wciskany, który również z nimi współpracuje."
        ))
        
    elif category == 'zlaczki':
        badge_lower = badge_text.lower()
        
        if '8mm' in badge_lower:
            szerokosc = "8mm (np. popularne taśmy jednokolorowe MONO COB lub SMD)"
        elif '10mm' in badge_lower:
            szerokosc = "10mm (często taśmy CCT, RGB lub wyższe moce MONO)"
        elif '12mm' in badge_lower:
            szerokosc = "12mm (zazwyczaj taśmy RGBW lub wielokolorowe)"
        else:
            szerokosc = "odpowiedniej szerokości"

        if 'kątow' in badge_lower or ' l ' in badge_lower:
            zasada = "Złączka typu L (kątowa) służy do estetycznego i bezpiecznego zakręcania taśmą pod kątem 90 stopni, bez ryzyka przełamania ścieżek miedzianych na laminacie."
            zastosowanie = "Idealna przy załamaniach blatu, w narożnikach sufitów podwieszanych i półek meblowych."
        elif 'trójnik' in badge_lower or ' t ' in badge_lower or ' t' in badge_lower:
            zasada = "Złączka typu T (trójnik) rozgałęzia sygnał i zasilanie w trzech kierunkach. Działa jak rozdzielacz, pozwalając na poprowadzenie światła w dwie strony od jednego punktu."
            zastosowanie = "Świetnie sprawdza się w rozbudowanych instalacjach, gdzie potrzebujemy stworzyć odnogi od głównego ciągu świetlnego."
        elif '9w1' in badge_lower or 'uniwersalna' in badge_lower:
            zasada = "Uniwersalny zestaw 9w1 (wielofunkcyjna złączka) pozwala na łączenie prostych odcinków, wyprowadzenie kabli do zasilacza lub łączenie taśm ze złączką narożną."
            zastosowanie = "Prawdziwy niezbędnik instalatora – jeden komplet rozwiązuje większość typowych problemów łączeniowych na obiekcie, dając ogromną swobodę."
        else:
            zasada = "Standardowa złączka służy do szybkiego łączenia dwóch odciętych kawałków taśmy w jedną dłuższą linię lub do bezlutowego podpięcia przewodów zasilających."
            zastosowanie = "Podstawowy element instalacyjny, pozwalający na przedłużanie taśmy bez konieczności kłopotliwego lutowania."

        blocks.append((
            "ZASADA DZIAŁANIA",
            "Szybki i pewny styk bez lutowania",
            f"{zasada} Kluczem działania złączek zaciskowych typu klips są ostre, metalowe piny wewnątrz, które mocno dociskają (lub przebijają) miedziane punkty stykowe taśmy, gwarantując ciągłość obwodu."
        ))
        blocks.append((
            "KOMPATYBILNOŚĆ",
            f"Dopasowana do taśm {szerokosc.split(' ')[0]}",
            f"Prezentowany model został zaprojektowany z myślą o taśmach o szerokości laminatu {szerokosc}. Solidny zacisk poliwęglanowej obudowy chroni przed przypadkowym wysunięciem się taśmy podczas pracy."
        ))
        blocks.append((
            "PRAKTYCZNE ZASTOSOWANIE",
            "Zwiększona wygoda instalatora",
            f"{zastosowanie} Wykorzystanie złączek eliminuje konieczność trudnego lutowania bezpośrednio na drabinie, co przyspiesza pracę i ułatwia szybkie przeróbki."
        ))
    else:
        return None, None
        
    html = ""
    text_val = ""
    for b in blocks:
        pill, h, p = b
        html += f"""
<section style="font-family: inherit; margin: 0 0 18px 0; padding: 22px 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
<span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;"> <span style="color: #ffffff;">{pill}</span> </span>
<h3 style="font-family: inherit; margin: 0 0 8px 0; background: none !important; background-color: transparent !important; color: inherit !important; font-size: 22px; line-height: 1.3; font-weight: bold;">{h}</h3>
"""
        if p.startswith("<ul>"):
            html += f"{p}\n</section>"
            text_val += f"{pill}\n{h}\n[Funkcje opisane punktowo]\n\n"
        else:
            html += f"<p style=\"font-family: inherit; margin: 0; background: none !important; background-color: transparent !important; color: inherit !important; font-size: 16px; line-height: 1.6; opacity: 0.85;\">{p}</p>\n</section>"
            text_val += f"{pill}\n{h}\n{p}\n\n"

    if category == 'sterowniki':
        html += blog_html_sterowniki
    elif category == 'zasilacze':
        html += blog_html_zasilacze
    else:
        html += blog_html_tasmy
    return html, text_val.strip()

with open('index.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

cards = soup.find_all('div', class_='product-accordion')
updates_count = {'sterowniki': 0, 'zasilacze': 0, 'profile': 0, 'zlaczki': 0, 'tasmy': 0}

for card in cards:
    sku = card.get('data-model')
    if not sku:
        continue
    
    cat = get_category(sku)
    badge_span = card.find('span', class_='product-label-badge')
    badge_text = badge_span.text.strip() if badge_span else sku
    
    for tab in ['wapro', 'tim', 'allegro']:
        model_block = card.find('div', id=f'desc-view-{tab}-{sku}')
        textarea = card.find('textarea', id=f'textarea-{tab}-{sku}')

        if model_block and textarea:
            if cat == 'tasmy':
                existing_html = "".join([str(c) for c in model_block.contents])
                if "Baza Wiedzy - Prescot" not in existing_html:
                    blog_soup = BeautifulSoup(blog_html_tasmy, 'html.parser')
                    model_block.append(blog_soup)
                    updates_count[cat] += 1
            else:
                html, text_val = generate_desc(cat, sku, badge_text)
                if html:
                    spec_table = model_block.find('section', class_='product-parameters-section')
                    spec_html = str(spec_table) if spec_table else ""
                    
                    new_html = html + "\n" + spec_html
                    new_soup = BeautifulSoup(new_html, 'html.parser')
                    
                    model_block.clear()
                    model_block.append(new_soup)
                    
                    textarea.string = text_val
                    updates_count[cat] += 1

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))
    
print(f"Updated items: {updates_count}")
