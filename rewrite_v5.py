import re
import pandas as pd

blog_html = """<section style="font-family:inherit; margin:18px 0 28px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <div style="font-family:inherit; margin-bottom:18px; background:none !important; background-color:transparent !important; color:inherit;">
    <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px;  line-height:1.2;">
    <font color="#ffffff">Praktyczne poradniki</font>
  </span>

    <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
      Dobierz komponenty bez zgadywania
    </h3>

    <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.78; font-size:14px; line-height:1.6;">
      Poradniki prowadzą przez parametry, zasilanie, profile aluminiowe i montaż, czyli decyzje, które naprawdę wpływają na efekt końcowy.
    </p>
  </div>

  <div style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit; align-items:stretch;">
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak czytać parametry taśmy LED?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">moc, lumeny, CRI, napięcie i IP</small>
      <a href="https://www.prescot.com.pl/pl/n/23" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Montaż taśmy LED na zewnątrz</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">IP, uszczelnienie i ochrona połączeń</small>
      <a href="https://www.prescot.com.pl/pl/n/16" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać taśmę LED do mieszkania?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">barwa, moc i miejsce montażu</small>
      <a href="https://www.prescot.com.pl/pl/n/12" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać profil aluminiowy do taśmy LED?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">profil, klosz, chłodzenie i estetyka linii światła</small>
      <a href="https://www.prescot.com.pl/pl/n/15" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
  </div>
</section>"""

blog_zasilacze_html = """<section style="font-family:inherit; margin:18px 0 0 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
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
      <a href="https://www.prescot.com.pl/pl/n/25" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
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
</section>"""

def get_sterownik_html(sku, tab):
    typ = "Jednokolorowych (MONO)" if "MONO" in sku else ("CCT (Dual White)" if "CCT" in sku and "RGB" not in sku else ("RGB" if "RGB-" in sku else ("RGBW" if "RGBW" in sku else "RGBCCT")))
    naglowek_glowny = f"Pilot, uchwyt magnetyczny i odbiornik {sku}"
    
    if tab == 'allegro':
        if "CCT" in sku and "RGB" not in sku:
            opis_ogolny = f"Stwórz idealny nastrój w swoim domu! Zaawansowany zestaw do taśm LED {typ}. Pozwala na płynne przejścia od ciepłego, relaksującego światła do chłodnego, idealnego do pracy. Niezawodny zasięg 2.4GHz RF do 30m sprawia, że pilot działa przez ściany i meble."
        elif "RGB-" in sku:
            opis_ogolny = f"Odmień swoje wnętrze! Zaawansowany zestaw do taśm LED {typ}. Wybieraj spośród 16 milionów kolorów i dopasuj oświetlenie do nastroju. Niezawodny zasięg 2.4GHz RF do 30m sprawia, że pilot działa przez ściany i meble."
        elif "RGBW" in sku:
            opis_ogolny = f"Kompletne rozwiązanie do domu! Zaawansowany zestaw do taśm LED {typ}. Połączenie wielokolorowego oświetlenia z czystym, białym światłem do codziennego użytku. Niezawodny zasięg 2.4GHz RF do 30m sprawia, że pilot działa przez ściany i meble."
        elif "RGBCCT" in sku:
            opis_ogolny = f"Pełna kontrola w Twoich rękach! Najbardziej zaawansowany zestaw do taśm LED {typ}. Wszystko w jednym: potężna paleta barw i regulacja bieli. Niezawodny zasięg 2.4GHz RF do 30m sprawia, że pilot działa przez ściany i meble."
        else: # MONO
            opis_ogolny = f"Niezawodny zestaw (ściemniacz) dedykowany do taśm LED {typ}. Idealny do salonu, kuchni czy sypialni. Precyzyjne sterowanie jasnością od 1% do 100%. Niezawodny zasięg 2.4GHz RF do 30m sprawia, że pilot działa przez ściany i meble."

        opis_ogolny += " Łatwy montaż – bez trudu schowasz sprzęt, np. za szafką lub w suficie podwieszanym."
        tytul_funkcji = "Intuicyjna obsługa i świetne efekty"
        funkcje = f"""
    <li style="margin-bottom:8px;"><b>Duża moc:</b> Obsłuży większość domowych instalacji (max 12A).</li>
    <li style="margin-bottom:8px;"><b>Duży zasięg (Auto-retransmisja):</b> Steruj oświetleniem nawet z innego pokoju (do 30m zasięgu).</li>
    <li style="margin-bottom:8px;"><b>Idealna synchronizacja:</b> Taśmy zmieniają kolory idealnie równo.</li>
    <li style="margin-bottom:8px;"><b>Ochrona oczu:</b> Brak efekty migotania światła, idealne do wypoczynku i przed kamerą telefonu.</li>
    <li style="margin-bottom:0;"><b>Tryb "Nie przeszkadzać":</b> Zabezpiecza przed niespodziewanym włączeniem oświetlenia w nocy po powrocie prądu w sieci.</li>"""

    elif tab == 'tim':
        opis_ogolny = f"Profesjonalny zestaw sterujący z pilotem i uchwytem ściennym magnetycznym. Przeznaczony do taśm LED {typ}. Stabilna komunikacja radiowa 2.4GHz RF zapewnia bezawaryjny zasięg do 30m w trudnych warunkach zabudowy, eliminując wymóg optycznej widoczności."
        opis_ogolny += " Moduł wykonawczy zaprojektowano z myślą o ergonomii montażu w rozdzielnicach czy sufitach podwieszanych."
        tytul_funkcji = "Specyfikacja techniczna i parametry dla instalatorów"
        funkcje = f"""
    <li style="margin-bottom:8px;"><b>Parametry prądowe:</b> Obciążalność max 12A (6A/kanał), optymalny do instalacji stałonapięciowych DC 5-24V.</li>
    <li style="margin-bottom:8px;"><b>Kaskadowa retransmisja (Mesh):</b> Wbudowany moduł przekazywania sygnału pozwala na budowę rozległych instalacji wielostrefowych (skok zasięgu co 30m).</li>
    <li style="margin-bottom:8px;"><b>Sprzętowa synchronizacja:</b> Brak latencji i perfekcyjne wyrównanie czasowe urządzeń wykonawczych.</li>
    <li style="margin-bottom:8px;"><b>Wysoka częstotliwość PWM:</b> Płynne ściemnianie w standardzie flicker-free, zgodne z normami dla przestrzeni biurowych.</li>
    <li style="margin-bottom:0;"><b>Stan pamięci (Do Not Disturb):</b> Zaawansowane zarządzanie zachowaniem po powrocie zasilania – ochrona przed przypadkowym wysterowaniem obwodu (DND).</li>"""

    else:
        if "CCT" in sku and "RGB" not in sku:
            opis_ogolny = f"Profesjonalny system zarządzania temperaturą barwową do taśm LED {typ}. Zaawansowana elektronika pozwala na precyzyjne przejścia między tonacjami (od chłodnej bieli do ciepłej) z zachowaniem optymalnego odwzorowania. Wykorzystanie protokołu bezprzewodowego 2.4GHz RF eliminuje opóźnienia, gwarantując zasięg do 30 metrów nawet w gęstej architekturze wnętrz."
        elif "RGB-" in sku:
            opis_ogolny = f"Wielostrefowy, profesjonalny system sterowania taśmami LED {typ}. Umożliwia precyzyjne zarządzanie nasyceniem z pełnego spektrum 16 milionów barw. Zastosowanie wydajnego protokołu komunikacji bezprzewodowej 2.4GHz RF gwarantuje natychmiastową reakcję i stabilny sygnał na dystansie do 30 metrów, eliminując wymóg optycznego celowania pilotem."
        elif "RGBW" in sku:
            opis_ogolny = f"Zaawansowany moduł sterujący dla taśm LED {typ}. Bezkompromisowe połączenie dynamicznego oświetlenia RGB z absolutnie czystym kanałem światła białego. Profesjonalny sprzęt oparty o komunikację 2.4GHz RF utrzymuje stabilne i pozbawione zakłóceń łącze o zasięgu do 30 metrów we wszystkich współczesnych obiektach architektonicznych."
        elif "RGBCCT" in sku:
            opis_ogolny = f"Najwyższej klasy, zintegrowany system 5-kanałowy do taśm LED {typ}. Zapewnia totalną kontrolę nad instalacją świetlną – od wielokolorowych aranżacji przestrzeni, poprzez precyzyjną kalibrację czystej bieli CCT, aż po bezstopniowe ściemnianie. Standard pracy 2.4GHz RF zapewnia penetrację przeszkód i zasięg do 30 metrów w warunkach docelowych."
        else: # MONO
            opis_ogolny = f"Profesjonalny zestaw sterujący zaprojektowany z myślą o zaawansowanych instalacjach na taśmach LED {typ}. Architektura oparta na komunikacji 2.4GHz RF gwarantuje niezawodną pracę systemu bez latencji. Zaawansowane algorytmy regulacji mocy modułu wykonawczego oferują precyzyjne i w pełni bezstopniowe sterowanie strumieniem świetlnym od 1% do 100%."

        opis_ogolny += " Kompaktowa forma odbiornika pozwala na pełną integrację w architekturze wnętrza. Zminimalizowane gabaryty umożliwiają błyskawiczny montaż bezpośrednio w profilach konstrukcyjnych, przestrzeniach sufitów podwieszanych i rozdzielnicach elektrycznych."
        tytul_funkcji = "Wygoda, kontrola i funkcje"
        funkcje = f"""
    <li style="margin-bottom:8px;"><b>Wysoka wydajność prądowa:</b> Moduł obsługuje obciążenia rzędu 12A (max 6A na kanał), stabilizując parametry zasilania w instalacjach DC 5-24V.</li>
    <li style="margin-bottom:8px;"><b>Aktywna retransmisja sygnału:</b> Urządzenie kaskadowo transmituje protokół sterujący do kolejnych węzłów, pozwalając na budowanie nieskończenie długich stref oświetleniowych.</li>
    <li style="margin-bottom:8px;"><b>Sprzętowa synchronizacja:</b> Rozległa sieć urządzeń wykonawczych działa w pełnej koordynacji, eliminując desynchronizację w płynnych przejściach tonalnych.</li>
    <li style="margin-bottom:8px;"><b>Adaptacyjna częstotliwość PWM:</b> Technologia redukcji stroboskopowej (flicker-free) gwarantująca najwyższy komfort wizualny, niezależnie od zastosowanego sprzętu wideo.</li>
    <li style="margin-bottom:0;"><b>Zarządzanie zasilaniem (DND):</b> Tryb inteligentnej pamięci zapobiega samoistnemu wzbudzeniu obwodu po nagłych spadkach lub utracie zasilania w obiekcie.</li>"""

    return f"""<section style="font-family:inherit; margin:28px 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Dedykowany do taśm {typ}</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    {naglowek_glowny}
  </h3>

  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    {opis_ogolny}
  </p>
</section>

<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">KONTROLA I FUNKCJE</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 14px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    {tytul_funkcji}
  </h3>

  <ul style="font-family:inherit; margin:0; padding-left:20px; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    {funkcje}
  </ul>
</section>
{blog_html}"""

def get_zlaczka_html(sku, tab):
    szerokosc = "8mm" if "FC8" in sku else "10mm"
    typ = "CCT" if "CCT" in sku else ("RGBW" if "RGBW" in sku else ("RGB" if "RGB" in sku else "MONO"))
    
    kompatybilnosc = "Uniwersalne zastosowanie: doskonale łączy zarówno taśmy COB (linia ciągła), jak i tradycyjne SMD."
    if "-COB-" in sku: kompatybilnosc = "Zaprojektowana specjalnie pod bezpunktowe taśmy COB."
    if "-SMD-" in sku: kompatybilnosc = "Zaprojektowana dla standardowych taśm SMD."
    
    warianty = "Wszechstronna budowa 9w1: łączy taśmę z taśmą, taśmę z przewodem, pozwala na łączenie narożne (L), boczne (T) oraz krzyżowe (X)." if "9IN1" in sku else "Szybkie, stabilne połączenie zaciskowe na piny bez konieczności czasochłonnego lutowania."

    if tab == 'allegro':
        opis_glowny = f"{kompatybilnosc} Zapomnij o lutownicy! Złączka zapewnia błyskawiczny montaż dzięki systemowi wciskania. Pionowe piny bezpiecznie przebijają powłokę taśmy i dają 100% pewny styk bez migotania światła. Idealne rozwiązanie do majsterkowania (DIY) i domowych remontów. {warianty}"
        tytul1 = f"Szybkozłączka LED {szerokosc} bez lutowania ({sku})"
        tytul2 = "Idealna do profili LED - niewidoczne łączenie"
        opis2 = "Dzięki krystalicznie przezroczystej i smukłej obudowie złączka bez problemu mieści się w standardowych profilach aluminiowych. Światło swobodnie przenika przez plastik, co eliminuje ciemne plamy w miejscu łączenia."
    elif tab == 'tim':
        opis_glowny = f"Profesjonalny system połączeń dla instalatorów. {kompatybilnosc} Innowacyjna konstrukcja z pionowymi pinami dociskowymi zapewnia pewny styk miedziany, minimalizując spadki napięć i czasochłonność montażu na obiekcie (brak konieczności lutowania). {warianty}"
        tytul1 = f"Instalacyjna złączka do taśm {typ} {szerokosc} ({sku})"
        tytul2 = "Transparentny profil i kompatybilność z korytami aluminiowymi"
        opis2 = "Zoptymalizowany, ultrakompaktowy rozmiar pozwala na bezpośrednią aplikację wewnątrz zamkniętych profili architektonicznych LED. Pełna transparentność materiału PC zapobiega powstawaniu cieni i gwarantuje utrzymanie jednolitej linii światła."
    else:
        opis_glowny = f"{kompatybilnosc} Złączka oparta jest o system pionowych pinów dociskowych, które przebijają powłokę i gwarantują pewny styk bez przerywania i migotania obwodu. {warianty}"
        tytul1 = f"Solidny montaż COB i SMD bez lutowania ({sku})"
        tytul2 = "Brak zaciemnień, idealne do profili LED"
        opis2 = "Smukła i kompaktowa budowa złączki sprawia, że bez problemu mieści się ona w większości aluminiowych profili LED. Dzięki krystalicznie przezroczystej obudowie światło swobodnie przenika na zewnątrz, całkowicie eliminując nieestetyczny efekt martwych, niedoświetlonych stref w miejscu łączenia."

    return f"""<section style="font-family:inherit; margin:28px 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Łączenie {typ} {szerokosc}</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    {tytul1}
  </h3>

  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    {opis_glowny}
  </p>
</section>

<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Transparentny design do profili</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    {tytul2}
  </h3>

  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    {opis2}
  </p>
</section>
{blog_html}"""


def get_scharfer_html(sku, tab):
    parts = sku.split('-')
    if len(parts) >= 3:
        w = parts[1]
        v = parts[2]
    else:
        w = "?"
        v = "?"

    if tab == 'allegro':
        tytul1 = f"Wodoodporny zasilacz do taśm LED {w}W {v}V DC ({sku})"
        opis1 = "Niezawodne i bezpieczne zasilanie Twojego oświetlenia. Zasilacze z tej serii radzą sobie z ciągłą pracą na 100% obciążenia, co pozwala Ci wykorzystać ich pełną moc bez obaw o przegrzanie. Aktywne zabezpieczenia (przeciwzwarciowe, przeciążeniowe) dbają o to, by instalacja w Twoim domu była w pełni bezpieczna i chroniła taśmy LED."
        tytul2 = "Aż 7 lat gwarancji i wodoodporność IP67"
        opis2 = "Inwestycja na lata! Szczelna obudowa (IP67) oznacza, że zasilacz można bez wahania montować w miejscach wilgotnych: w łazience czy na zewnątrz. Metalowy korpus świetnie chłodzi elektronikę, co sprawia, że producent udziela na ten sprzęt aż 7-letniej gwarancji."
    elif tab == 'tim':
        tytul1 = f"Zasilacz instalacyjny stałonapięciowy {v}V DC | {w}W ({sku})"
        opis1 = "Komponent zasilający klasy przemysłowej. Zaprojektowany do ciągłej eksploatacji (100% Load Capacity) bez zjawiska deratingu mocy. Wysoka stabilność napięcia wyjściowego minimalizuje migotanie (flicker) oświetlenia. Wyposażony w komplet sprzętowych, aktywnych zabezpieczeń prądowych i napięciowych chroniących wrażliwe taśmy LED."
        tytul2 = "Szczelność IP67 i gwarancja projektowa 7 lat"
        opis2 = "Hermetyczna obudowa z ekstrudowanego aluminium zapewnia certyfikację IP67 oraz bardzo dobre, pasywne rozpraszanie ciepła w niesprzyjających warunkach środowiskowych. Zasilacz dedykowany do inwestycji z długoterminowym resursowaniem, potwierdzony 7-letnim okresem ochrony gwarancyjnej."
    else:
        tytul1 = f"Stabilne zasilanie z obsługą 100% obciążenia ({sku})"
        opis1 = "Zasilacze z tej serii charakteryzują się bardzo stabilnym napięciem wyjściowym i zdolnością do ciągłej pracy pod pełnym, stuprocentowym obciążeniem. To sprzęt klasy premium dla wymagających instalacji, redukujący migotanie i przedłużający żywotność samych taśm LED. Wbudowane, aktywne zabezpieczenia: przeciwzwarciowe, przeciążeniowe i nadnapięciowe chronią Twój obwód."
        tytul2 = "Szczelny metalowy korpus i legendarna bezawaryjność"
        opis2 = "Obudowa o klasie wodoszczelności IP67 gwarantuje, że elektronika jest w pełni uodporniona na kurz, zabrudzenia i wilgoć. Dzięki doskonałemu odprowadzaniu ciepła przez zwarty korpus, zasilacze Scharfer objęte są bezkompromisową, 7-letnią gwarancją producenta – to dowód na rzeczywistą trwałość, potwierdzoną certyfikatem CE."

    return f"""<section style="font-family:inherit; margin:28px 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">Napięcie {v}V DC | Moc {w}W</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    {tytul1}
  </h3>

  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    {opis1}
  </p>
</section>

<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">IP67 | 7 LAT GWARANCJI</font>
  </span>

  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    {tytul2}
  </h3>

  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    {opis2}
  </p>
</section>
{blog_zasilacze_html}"""


# SKUs to update
sterowniki = ['PR-CCT-12A', 'PR-MONO-12A', 'PR-RGB-12A', 'PR-RGBCCT-12A', 'PR-RGBW-12A']
zlaczki = ['FC8-MONO-MULTI-9IN1', 'FC8-MONO-MULTI-TP', 'FC8-MONO-MULTI-TPT', 'FC8-MONO-MULTI', 'FC8-MONO-MULTI-L', 'FC8-MONO-MULTI-T', 
           'FC10-MONO-MULTI-9IN1', 'FC10-MONO-MULTI-TPT', 'FC10-MONO-MULTI', 'FC10-MONO-MULTI-L', 'FC10-MONO-MULTI-T', 'FC10-MONO-MULTI-TP',
           'FC10-COB-RGB-TP', 'FC10-COB-RGB-TPT', 'FC8-SMD-CCT-TP', 'FC10-SMD-RGB-TP', 'FC10-SMD-RGB-TPT', 'FC10-SMD-RGBW-TP', 'FC10-SMD-RGBW-TPT']
scharfer = ['SCH-18-12', 'SCH-20-12', 'SCH-30-12', 'SCH-45-12', 'SCH-60-12', 'SCH-100-12', 'SCH-150-12', 'SCH-200-12', 'SCH-300-12', 'SCH-400-12', 
            'SCH-18-24', 'SCH-20-24', 'SCH-30-24', 'SCH-45-24', 'SCH-60-24', 'SCH-100-24', 'SCH-150-24', 'SCH-200-24', 'SCH-300-24', 'SCH-400-24']


def update_in_html(content, sku, tab, html_str):
    c_total = 0
    view_pattern = rf'(<div class="model-block" id="desc-view-{tab}-{sku}">)(.*?)(</div>\s*<div class="edit-block" id="desc-edit-{tab}-{sku}")'
    def replacer_view(match):
        return match.group(1) + "\n" + html_str + "\n" + match.group(3)
    content, c1 = re.subn(view_pattern, replacer_view, content, flags=re.DOTALL)
    
    textarea_pattern = rf'(<textarea class="edit-textarea" id="textarea-{tab}-{sku}"[^>]*>)(.*?)(</textarea>)'
    def replacer_textarea(match):
        return match.group(1) + "\n" + html_str + "\n" + match.group(3)
    content, c2 = re.subn(textarea_pattern, replacer_textarea, content, flags=re.DOTALL)
    
    return content, (1 if c1 > 0 or c2 > 0 else 0)

# Update index.html
index_path = '/Users/karolbohdanowicz/my-ai-agents/prescot/index.html'
with open(index_path, 'r', encoding='utf-8') as f:
    index_content = f.read()

updated_html = 0

for sku in sterowniki:
    for tab in ['wapro', 'tim', 'allegro']:
        h = get_sterownik_html(sku, tab)
        index_content, c = update_in_html(index_content, sku, tab, h)
        updated_html += c

for sku in zlaczki:
    for tab in ['wapro', 'tim', 'allegro']:
        h = get_zlaczka_html(sku, tab)
        index_content, c = update_in_html(index_content, sku, tab, h)
        updated_html += c

for sku in scharfer:
    for tab in ['wapro', 'tim', 'allegro']:
        h = get_scharfer_html(sku, tab)
        index_content, c = update_in_html(index_content, sku, tab, h)
        updated_html += c

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(index_content)

print(f"Updated {updated_html} elements in index.html")

# Update Excel using standard wapro HTML as the master description for the export file
excel_path = '/Users/karolbohdanowicz/Desktop/EksportowaneArtykuly.xlsx'
df = pd.read_excel(excel_path)
updated_excel = 0

all_products = {}
for s in sterowniki: all_products[s] = get_sterownik_html(s, 'wapro')
for z in zlaczki: all_products[z] = get_zlaczka_html(z, 'wapro')
for sc in scharfer: all_products[sc] = get_scharfer_html(sc, 'wapro')

for idx, row in df.iterrows():
    sku = str(row['INDEKS_HANDLOWY']).strip()
    if sku in all_products:
        df.at[idx, 'OPIS'] = all_products[sku]
        updated_excel += 1

df.to_excel(excel_path, index=False)
print(f"Updated {updated_excel} rows in Excel")
