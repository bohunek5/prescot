#!/usr/bin/env python3
"""
Master generator portalu TIM — łączy Taśmy LED, Zasilacze LED i Akcesoria montażowe.
Zasilacze:
- ⭐ 1. PR-MAD Smart Auto 12V/24V (na samej górze!)
- 🏆 2. Schärfer Hermetyczne IP67 7Y (zaraz pod PR-MAD!)
- 📦 3. Pozostałe modele (Mean Well, Prescot Slim/DIN/Dopuszkowe)
"""

import json
import os
import sys

BASE_DIR = "/Users/karolbohdanowicz/my-ai-agents/prescot/tmp/tim-opisy-tasmy"


def esc(s):
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_unified_html(tapes, zasilacze, akcesoria):
    total_count = len(tapes) + len(zasilacze) + len(akcesoria)

    # 1. Render Tapes (Delux 7Y first)
    # Sort tapes so Delux PL7Y is at the top
    tapes_sorted = sorted(tapes, key=lambda p: (
        0 if "delux" in p["name"].lower() and (p.get("parsed_info",{}).get("is_pl") or "7" in str(p.get("parsed_info",{}).get("warranty",""))) else (
            1 if p.get("parsed_info",{}).get("is_pl") or p.get("parsed_info",{}).get("series") == "Delux" else 2
        ),
        p.get("subcat",""),
        p["name"]
    ))

    tapes_html = []
    for i, p in enumerate(tapes_sorted, 1):
        d = p["description"]
        info = p.get("parsed_info", {})
        badges = []
        if info.get("series") == "Delux" or "delux" in p["name"].lower():
            badges.append('<span class="badge badge-flag-delux">👑 DELUX 7 LAT GWARANCJI</span>')
        badges.append(f'<span class="badge badge-volt">{esc(info.get("voltage","12V"))}</span>')
        badges.append(f'<span class="badge badge-width">{esc(info.get("width","8 mm"))}</span>')
        badges.append(f'<span class="badge badge-power">{esc(str(info.get("power_w_m",4.8)))} W/m</span>')
        len_m = info.get("length_m", 5)
        pwm = info.get("power_w_m", 4.8)
        calc_1m = 12 if pwm <= 9.6 else (24 if pwm <= 19.2 else int(round(pwm * 1.2)))
        if len_m >= 15:
            badges.append(f'<span class="badge badge-psu">⚡ Zasilacz: min. {calc_1m}W/m</span>')
            badges.append(f'<span class="badge badge-len">📏 Szpula {len_m}m</span>')
        elif info.get("is_meter") or len_m == 1:
            badges.append(f'<span class="badge badge-psu">⚡ Zasilacz: min. {calc_1m}W/m</span>')
            badges.append('<span class="badge badge-len">📏 Na metry</span>')
        else:
            badges.append(f'<span class="badge badge-psu">⚡ Zasilacz: {esc(str(info.get("psu_rec",30)))}W</span>')
            badges.append(f'<span class="badge badge-len">📏 Rolka {len_m}m</span>')
        badges.append(f'<span class="badge badge-war">🛡️ {esc(str(info.get("warranty",3)))} lat</span>')
        if info.get("is_pl"):
            badges.append('<span class="badge badge-pl">🇵🇱 Polska</span>')
        if info.get("is_ip67"):
            badges.append(f'<span class="badge badge-ip">💧 {esc(info.get("ip","IP67"))}</span>')

        is_delux_top = "card-highlight-delux" if info.get("series") == "Delux" else ""

        tapes_html.append(f'''
<article class="product-card {is_delux_top}" id="tape-{i}" data-category="tasmy" data-subcat="{esc(p.get("subcat",""))}">
  <div class="card-header">
    <div class="card-top-row">
      <span class="card-num">#T{i}</span>
      <div class="badges-row">{"".join(badges)}</div>
    </div>
    <h3 class="card-name">{esc(p["name"])}</h3>
    <div class="card-meta">
      <span class="meta-code">Kod: {esc(p["code"])}</span>
      <span class="meta-ean">EAN: {esc(p["ean"])}</span>
      <span class="meta-subcat">Kategoria: {esc(p.get("subcat",""))}</span>
      <span class="meta-price">{esc(p["price"])} PLN</span>
    </div>
  </div>
  <div class="card-body">
    <div class="desc-block intro">
      <div class="section-title">WPROWADZENIE</div>
      <p>{esc(d["intro"])}</p>
    </div>
    <div class="desc-block barwa">
      <div class="section-title">BARWA ŚWIATŁA I ZASTOSOWANIE</div>
      <p>{esc(d["barwa"].replace("Barwa światła i zastosowanie", "").strip())}</p>
    </div>
    <div class="desc-block dobor">
      <div class="section-title">DOBÓR I BEZPIECZEŃSTWO</div>
      <p>{esc(d["dobor"].replace("Dobór i bezpieczeństwo", "").strip())}</p>
    </div>
  </div>
  <div class="card-actions">
    <button class="btn-copy" onclick="copyDesc(this)">📋 Kopiuj pełny opis (Plain Text)</button>
  </div>
</article>''')

    # 2. Render Zasilacze (PR-MAD first, then Schärfer, then others)
    zas_html = []
    prmad_cnt = 0
    sch_cnt = 0
    std_cnt = 0

    for i, p in enumerate(zasilacze, 1):
        d = p["description"]
        info = p.get("parsed_info", {})
        is_prmad = info.get("is_prmad", False)
        is_sch = info.get("is_scharfer", False)

        badges = []
        highlight_class = ""

        if is_prmad:
            prmad_cnt += 1
            highlight_class = "card-highlight-prmad"
            badges.append('<span class="badge badge-flag-prmad">⭐ FLAGOWY SMART AUTO 12V/24V</span>')
        elif is_sch:
            sch_cnt += 1
            highlight_class = "card-highlight-sch"
            badges.append('<span class="badge badge-flag-sch">🏆 SCHÄRFER 7Y HERMETIC IP67</span>')
        else:
            std_cnt += 1
            badges.append(f'<span class="badge badge-brand">{esc(info.get("brand","Prescot"))}</span>')

        badges.append(f'<span class="badge badge-volt">{esc(info.get("voltage","12V"))}</span>')
        badges.append(f'<span class="badge badge-psu">⚡ {esc(str(info.get("power_w",0)))} W</span>')
        badges.append(f'<span class="badge badge-power">Użyteczna: {esc(str(info.get("usable_power",0)))} W</span>')
        badges.append(f'<span class="badge badge-ip">🛡️ {esc(info.get("ip","IP20"))}</span>')
        badges.append(f'<span class="badge badge-war">{esc(str(info.get("warranty",3)))} lat gw.</span>')

        zas_html.append(f'''
<article class="product-card {highlight_class}" id="zas-{i}" data-category="zasilacze" data-subcat="{esc(p.get("subcat",""))}">
  <div class="card-header">
    <div class="card-top-row">
      <span class="card-num">#Z{i}</span>
      <div class="badges-row">{"".join(badges)}</div>
    </div>
    <h3 class="card-name">{esc(p["name"])}</h3>
    <div class="card-meta">
      <span class="meta-code">Kod: {esc(p["code"])}</span>
      <span class="meta-ean">EAN: {esc(p["ean"])}</span>
      <span class="meta-subcat">Typ: {esc(p.get("subcat",""))}</span>
      <span class="meta-price">{esc(p["price"])} PLN</span>
    </div>
  </div>
  <div class="card-body">
    <div class="desc-block intro">
      <div class="section-title">WPROWADZENIE</div>
      <p>{esc(d["intro"])}</p>
    </div>
    <div class="desc-block gdzie">
      <div class="section-title">GDZIE UŻYĆ I MONTAŻ</div>
      <p>{esc(d["gdzie"].replace("Gdzie użyć i montaż", "").strip())}</p>
    </div>
    <div class="desc-block zczym">
      <div class="section-title">Z CZYM UŻYĆ I DOBÓR MOCY</div>
      <p>{esc(d["z_czym"].replace("Z czym użyć i dobór mocy", "").strip())}</p>
    </div>
  </div>
  <div class="card-actions">
    <button class="btn-copy" onclick="copyDesc(this)">📋 Kopiuj pełny opis (Plain Text)</button>
  </div>
</article>''')

    # 3. Render Akcesoria
    akc_html = []
    for i, p in enumerate(akcesoria, 1):
        d = p["description"]
        info = p.get("parsed_info", {})
        badges = [
            f'<span class="badge badge-width">Szerokość: {esc(info.get("width","8 mm"))}</span>',
            f'<span class="badge badge-volt">{esc(info.get("pin_type","MONO"))}</span>',
            f'<span class="badge badge-power">{esc(info.get("shape","prosta"))}</span>',
            f'<span class="badge badge-war">🛡️ 2 lata gw.</span>',
        ]
        akc_html.append(f'''
<article class="product-card" id="akc-{i}" data-category="akcesoria" data-subcat="{esc(p.get("subcat",""))}">
  <div class="card-header">
    <div class="card-top-row">
      <span class="card-num">#A{i}</span>
      <div class="badges-row">{"".join(badges)}</div>
    </div>
    <h3 class="card-name">{esc(p["name"])}</h3>
    <div class="card-meta">
      <span class="meta-code">Kod: {esc(p["code"])}</span>
      <span class="meta-ean">EAN: {esc(p["ean"])}</span>
      <span class="meta-subcat">Grupa: {esc(p.get("subcat",""))}</span>
      <span class="meta-price">{esc(p["price"])} PLN</span>
    </div>
  </div>
  <div class="card-body">
    <div class="desc-block intro">
      <div class="section-title">WPROWADZENIE</div>
      <p>{esc(d["intro"])}</p>
    </div>
    <div class="desc-block gdzie">
      <div class="section-title">GDZIE UŻYĆ I FUNKCJA W INSTALACJI</div>
      <p>{esc(d["gdzie"].replace("Gdzie użyć i funkcja w instalacji", "").strip())}</p>
    </div>
    <div class="desc-block zczym">
      <div class="section-title">Z CZYM UŻYĆ I WSKAZÓWKI MONTAŻOWE</div>
      <p>{esc(d["z_czym"].replace("Z czym użyć i wskazówki montażowe", "").strip())}</p>
    </div>
  </div>
  <div class="card-actions">
    <button class="btn-copy" onclick="copyDesc(this)">📋 Kopiuj pełny opis (Plain Text)</button>
  </div>
</article>''')

    return f'''<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Prescot TIM — Baza Opisów Produktów ({total_count})</title>
<style>
*,*::before,*::after{{box-sizing:border-box}}
:root{{
  --bg:#090b10;--surface:#131620;--surface-hover:#1a1e2c;--border:#242838;
  --text:#e4e6eb;--text-dim:#949ba8;--accent:#e94b25;--accent-hover:#d63c18;
  --green:#22c55e;--blue:#3b82f6;--purple:#a855f7;--amber:#f59e0b;--cyan:#06b6d4;--gold:#fbbf24;
  --font:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
}}
body{{margin:0;font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.6}}
.wrap{{max-width:1100px;margin:0 auto;padding:24px 20px 100px}}

header{{text-align:center;padding:32px 0 20px;border-bottom:1px solid var(--border)}}
header h1{{font-size:32px;margin:0 0 8px;color:var(--accent);letter-spacing:-0.5px}}
header p{{margin:0;color:var(--text-dim);font-size:15px}}

/* Navigation Tabs */
.nav-tabs{{display:flex;gap:10px;justify-content:center;margin:24px 0 16px;flex-wrap:wrap}}
.tab-btn{{
  background:var(--surface);border:1px solid var(--border);border-radius:12px;
  padding:12px 22px;color:var(--text);font-size:15px;font-weight:700;cursor:pointer;
  display:inline-flex;align-items:center;gap:10px;transition:all .2s;
}}
.tab-btn:hover{{border-color:var(--accent);background:var(--surface-hover)}}
.tab-btn.active{{background:var(--accent);border-color:var(--accent);color:#fff;box-shadow:0 4px 16px rgba(233,75,37,0.35)}}
.tab-count{{background:rgba(0,0,0,0.25);padding:2px 8px;border-radius:999px;font-size:12px;font-weight:800}}

.stats{{display:flex;gap:14px;justify-content:center;margin:20px 0 24px;flex-wrap:wrap}}
.stat{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:10px 20px;text-align:center;min-width:130px}}
.stat-num{{font-size:24px;font-weight:800;color:var(--accent)}}
.stat-label{{font-size:11px;color:var(--text-dim);text-transform:uppercase;letter-spacing:1px;font-weight:600}}

/* Search bar */
.search-box{{
  position:sticky;top:14px;z-index:100;padding:12px 0;
  background:rgba(9,11,16,0.92);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  margin-bottom:24px;
}}
.search-box input{{
  width:100%;padding:14px 22px;font-size:15px;border:1px solid var(--border);
  border-radius:14px;background:var(--surface);color:var(--text);
  outline:none;transition:border-color .2s,box-shadow .2s;
}}
.search-box input:focus{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(233,75,37,0.25)}}
.search-box input::placeholder{{color:var(--text-dim)}}

/* Product Cards */
.tab-content{{display:none}}
.tab-content.active{{display:block}}

.product-card{{
  background:var(--surface);border:1px solid var(--border);border-radius:14px;
  margin:0 0 20px;overflow:hidden;transition:border-color .2s,background .2s;
}}
.product-card:hover{{border-color:#383e54}}

/* Flagship Highlights */
.card-highlight-prmad{{
  border:2px solid #f59e0b !important;
  background:linear-gradient(180deg, rgba(245,158,11,0.06) 0%, var(--surface) 100%);
  box-shadow:0 4px 20px rgba(245,158,11,0.12);
}}
.card-highlight-sch{{
  border:2px solid #06b6d4 !important;
  background:linear-gradient(180deg, rgba(6,182,212,0.06) 0%, var(--surface) 100%);
  box-shadow:0 4px 20px rgba(6,182,212,0.12);
}}
.card-highlight-delux{{
  border:2px solid #a855f7 !important;
  background:linear-gradient(180deg, rgba(168,85,247,0.06) 0%, var(--surface) 100%);
  box-shadow:0 4px 20px rgba(168,85,247,0.12);
}}

.card-header{{padding:18px 22px 14px;border-bottom:1px solid var(--border)}}
.card-top-row{{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px}}
.card-num{{color:var(--accent);font-weight:800;font-size:14px}}

.badges-row{{display:flex;gap:6px;flex-wrap:wrap}}
.badge{{
  font-size:11px;font-weight:600;padding:3px 8px;border-radius:6px;
  background:#1e2333;color:var(--text-dim);letter-spacing:0.3px;
}}
.badge-volt{{background:rgba(59,130,246,0.15);color:#60a5fa;border:1px solid rgba(59,130,246,0.3)}}
.badge-width{{background:rgba(168,85,247,0.15);color:#c084fc;border:1px solid rgba(168,85,247,0.3)}}
.badge-power{{background:rgba(245,158,11,0.15);color:#fbbf24;border:1px solid rgba(245,158,11,0.3)}}
.badge-psu{{background:rgba(34,197,94,0.15);color:#4ade80;border:1px solid rgba(34,197,94,0.3);font-weight:700}}
.badge-war{{background:rgba(233,75,37,0.15);color:#f87171;border:1px solid rgba(233,75,37,0.3)}}
.badge-pl{{background:rgba(244,63,94,0.15);color:#fb7185;border:1px solid rgba(244,63,94,0.3)}}
.badge-ip{{background:rgba(14,165,233,0.15);color:#38bdf8;border:1px solid rgba(14,165,233,0.3)}}
.badge-brand{{background:rgba(6,182,212,0.15);color:#22d3ee;border:1px solid rgba(6,182,212,0.3);font-weight:700}}

.badge-flag-prmad{{background:linear-gradient(135deg, #f59e0b, #d97706);color:#000;font-weight:800;border:none;box-shadow:0 2px 8px rgba(245,158,11,0.4)}}
.badge-flag-sch{{background:linear-gradient(135deg, #06b6d4, #0891b2);color:#000;font-weight:800;border:none;box-shadow:0 2px 8px rgba(6,182,212,0.4)}}
.badge-flag-delux{{background:linear-gradient(135deg, #a855f7, #7e22ce);color:#fff;font-weight:800;border:none;box-shadow:0 2px 8px rgba(168,85,247,0.4)}}

.card-name{{margin:0 0 10px;font-size:16px;font-weight:700;line-height:1.45;color:#fff}}
.card-meta{{display:flex;gap:14px;font-size:12px;color:var(--text-dim);flex-wrap:wrap}}
.meta-code,.meta-ean{{background:#0b0d13;padding:2px 8px;border-radius:4px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}
.meta-subcat{{color:#949ba8}}
.meta-price{{color:var(--accent);font-weight:700;margin-left:auto}}

.card-body{{padding:20px 22px}}
.desc-block{{margin:0 0 18px}}
.desc-block:last-child{{margin-bottom:0}}
.section-title{{font-size:11px;font-weight:800;letter-spacing:1px;color:var(--accent);margin-bottom:6px}}
.desc-block p{{margin:0;font-size:14px;color:#d1d5db;line-height:1.7;white-space:pre-line}}
.desc-block.intro p{{font-size:14.5px;color:#f3f4f6;font-weight:500}}

.card-actions{{padding:0 22px 18px;display:flex;gap:12px}}
.btn-copy{{
  background:var(--accent);color:#fff;border:none;border-radius:8px;
  padding:10px 18px;font-size:13px;font-weight:700;cursor:pointer;
  transition:all .15s;display:inline-flex;align-items:center;gap:6px;
}}
.btn-copy:hover{{background:var(--accent-hover);transform:translateY(-1px)}}
.btn-copy.copied{{background:var(--green)}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>🏷️ Prescot TIM — Kompletna Baza Opisów</h1>
    <p>Gotowe opisy plain text do TIM.pl • Flagowe PR-MAD & Schärfer na samej górze!</p>
  </header>

  <div class="stats">
    <div class="stat"><div class="stat-num">{total_count}</div><div class="stat-label">Wszystkich Produktów</div></div>
    <div class="stat"><div class="stat-num">{len(tapes)}</div><div class="stat-label">Taśm LED (Delux 7Y TOP)</div></div>
    <div class="stat"><div class="stat-num">{len(zasilacze)}</div><div class="stat-label">Zasilaczy (PR-MAD & Schärfer TOP)</div></div>
    <div class="stat"><div class="stat-num">{len(akcesoria)}</div><div class="stat-label">Akcesoriów LED</div></div>
  </div>

  <nav class="nav-tabs">
    <button class="tab-btn active" onclick="switchTab('tasmy', this)">
      🌟 Taśmy LED <span class="tab-count">{len(tapes)}</span>
    </button>
    <button class="tab-btn" onclick="switchTab('zasilacze', this)">
      ⚡ Zasilacze LED (PR-MAD & Schärfer TOP) <span class="tab-count">{len(zasilacze)}</span>
    </button>
    <button class="tab-btn" onclick="switchTab('akcesoria', this)">
      🔌 Akcesoria montażowe <span class="tab-count">{len(akcesoria)}</span>
    </button>
  </nav>

  <div class="search-box">
    <input type="search" id="search" placeholder="Szukaj po nazwie (np. Schärfer, PR-MAD, Delux), kodzie, EAN, mocy (W), szerokości (mm), napięciu (12V/24V)..." autocomplete="off">
  </div>

  <main>
    <section id="tab-tasmy" class="tab-content active">
      {"".join(tapes_html)}
    </section>

    <section id="tab-zasilacze" class="tab-content">
      {"".join(zas_html)}
    </section>

    <section id="tab-akcesoria" class="tab-content">
      {"".join(akc_html)}
    </section>
  </main>
</div>

<script>
function switchTab(tabName, btn) {{
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('tab-' + tabName).classList.add('active');
  filterProducts();
}}

function copyDesc(btn) {{
  const card = btn.closest('.product-card');
  const blocks = card.querySelectorAll('.desc-block');
  let text = '';
  blocks.forEach(b => {{
    const title = b.querySelector('.section-title');
    const p = b.querySelector('p');
    if (title && title.textContent !== 'WPROWADZENIE') {{
      let t = title.textContent;
      if (t === 'BARWA ŚWIATŁA I ZASTOSOWANIE') t = 'Barwa światła i zastosowanie';
      if (t === 'DOBÓR I BEZPIECZEŃSTWO') t = 'Dobór i bezpieczeństwo';
      if (t === 'GDZIE UŻYĆ I MONTAŻ') t = 'Gdzie użyć i montaż';
      if (t === 'Z CZYM UŻYĆ I DOBÓR MOCY') t = 'Z czym użyć i dobór mocy';
      if (t === 'GDZIE UŻYĆ I FUNKCJA W INSTALACJI') t = 'Gdzie użyć i funkcja w instalacji';
      if (t === 'Z CZYM UŻYĆ I WSKAZÓWKI MONTAŻOWE') t = 'Z czym użyć i wskazówki montażowe';
      text += t + '\\n';
    }}
    if (p) text += p.textContent + '\\n\\n';
  }});
  navigator.clipboard.writeText(text.trim());
  btn.textContent = '✅ Skopiowano!';
  btn.classList.add('copied');
  setTimeout(() => {{ btn.textContent = '📋 Kopiuj pełny opis (Plain Text)'; btn.classList.remove('copied'); }}, 1600);
}}

function filterProducts() {{
  const q = document.getElementById('search').value.toLowerCase();
  const activeTab = document.querySelector('.tab-content.active');
  if (!activeTab) return;
  activeTab.querySelectorAll('.product-card').forEach(card => {{
    const text = card.textContent.toLowerCase();
    card.style.display = text.includes(q) ? '' : 'none';
  }});
}}

document.getElementById('search').addEventListener('input', filterProducts);
</script>
</body>
</html>'''


def main():
    tapes_path = os.path.join(BASE_DIR, "tim_tapes_descriptions.json")
    zas_path = os.path.join(BASE_DIR, "tim_zasilacze_descriptions.json")
    akc_path = os.path.join(BASE_DIR, "tim_akcesoria_descriptions.json")

    with open(tapes_path, "r", encoding="utf-8") as f:
        tapes = json.load(f)
    with open(zas_path, "r", encoding="utf-8") as f:
        zasilacze = json.load(f)
    with open(akc_path, "r", encoding="utf-8") as f:
        akcesoria = json.load(f)

    html_content = build_unified_html(tapes, zasilacze, akcesoria)
    index_path = os.path.join(BASE_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Zaktualizowano portal TIM z priorytetami na samej górze!")
    print(f"   Łącznie produktów: {len(tapes) + len(zasilacze) + len(akcesoria)}")
    print(f"   - Zasilacze: {len(zasilacze)} (w tym PR-MAD na samej górze, zaraz po nich Schärfer)")
    print(f"   - Taśmy: {len(tapes)} (w tym Delux PL 7Y na samej górze)")
    print(f"   - Akcesoria: {len(akcesoria)}")


if __name__ == "__main__":
    main()
