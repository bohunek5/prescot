import re
import random
import os
from bs4 import BeautifulSoup

def extract_params(sku, full_text):
    params = {
        'lm': None, 'k': None, 'w': None, 'v': None, 'ip': 20, 
        'len': 5, 'y': 5, 'type': 'other', 'cct': False, 'rgb': False
    }
    
    if 'WCOB' in sku or 'D00' in sku or 'COB' in sku or 'tasmy' in full_text.lower() or 'taśma' in full_text.lower() or 'SMD' in sku:
        params['type'] = 'tape'
    elif sku.startswith('SCH-') or sku.startswith('POS-') or 'zasilacz' in full_text.lower():
        params['type'] = 'power'
        if 'SCH-' in sku:
            params['y'] = 7
    elif sku.startswith('FC-') or sku.startswith('RC-') or sku.startswith('B') or 'sterownik' in full_text.lower() or 'odbiornik' in full_text.lower() or 'pilot' in full_text.lower():
        params['type'] = 'controller'

    lm_match = re.search(r'(\d+)\s*lm', full_text, re.I)
    if lm_match: params['lm'] = int(lm_match.group(1))

    k_match = re.search(r'(\d{4})K', full_text, re.I)
    if k_match: params['k'] = int(k_match.group(1))

    if 'CCT' in full_text or 'CCT' in sku: params['cct'] = True
    if 'RGB' in full_text or 'RGB' in sku: params['rgb'] = True

    w_match = re.search(r'(\d+)\s*W', full_text, re.I)
    if w_match: params['w'] = int(w_match.group(1))

    v_match = re.search(r'(12|24)V', full_text, re.I)
    if v_match: params['v'] = int(v_match.group(1))
    elif '12V' in sku: params['v'] = 12
    elif '24V' in sku: params['v'] = 24

    ip_match = re.search(r'IP(\d{2})', full_text, re.I)
    if ip_match: params['ip'] = int(ip_match.group(1))

    len_match = re.search(r'wariant (\d+)m', full_text, re.I)
    if len_match: params['len'] = int(len_match.group(1))

    y_match = re.search(r'(\d+)\s*(?:lat|lata|Y)', full_text, re.I)
    if y_match: params['y'] = int(y_match.group(1))
    elif 'Scharfer 7Y' in full_text: params['y'] = 7

    return params

def gen_tape_blocks(p):
    blocks = []
    # Block 1: Purpose & Brightness
    if p['lm']:
        if p['lm'] <= 600:
            pills = ["AKCENT ŚWIETLNY", "ŚWIATŁO DEKORACYJNE", "SUBTELNY BLASK"]
            h_templates = ["Idealne tło dla Twojego wnętrza", "Miękkie światło, które nie męczy wzroku", "Zbuduj atmosferę odpowiednim detalem"]
            p_templates = [
                f"Jasność rzędu {p['lm']} lm/m to doskonały wybór do półek, gzymsów, cokołów czy podświetlenia łóżka w sypialni. Światło pełni rolę budowania nastroju.",
                f"Zamiast mocnego naświetlania – delikatny efekt wizualny. Model o wydajności {p['lm']} lm/m idealnie sprawdza się we wnękach i przy subtelnym doświetlaniu mebli."
            ]
        elif p['lm'] <= 1200:
            pills = ["OŚWIETLENIE UŻYTKOWE", "ZŁOTY ŚRODEK", "UNIWERSALNA MOC"]
            h_templates = ["Dobre światło do pracy i na co dzień", "Równomierne doświetlenie blatu", "Komfort wizualny i funkcjonalność"]
            p_templates = [
                f"Parametr {p['lm']} lm/m to klasyka gatunku. Zapewnia odpowiednią ilość światła do kuchni pod szafki, do doświetlania luster czy stanowisk roboczych.",
                f"Złoty kompromis pomiędzy nastrojem a mocą. Z wydajnością {p['lm']} lm/m bez trudu oświetlisz ciągi komunikacyjne oraz domowe strefy aktywności."
            ]
        else:
            pills = ["GŁÓWNE ŹRÓDŁO ŚWIATŁA", "POTĘŻNA WYDAJNOŚĆ", "INTENSYWNE NAŚWIETLENIE"]
            h_templates = ["Zastąp tradycyjne oświetlenie", "Moc wystarczająca dla całego pomieszczenia", "Profesjonalne doświetlenie sufitów"]
            p_templates = [
                f"Aż {p['lm']} lm z każdego metra sprawia, że taśma swobodnie poradzi sobie jako oświetlenie centralne biura, przedpokoju czy dużego salonu.",
                f"Nie uznajesz kompromisów. Moc świetlna rzędu {p['lm']} lm/m pozwala kreować intensywne, wyraziste oświetlenie ogólne w głębokich sufitach podwieszanych."
            ]
        blocks.append((random.choice(pills), random.choice(h_templates), random.choice(p_templates)))
    else:
        blocks.append(("INNOWACJA LED", "Nowoczesne oświetlenie", "Starannie wyselekcjonowane diody zapewniające stabilną emisję i długą żywotność, idealne do projektów wnętrz."))

    # Block 2: Color Temperature
    if p['cct']:
        pills = ["PŁYNNA ZMIANA BARWY", "CCT - TY DECYDUJESZ", "ZMIENNY KLIMAT"]
        h_templates = ["Od relaksu po maksymalne skupienie", "Dopasuj światło do pory dnia"]
        p_templates = [
            "Z technologią CCT nie musisz wybierać. Zależnie od nastroju, płynnie zmieniasz temperaturę z ciepłej (do wieczornego relaksu) na chłodną (do pracy).",
            "Ciepła do odpoczynku, neutralna do czytania. System CCT pozwala na pełną adaptację do naturalnego cyklu dobowego za pomocą odpowiedniego sterownika."
        ]
        blocks.append((random.choice(pills), random.choice(h_templates), random.choice(p_templates)))
    elif p['k']:
        if p['k'] <= 3000:
            pills = ["DOMOWE CIEPŁO", "KLIMATYCZNE WNĘTRZE", "CIEPŁY ODCIEŃ"]
            h_templates = [f"Miękka, przyjemna barwa {p['k']}K", "Idealne do drewna i strefy odpoczynku"]
            p_templates = [
                f"Ciepła biel na poziomie {p['k']}K wizualnie ociepla wnętrze, świetnie rezonując z naturalnymi materiałami, drewnem i tkaninami. Oaza spokoju w salonie.",
                f"Szukasz odpoczynku? Temperatura barwowa {p['k']}K to odpowiednik tradycyjnej, domowej żarówki. Relaksuje i nadaje pomieszczeniom wyjątkowy, przytulny charakter."
            ]
        elif p['k'] <= 4500:
            pills = ["ZŁOTY ŚRODEK (NEUTRALNA)", "CZYSTA BIEL", "NOWOCZESNY WYGLĄD"]
            h_templates = [f"Krystaliczna, naturalna barwa {p['k']}K", "Biel idealna do kuchni i łazienki"]
            p_templates = [
                f"Światło dzienne ({p['k']}K) to najbardziej naturalny wybór, który nie przekłamuje barw otoczenia. Nowoczesny chłód połączony z rześką przejrzystością.",
                f"Jeśli chcesz wyeksponować biel ścian czy nowoczesne, minimalistyczne meble, temperatura rzędu {p['k']}K sprawdzi się najlepiej. Czysta, rześka biel."
            ]
        else:
            pills = ["MOCNY CHŁÓD", "POBUDZENIE I SKUPIENIE", "BARWA ZIMNA"]
            h_templates = [f"Chłodne i rześkie światło {p['k']}K", "Do zadań specjalnych i ekspozycji"]
            p_templates = [
                f"Zimna barwa ({p['k']}K) działa pobudzająco i stymulująco. Doskonale sprawdza się w nowoczesnych przestrzeniach biurowych, garażach oraz jubilerstwie.",
                f"Wysoki kontrast i pełne wyostrzenie detali – barwa {p['k']}K przeznaczona jest do precyzyjnych zastosowań, gdzie liczy się uwydatnienie chłodnych powierzchni."
            ]
        blocks.append((random.choice(pills), random.choice(h_templates), random.choice(p_templates)))
    elif p['rgb']:
        blocks.append(("ŚWIATŁO RGB", "Paleta barw na wyciągnięcie ręki", "Dodaj swoim wnętrzom koloru z taśmą RGB, kreując dynamiczne, klubowe lub relaksacyjne scenerie świetlne."))

    # Block 3: IP / Length / Warranty
    if p['ip'] >= 65:
        pills = ["PEŁNA OCHRONA IP67/68", "ODPORNOŚĆ NA WODĘ", "BEZPIECZEŃSTWO W ŁAZIENCE"]
        h_templates = ["Przeznaczona do stref wilgotnych", "Zabezpieczona przed wodą i pyłem"]
        p_templates = [
            f"Warstwa ochronna (IP{p['ip']}) zabezpiecza komponenty przed strumieniami wody, umożliwiając bezpieczny montaż pod prysznicem, przy lustrze lub na elewacji zewnętrznej.",
            f"Nie martw się o wilgoć. Standard IP{p['ip']} oznacza w pełni hermetyczne rozwiązanie. Nawet w trudnych warunkach taśma zachowa sprawność przez długie lata."
        ]
        blocks.append((random.choice(pills), random.choice(h_templates), random.choice(p_templates)))
    elif p['len'] and p['len'] > 5:
        pills = [f"ROLKA {p['len']} METRÓW", "INSTALACJE BEZ SPADKÓW", "DŁUGIE CIĄGI ŚWIETLNE"]
        h_templates = ["Prostszy montaż profesjonalnych instalacji", "Ciągłość światła bez zbędnych połączeń"]
        p_templates = [
            f"Wersja o długości {p['len']}m ułatwia wyprowadzenie długich linii w sufitach podwieszanych bez obawy o drastyczne spadki napięcia. Mniej punktów podłączeniowych to szybsza praca.",
            f"Rolka fabrycznie nawinięta wariancie {p['len']}m jest przeznaczona do obwodów klasy PRO. Eliminujesz ryzyko nierównomiernego świecenia pod warunkiem odpowiedniego zasilania z dwóch stron."
        ]
        blocks.append((random.choice(pills), random.choice(h_templates), random.choice(p_templates)))
    else:
        pills = [f"TRWAŁOŚĆ {p['y']} LAT", "JAKOŚĆ I GWARANCJA", "CERTYFIKOWANY PRODUKT"]
        h_templates = ["Solidny nośnik PCB na lata", "Inwestycja w sprawdzone komponenty"]
        p_templates = [
            f"Podwójny podkład PCB zapewnia lepsze odprowadzanie ciepła. Dzięki temu, w połączeniu z profilem aluminiowym, taśma objęta jest aż {p['y']}-letnią gwarancją producenta.",
            f"Diody o obniżonym stopniu degradacji luminoforu sprawiają, że nawet po {p['y']} latach użytkowania różnica w świeceniu jest trudna do zauważenia gołym okiem."
        ]
        blocks.append((random.choice(pills), random.choice(h_templates), random.choice(p_templates)))

    return blocks

def gen_power_blocks(p):
    blocks = []
    # Block 1: Power & Voltage
    vol_text = f"{p['v']}V" if p['v'] else "odpowiednie"
    w_text = f"Moc {p['w']}W" if p['w'] else "Duży zapas mocy"
    
    pills = [f"STABILNE NAPIĘCIE {vol_text}", "CIĄGŁA PRACA 100%", "BEZPIECZNA REZERWA"]
    h_templates = [f"{w_text} dla długich instalacji", "Wytrzymuje obciążenia bez przegrzewania", "Klasa przemysłowa do użytku domowego"]
    p_templates = [
        f"Zasilacze tego typu bez problemu utrzymują napięcie {vol_text} przez cały cykl pracy. Oferują realną moc znamionową, zapobiegając irytującemu migotaniu taśm pod obciążeniem.",
        f"Gwarancja ciągłości pracy przy zachowaniu odpowiedniej wentylacji. Model przystosowany jest do wymagających, ciągłych instalacji pod napięciem {vol_text}."
    ]
    blocks.append((random.choice(pills), random.choice(h_templates), random.choice(p_templates)))

    # Block 2: IP
    if p['ip'] >= 65:
        pills = ["PEŁNA HERMETYCZNOŚĆ", "IP67 - WODA I PYŁ", "ODPORNA OBUDOWA"]
        h_templates = ["Zabezpieczone silikonową zalewą", "Gotowy na pracę na zewnątrz i w łazience"]
        p_templates = [
            "Zasilacz wlany w specjalny uszczelniacz termiczny osiągający normę IP67. To oznacza, że nie straszna mu skroplona wilgoć ani ulewne deszcze podczas zewnętrznej pracy.",
            "Wysoki stopień ochrony IP gwarantuje bezpieczeństwo w strefach mokrych (jak łazienki) czy brudnych. Aluminiowa obudowa efektywnie odprowadza gromadzące się ciepło."
        ]
        blocks.append((random.choice(pills), random.choice(h_templates), random.choice(p_templates)))
    else:
        pills = ["WERSJA SLIM / MODUŁOWA", "ŁATWY MONTAŻ", "DO MEBLI I ZABUDOWY"]
        h_templates = ["Kompaktowy rozmiar, łatwe ukrycie", "Świetny design do ciasnych przestrzeni"]
        p_templates = [
            "Zaprojektowany z myślą o sufitach podwieszanych i szafkach meblowych, gdzie przestrzeń montażowa jest mocno ograniczona. Smukła linia nie rzuca się w oczy.",
            "Ażurowa lub ultra-płaska konstrukcja obudowy sprzyja naturalnej cyrkulacji powietrza, dzięki czemu moduł idealnie chłodzi się w dobrze wentylowanych wnękach."
        ]
        blocks.append((random.choice(pills), random.choice(h_templates), random.choice(p_templates)))

    # Block 3: Warranty
    pills = [f"{p['y']} LAT GWARANCJI", "BEZPIECZEŃSTWO AKTYWNE", "WBUDOWANE ZABEZPIECZENIA"]
    h_templates = ["Ochrona przeciwzwarciowa i termiczna", "Solidny sprzęt, z którym śpisz spokojnie"]
    p_templates = [
        f"Producent jest na tyle pewny zastosowanych kondensatorów i cewek, że udziela długiej, {p['y']}-letniej gwarancji. Zaawansowane układy chronią sieć przed przepięciami.",
        f"Gdy temperatura lub prąd obciążenia gwałtownie wzrosną, zabezpieczenia aktywne natychmiast odetną układ. {p['y']} lat gwarancji udowadnia, że to komponent z górnej półki."
    ]
    blocks.append((random.choice(pills), random.choice(h_templates), random.choice(p_templates)))

    return blocks

def gen_controller_blocks(p):
    blocks = []
    # Block 1: Feature
    if p['cct']:
        pills = ["PEŁNA PŁYNNOŚĆ CCT", "STEROWANIE TEMPERATURĄ", "BEZSKOKOWA REGULACJA"]
        h_templates = ["Dotykiem dopasuj barwę do potrzeb", "Błyskawiczna reakcja na zmianę klimatu"]
        p_templates = [
            "Czułe układy sterujące perfekcyjnie miksują diody ciepłe i zimne. W mgnieniu oka przejdziesz z ostrej bieli roboczej do relaksującego, żółtego odcienia wieczoru.",
            "Suwakiem płynnie dopasowujesz bilans barwy. System zachowuje parametry w pamięci po wyłączeniu zasilania, zapewniając komfort za każdym uruchomieniem."
        ]
    elif p['rgb']:
        pills = ["ZABAWA KOLOREM", "DYNAMIKA RGB", "MILIARDY ODCIENI"]
        h_templates = ["Nieskończone możliwości mieszania barw", "Rozkręć imprezę lub wycisz wnętrze"]
        p_templates = [
            "Inteligentny system zarządzający kolorami RGB pozwala na miksowanie barw i tworzenie własnych, unikalnych przejść świetlnych. Zabawa światłem bez końca.",
            "Wybieraj statyczny kolor lub uruchamiaj automatyczne pętle. Z tym sterownikiem wydobędziesz z taśmy RGB maksimum jej spektakularnych możliwości barwnych."
        ]
    else:
        pills = ["ŚCIEMNIANIE PWM", "PRECYZYJNA KONTROLA", "BEZ EFEKTU MIGOTANIA"]
        h_templates = ["Od 1% do 100% jasności z pełną gracją", "Najwyższej klasy częstotliwość sterowania"]
        p_templates = [
            "Zaawansowana krzywa ściemniania zapewnia super płynne rozjaśnianie bez zjawiska irytującego skakania jasności w najniższych rejestrach.",
            "Wysoka częstotliwość próbkowania PWM całkowicie eliminuje widoczne zjawisko migotania. Twoje oczy odpoczną przy ściemnionym świetle jak nigdy dotąd."
        ]
    blocks.append((random.choice(pills), random.choice(h_templates), random.choice(p_templates)))

    # Block 2 & 3: Range & Ecosystem
    pills_2 = ["KOMUNIKACJA RADIOWA", "ZASIĘG PRZEZ ŚCIANY", "STABILNY SYGNAŁ"]
    h_2 = "Zero zakłóceń dzięki fali RF"
    p_2 = "Zastosowanie szyfrowanej częstotliwości radiowej sprawia, że nie musisz celować pilotem w odbiornik. Sygnał z łatwością pokonuje cienkie ściany, drewno i gips-karton."
    blocks.append((random.choice(pills_2), h_2, p_2))

    pills_3 = ["SYSTEM WIELE-DO-WIELU", "BUDOWA STREF", "JEDEN PILOT - CAŁY DOM"]
    h_3 = "Bezproblemowe rozszerzanie ekosystemu"
    p_3 = "Rozbuduj system w przyszłości. Bez trudu przypiszesz wiele odbiorników pod jedną strefę w pilocie, lub użyjesz kilku pilotów naściennych do sterowania jedną taśmą."
    blocks.append((random.choice(pills_3), h_3, p_3))

    return blocks

with open('index.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

for acc in soup.find_all('div', class_='product-accordion'):
    sku = acc.get('data-model', '')
    full_text = acc.get_text()
    
    # Check if there is an exact params span with pill format
    # Extract params
    p = extract_params(sku, full_text)
    
    # Gen Blocks
    if p['type'] == 'tape':
        blocks = gen_tape_blocks(p)
    elif p['type'] == 'power':
        blocks = gen_power_blocks(p)
    elif p['type'] == 'controller':
        blocks = gen_controller_blocks(p)
    else:
        continue # skip others (e.g. tools, profiles)

    desc_view = acc.find('div', class_='model-block')
    if desc_view:
        new_html = ""
        for (pill, h, text) in blocks:
            new_html += f"""
<section style="font-family: inherit; margin: 0 0 18px 0; padding: 22px 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
<span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;"> <span style="color: #ffffff;">{pill}</span> </span>
<h3 style="font-family: inherit; margin: 0 0 8px 0; background: none !important; background-color: transparent !important; color: inherit !important; font-size: 22px; line-height: 1.3; font-weight: bold;">{h}</h3>
<p style="font-family: inherit; margin: 0; background: none !important; background-color: transparent !important; color: inherit !important; font-size: 16px; line-height: 1.6; opacity: 0.85;">{text}</p>
</section>
"""
        # Clear contents and append new raw HTML
        desc_view.clear()
        desc_view.append(BeautifulSoup(new_html, 'html.parser'))

    textarea = acc.find('textarea')
    if textarea:
        new_text = ""
        for (pill, h, text) in blocks:
            new_text += f"{pill}\n{h}\n{text}\n\n"
        textarea.string = new_text.strip()

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))
print("Descriptions completely re-generated with dynamic parameter mapping!")
