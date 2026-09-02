#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ulepsza kalkulator LED w Bazie Wiedzy:
- Wizualny schemat instalacji z dynamicznym spadkiem napięcia na początku i końcu taśmy.
- Gotowe profile / presety instalacji (Sufit w salonie, Blat kuchenny, Wnęka LED, Linia COB).
- Luksusowy design w stylu Apple / Porsche Design z dynamicznym paskiem obciążenia i mikroanimacjami.
- Inteligentny dobór zasilacza Prescot Ultra Slim z bezpośrednim linkiem do sklepu.
"""

import re
import os

CALC_CSS = """
  /* =========================================================
     LUXURY APPLE-GRADE LED CALCULATOR (UPGRADED 2026)
     ========================================================= */
  .apple-calc-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 24px;
    box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.08);
    overflow: hidden;
    margin-bottom: 80px;
    transition: box-shadow 0.3s ease;
  }
  .apple-calc-card:hover {
    box-shadow: 0 25px 50px -12px rgba(229, 89, 51, 0.12);
  }
  .apple-calc-header {
    padding: 32px 36px 24px 36px;
    border-bottom: 1px solid #f1f5f9;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #ffffff;
    flex-wrap: wrap;
    gap: 16px;
  }
  .apple-calc-header h2 {
    font-family: 'Outfit', sans-serif;
    font-size: clamp(22px, 2.5vw, 28px);
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
  }
  .apple-calc-header p {
    font-size: 14.5px;
    color: #64748b;
  }
  .apple-calc-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 700;
    color: #e55933;
    background: rgba(229, 89, 51, 0.08);
    border: 1px solid rgba(229, 89, 51, 0.2);
    padding: 7px 16px;
    border-radius: 999px;
    letter-spacing: 0.3px;
  }

  /* PRESET BUTTONS */
  .calc-presets-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 36px;
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    overflow-x: auto;
    white-space: nowrap;
  }
  .calc-preset-label {
    font-size: 12px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-right: 4px;
  }
  .calc-preset-btn {
    padding: 6px 14px;
    border-radius: 999px;
    border: 1px solid #e2e8f0;
    background: #ffffff;
    color: #334155;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }
  .calc-preset-btn:hover {
    border-color: #e55933;
    color: #e55933;
    background: #fff5f2;
  }

  .apple-calc-body {
    display: grid;
    grid-template-columns: 1fr 1.08fr;
    background: #ffffff;
  }
  @media (max-width: 960px) {
    .apple-calc-body { grid-template-columns: 1fr; }
  }

  .apple-calc-config {
    padding: 36px;
    border-right: 1px solid #f1f5f9;
    display: flex;
    flex-direction: column;
    gap: 26px;
  }
  @media (max-width: 960px) {
    .apple-calc-config { border-right: none; border-bottom: 1px solid #f1f5f9; }
  }

  .calc-field-group {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .calc-field-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .calc-field-label {
    font-size: 13.5px;
    font-weight: 700;
    color: #0f172a;
  }
  .calc-field-val-display {
    font-size: 13.5px;
    font-weight: 800;
    color: #e55933;
    font-family: 'Outfit', sans-serif;
  }

  .apple-segmented {
    display: flex;
    background: #f1f5f9;
    padding: 4px;
    border-radius: 14px;
    gap: 4px;
  }
  .apple-seg-btn {
    flex: 1;
    padding: 10px 14px;
    border: none;
    background: transparent;
    border-radius: 10px;
    font-size: 13.5px;
    font-weight: 700;
    color: #64748b;
    cursor: pointer;
    transition: all 0.25s ease;
  }
  .apple-seg-btn.active {
    background: #ffffff;
    color: #0f172a;
    box-shadow: 0 3px 8px rgba(0,0,0,0.06);
  }

  .apple-chip-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
    gap: 8px;
  }
  .apple-chip-btn {
    padding: 10px 8px;
    border: 1px solid #e2e8f0;
    background: #f8fafc;
    border-radius: 10px;
    font-size: 12.5px;
    font-weight: 700;
    color: #475569;
    cursor: pointer;
    text-align: center;
    transition: all 0.2s ease;
  }
  .apple-chip-btn:hover { border-color: #cbd5e1; background: #ffffff; }
  .apple-chip-btn.active {
    border-color: #e55933;
    background: rgba(229, 89, 51, 0.08);
    color: #e55933;
    box-shadow: 0 2px 6px rgba(229, 89, 51, 0.1);
  }

  .apple-slider-wrap {
    display: flex;
    align-items: center;
    gap: 14px;
  }
  .apple-range-slider {
    flex: 1;
    accent-color: #e55933;
    cursor: pointer;
    height: 6px;
    border-radius: 4px;
    background: #e2e8f0;
  }
  .apple-num-input {
    width: 82px;
    padding: 8px 10px;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 700;
    color: #0f172a;
    text-align: center;
    outline: none;
    transition: border-color 0.2s;
  }
  .apple-num-input:focus { border-color: #e55933; box-shadow: 0 0 0 3px rgba(229,89,51,0.15); }

  .apple-calc-results {
    padding: 36px;
    background: #fbfcfe;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 24px;
  }

  /* VISUAL CIRCUIT SIMULATOR */
  .calc-circuit-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
  }
  .calc-circuit-title {
    font-size: 11.5px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #64748b;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .circuit-status-badge {
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
  }
  .circuit-diagram {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 0;
    overflow-x: auto;
  }
  .circuit-node {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    flex-shrink: 0;
  }
  .circuit-node-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: #0f172a;
    color: #ffffff;
    display: grid;
    place-items: center;
    font-size: 11px;
    font-weight: 800;
  }
  .circuit-node-label {
    font-size: 11px;
    font-weight: 700;
    color: #475569;
  }
  .circuit-node-val {
    font-size: 11.5px;
    font-weight: 800;
    color: #e55933;
    font-family: 'Outfit', sans-serif;
  }
  .circuit-line {
    flex: 1;
    min-width: 45px;
    height: 3px;
    background: #cbd5e1;
    position: relative;
    border-radius: 2px;
  }
  .circuit-line.led-strip {
    height: 8px;
    background: linear-gradient(90deg, #ffedd5 0%, #fed7aa 100%);
    border: 1px solid #fdba74;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: space-around;
    padding: 0 4px;
  }
  .led-dot {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #e55933;
    box-shadow: 0 0 4px #e55933;
  }

  .calc-metric-cards {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  @media (max-width: 550px) {
    .calc-metric-cards { grid-template-columns: 1fr; }
  }
  .metric-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 16px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
  }
  .metric-card.hero-metric {
    grid-column: 1 / -1;
    background: linear-gradient(135deg, #ffffff 0%, #fffbf9 100%);
    border: 2px solid #e55933;
    box-shadow: 0 10px 25px -5px rgba(229, 89, 51, 0.15);
  }
  .metric-label {
    font-size: 12px;
    color: #64748b;
    display: block;
    margin-bottom: 4px;
    font-weight: 600;
  }
  .metric-card.hero-metric .metric-label {
    color: #e55933;
    font-weight: 800;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
  }
  .metric-val {
    font-family: 'Outfit', sans-serif;
    font-size: 24px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.2;
  }
  .metric-card.hero-metric .metric-val {
    font-size: 32px;
    color: #e55933;
  }

  /* LOAD BAR */
  .calc-load-bar-wrap {
    margin-top: 14px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px 16px;
  }
  .calc-load-info {
    display: flex;
    justify-content: space-between;
    font-size: 12.5px;
    color: #64748b;
    margin-bottom: 8px;
    font-weight: 600;
  }
  .calc-progress-track {
    height: 8px;
    background: #f1f5f9;
    border-radius: 999px;
    overflow: hidden;
  }
  .calc-progress-fill {
    height: 100%;
    width: 60%;
    background: #10b981;
    border-radius: 999px;
    transition: width 0.3s ease, background-color 0.3s ease;
  }

  /* RECOMMENDATION CARD */
  .calc-rec-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 22px 24px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.04);
  }
  .calc-rec-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #166534;
    background: #dcfce7;
    padding: 4px 10px;
    border-radius: 6px;
    margin-bottom: 10px;
  }
  .calc-rec-title {
    font-family: 'Outfit', sans-serif;
    font-size: 18px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 8px;
  }
  .calc-rec-desc {
    font-size: 13.5px;
    color: #475569;
    line-height: 1.6;
    margin-bottom: 16px;
  }
  .calc-rec-btn {
    width: 100%;
    justify-content: center;
    padding: 13px 20px;
    font-weight: 700;
    font-size: 14px;
  }
"""

CALC_HTML = """  <!-- 2. APPLE-GRADE LIGHT CALCULATOR SECTION (PONIŻEJ BLOGA) -->
  <section id="kalkulator-led" class="apple-calc-card">
    <div class="apple-calc-header">
      <div>
        <h2>Kalkulator Doboru Zasilacza &amp; Spadków Napięć</h2>
        <p>Wybierz parametry taśmy i instalacji — dobierzemy właściwy zasilacz z bezpieczną rezerwą mocy.</p>
      </div>
      <div class="apple-calc-badge">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
        Laboratorium Prescot LED
      </div>
    </div>

    <!-- PRESETS BAR -->
    <div class="calc-presets-bar">
      <span class="calc-preset-label">Gotowe scenariusze:</span>
      <button type="button" class="calc-preset-btn" onclick="applyCalcPreset('salon')">🏠 Sufit w salonie (10m 24V)</button>
      <button type="button" class="calc-preset-btn" onclick="applyCalcPreset('kuchnia')">🍳 Blat kuchenny (3m 24V)</button>
      <button type="button" class="calc-preset-btn" onclick="applyCalcPreset('wneka')">🛋️ Wnęka LED (5m 12V)</button>
      <button type="button" class="calc-preset-btn" onclick="applyCalcPreset('cob')">✨ Linia COB Premium (8m 24V)</button>
    </div>

    <div class="apple-calc-body">
      <!-- CONFIGURATION PANEL -->
      <div class="apple-calc-config">
        <!-- 1. Voltage -->
        <div class="calc-field-group">
          <div class="calc-field-header">
            <span class="calc-field-label">Napięcie instalacji</span>
            <span class="calc-field-val-display" id="disp-voltage">24V DC</span>
          </div>
          <div class="apple-segmented" id="seg-voltage">
            <button type="button" class="apple-seg-btn" data-val="12">12V DC</button>
            <button type="button" class="apple-seg-btn active" data-val="24">24V DC (Zalecane)</button>
            <button type="button" class="apple-seg-btn" data-val="48">48V DC</button>
          </div>
        </div>

        <!-- 2. Power per meter -->
        <div class="calc-field-group">
          <div class="calc-field-header">
            <span class="calc-field-label">Moc taśmy LED na 1 metr</span>
            <span class="calc-field-val-display" id="disp-power">14.4 W/m</span>
          </div>
          <div class="apple-chip-grid" id="grid-power">
            <button type="button" class="apple-chip-btn" data-val="4.8">4.8 W/m</button>
            <button type="button" class="apple-chip-btn" data-val="9.6">9.6 W/m</button>
            <button type="button" class="apple-chip-btn active" data-val="14.4">14.4 W/m</button>
            <button type="button" class="apple-chip-btn" data-val="19.2">19.2 W/m</button>
            <button type="button" class="apple-chip-btn" data-val="24.0">24.0 W/m</button>
          </div>
        </div>

        <!-- 3. LED Length -->
        <div class="calc-field-group">
          <div class="calc-field-header">
            <span class="calc-field-label">Długość odcinka taśmy LED</span>
            <span class="calc-field-val-display" id="disp-length">6.0 m</span>
          </div>
          <div class="apple-slider-wrap">
            <input type="range" class="apple-range-slider" id="slider-length" min="0.5" max="50" step="0.5" value="6.0">
            <input type="number" class="apple-num-input" id="num-length" min="0.5" max="100" step="0.5" value="6.0">
          </div>
        </div>

        <!-- 4. Cable Distance -->
        <div class="calc-field-group">
          <div class="calc-field-header">
            <span class="calc-field-label">Długość kabla (Zasilacz &rarr; Taśma)</span>
            <span class="calc-field-val-display" id="disp-cable">3.0 m</span>
          </div>
          <div class="apple-slider-wrap">
            <input type="range" class="apple-range-slider" id="slider-cable" min="0.5" max="40" step="0.5" value="3.0">
            <input type="number" class="apple-num-input" id="num-cable" min="0.5" max="50" step="0.5" value="3.0">
          </div>
        </div>

        <!-- 5. Wire Cross-section -->
        <div class="calc-field-group">
          <div class="calc-field-header">
            <span class="calc-field-label">Przekrój żyły przewodu</span>
            <span class="calc-field-val-display" id="disp-wire">0.75 mm²</span>
          </div>
          <div class="apple-chip-grid" id="grid-wire">
            <button type="button" class="apple-chip-btn" data-val="0.5">0.50 mm²</button>
            <button type="button" class="apple-chip-btn active" data-val="0.75">0.75 mm²</button>
            <button type="button" class="apple-chip-btn" data-val="1.0">1.00 mm²</button>
            <button type="button" class="apple-chip-btn" data-val="1.5">1.50 mm²</button>
            <button type="button" class="apple-chip-btn" data-val="2.5">2.50 mm²</button>
          </div>
        </div>
      </div>

      <!-- RESULTS & TELEMETRY PANEL -->
      <div class="apple-calc-results">
        <div>
          <!-- VISUAL CIRCUIT SIMULATOR -->
          <div class="calc-circuit-box">
            <div class="calc-circuit-title">
              <span>Wizualizacja instalacji &amp; spadku napięcia</span>
              <span class="circuit-status-badge" id="circuit-badge" style="background:#dcfce7; color:#166534;">Stan idealny (&lt;3%)</span>
            </div>
            <div class="circuit-diagram">
              <div class="circuit-node">
                <div class="circuit-node-icon" id="circ-psu-box">PSU</div>
                <span class="circuit-node-label">Zasilacz</span>
                <span class="circuit-node-val" id="circ-psu-val">24.0V</span>
              </div>
              <div class="circuit-line" title="Kabel zasilający"></div>
              <div class="circuit-node">
                <div class="circuit-node-icon" style="background:#e55933;">LED</div>
                <span class="circuit-node-label">Start taśmy</span>
                <span class="circuit-node-val" id="circ-start-val">23.8V</span>
              </div>
              <div class="circuit-line led-strip" title="Taśma LED">
                <div class="led-dot"></div>
                <div class="led-dot"></div>
                <div class="led-dot"></div>
                <div class="led-dot"></div>
              </div>
              <div class="circuit-node">
                <div class="circuit-node-icon" style="background:#64748b;">END</div>
                <span class="circuit-node-label">Koniec</span>
                <span class="circuit-node-val" id="circ-end-val">23.4V</span>
              </div>
            </div>
          </div>

          <div class="calc-metric-cards" style="margin-top: 16px;">
            <!-- Hero Metric: Recommended PSU -->
            <div class="metric-card hero-metric">
              <span class="metric-label">Zalecana moc zasilacza (+20% rezerwy):</span>
              <div class="metric-val" id="res-psu-val">104 W</div>
            </div>

            <!-- Metric 1: Nominal LED power -->
            <div class="metric-card">
              <span class="metric-label">Moc znamionowa LED:</span>
              <div class="metric-val" id="res-power-val">86.4 W</div>
            </div>

            <!-- Metric 2: Circuit Current -->
            <div class="metric-card">
              <span class="metric-label">Prąd roboczy obwodu:</span>
              <div class="metric-val" id="res-current-val">3.60 A</div>
            </div>

            <!-- Metric 3: Voltage Drop -->
            <div class="metric-card">
              <span class="metric-label">Spadek na kablu:</span>
              <div class="metric-val" id="res-drop-val">0.34 V</div>
            </div>

            <!-- Metric 4: Loss percent -->
            <div class="metric-card">
              <span class="metric-label">Względna strata napięcia:</span>
              <div class="metric-val" id="res-loss-val">1.4%</div>
            </div>
          </div>

          <!-- Live Power Load Bar -->
          <div class="calc-load-bar-wrap">
            <div class="calc-load-info">
              <span>Współczynnik obciążenia wybranego zasilacza</span>
              <span id="res-load-pct" style="color:#0f172a; font-weight:700;">83% (Optymalny punkt)</span>
            </div>
            <div class="calc-progress-track">
              <div class="calc-progress-fill" id="res-load-bar"></div>
            </div>
          </div>
        </div>

        <!-- Recommendation Box -->
        <div class="calc-rec-card">
          <div class="calc-rec-tag">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            Dobrany model z magazynu Prescot
          </div>
          <div class="calc-rec-title" id="rec-psu-name">Zasilacz Prescot Ultra Slim 150W 24V</div>
          <p class="calc-rec-desc" id="rec-psu-text">Idealnie dobrana moc z 20% bezpiecznego zapasu. Zasilacz nie będzie się przegrzewał, ma zabezpieczenia przed zwarciem i posłuży na lata.</p>
          <a href="https://www.prescot.com.pl/pl/searchquery/zasilacz+150W+24V/1/phot/5?url=zasilacz+150W+24V" id="rec-psu-link" target="_blank" rel="noopener" class="p-btn p-btn-primary calc-rec-btn">
            Kup zasilacz 150W w sklepie fabrycznym &rarr;
          </a>
        </div>
      </div>
    </div>
  </section>
"""

CALC_JS = """// APPLE-GRADE PRESCOT LED CALCULATOR CONTROLLER (UPGRADED 2026)
var state = {
  voltage: 24,
  powerPerM: 14.4,
  length: 6.0,
  cable: 3.0,
  wire: 0.75
};

function applyCalcPreset(type) {
  if (type === 'salon') {
    state = { voltage: 24, powerPerM: 14.4, length: 10.0, cable: 4.0, wire: 1.0 };
  } else if (type === 'kuchnia') {
    state = { voltage: 24, powerPerM: 9.6, length: 3.0, cable: 2.0, wire: 0.75 };
  } else if (type === 'wneka') {
    state = { voltage: 12, powerPerM: 4.8, length: 5.0, cable: 2.5, wire: 0.75 };
  } else if (type === 'cob') {
    state = { voltage: 24, powerPerM: 19.2, length: 8.0, cable: 3.0, wire: 1.5 };
  }
  syncControlsFromState();
  updateCalculator();
}

function syncControlsFromState() {
  // Voltage buttons
  document.querySelectorAll('#seg-voltage .apple-seg-btn').forEach(function(b) {
    b.classList.toggle('active', parseFloat(b.dataset.val) === state.voltage);
  });
  // Power buttons
  document.querySelectorAll('#grid-power .apple-chip-btn').forEach(function(b) {
    b.classList.toggle('active', parseFloat(b.dataset.val) === state.powerPerM);
  });
  // Length slider & input
  var sL = document.getElementById('slider-length');
  var nL = document.getElementById('num-length');
  if (sL && nL) { sL.value = state.length; nL.value = state.length; }
  // Cable slider & input
  var sC = document.getElementById('slider-cable');
  var nC = document.getElementById('num-cable');
  if (sC && nC) { sC.value = state.cable; nC.value = state.cable; }
  // Wire buttons
  document.querySelectorAll('#grid-wire .apple-chip-btn').forEach(function(b) {
    b.classList.toggle('active', parseFloat(b.dataset.val) === state.wire);
  });
}

function updateCalculator() {
  var nominalPower = state.powerPerM * state.length;
  var recommendedPsu = nominalPower * 1.20;
  var current = nominalPower / state.voltage;

  var wireResistance = (0.0175 * state.cable * 2) / state.wire;
  var cableDrop = current * wireResistance;
  
  // Approximate internal PCB strip drop
  var stripDrop = (current * 0.5 * (state.length * 0.04));
  var totalDrop = cableDrop + stripDrop;
  var lossPct = (totalDrop / state.voltage) * 100;

  var psuOptions = [35, 60, 100, 150, 200, 250, 300, 400, 600];
  var matchedPsu = 600;
  for (var i = 0; i < psuOptions.length; i++) {
    if (psuOptions[i] >= recommendedPsu) {
      matchedPsu = psuOptions[i];
      break;
    }
  }

  var loadPct = Math.round((nominalPower / matchedPsu) * 100);

  // Update displays
  document.getElementById('disp-voltage').textContent = state.voltage + 'V DC';
  document.getElementById('disp-power').textContent = state.powerPerM + ' W/m';
  document.getElementById('disp-length').textContent = state.length.toFixed(1) + ' m';
  document.getElementById('disp-cable').textContent = state.cable.toFixed(1) + ' m';
  document.getElementById('disp-wire').textContent = state.wire.toFixed(2) + ' mm²';

  document.getElementById('res-psu-val').textContent = Math.ceil(recommendedPsu) + ' W';
  document.getElementById('res-power-val').textContent = nominalPower.toFixed(1) + ' W';
  document.getElementById('res-current-val').textContent = current.toFixed(2) + ' A';
  document.getElementById('res-drop-val').textContent = cableDrop.toFixed(2) + ' V';
  document.getElementById('res-loss-val').textContent = lossPct.toFixed(1) + '%';

  // Circuit simulator telemetry
  var vStart = Math.max(0, state.voltage - cableDrop);
  var vEnd = Math.max(0, state.voltage - totalDrop);
  document.getElementById('circ-psu-val').textContent = state.voltage.toFixed(1) + 'V';
  document.getElementById('circ-start-val').textContent = vStart.toFixed(2) + 'V';
  document.getElementById('circ-end-val').textContent = vEnd.toFixed(2) + 'V';

  var badge = document.getElementById('circuit-badge');
  if (lossPct <= 3.0) {
    badge.textContent = 'Stan idealny (<3% straty)';
    badge.style.background = '#dcfce7';
    badge.style.color = '#166534';
  } else if (lossPct <= 5.0) {
    badge.textContent = 'Dopuszczalny (3-5% straty)';
    badge.style.background = '#fef3c7';
    badge.style.color = '#92400e';
  } else {
    badge.textContent = 'Duży spadek (>5%) - Zasil obustronnie!';
    badge.style.background = '#fee2e2';
    badge.style.color = '#991b1b';
  }

  // Load bar
  document.getElementById('res-load-pct').textContent = loadPct + '% obciążenia (' + matchedPsu + 'W)';
  document.getElementById('res-load-bar').style.width = Math.min(100, loadPct) + '%';
  if (loadPct > 90) {
    document.getElementById('res-load-bar').style.background = '#ef4444';
  } else if (loadPct > 80) {
    document.getElementById('res-load-bar').style.background = '#e55933';
  } else {
    document.getElementById('res-load-bar').style.background = '#10b981';
  }

  // Recommendation text
  var modelName = 'Zasilacz Prescot Ultra Slim ' + matchedPsu + 'W ' + state.voltage + 'V DC';
  document.getElementById('rec-psu-name').textContent = modelName;

  var advice = 'Idealnie dobrana moc z 20% bezpieczną rezerwą. Zasilacz nie przegrzewa się, posiada certyfikaty CE/EMC i zabezpieczenia zwarciowo-przeciążeniowe. ';
  if (state.voltage === 12 && state.length > 5) {
    advice += 'Ważne: przy taśmie 12V i długości ' + state.length.toFixed(1) + 'm zalecamy doprowadzenie zasilania z obu końców taśmy, aby uniknąć przyciemnienia na końcu.';
  } else if (lossPct > 4.0) {
    advice += 'Wskazówka: przy kablu ' + state.cable.toFixed(1) + 'm sugerujemy zwiększyć przekrój do ' + (state.wire < 1.0 ? '1.00 mm²' : '1.50 mm²') + ', co zredukuje straty do minimum.';
  } else {
    advice += 'Twój odcinek ' + state.length.toFixed(1) + 'm możesz bez problemu zasilić jednostronnie.';
  }
  document.getElementById('rec-psu-text').textContent = advice;

  var query = encodeURIComponent('zasilacz ' + matchedPsu + 'W ' + state.voltage + 'V');
  var searchUrl = 'https://www.prescot.com.pl/pl/searchquery/' + query + '/1/phot/5?url=' + query;
  var btnLink = document.getElementById('rec-psu-link');
  if (btnLink) {
    btnLink.href = searchUrl;
    btnLink.innerHTML = 'Kup zasilacz ' + matchedPsu + 'W w sklepie fabrycznym &rarr;';
  }
}

// 1. Voltage Segments
document.querySelectorAll('#seg-voltage .apple-seg-btn').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('#seg-voltage .apple-seg-btn').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    state.voltage = parseFloat(btn.dataset.val);
    updateCalculator();
  });
});

// 2. Power Chips
document.querySelectorAll('#grid-power .apple-chip-btn').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('#grid-power .apple-chip-btn').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    state.powerPerM = parseFloat(btn.dataset.val);
    updateCalculator();
  });
});

// 3. LED Length
var sLen = document.getElementById('slider-length');
var nLen = document.getElementById('num-length');
if (sLen && nLen) {
  sLen.addEventListener('input', function() {
    state.length = Math.max(0.5, parseFloat(sLen.value) || 0.5);
    nLen.value = state.length;
    updateCalculator();
  });
  nLen.addEventListener('input', function() {
    state.length = Math.max(0.5, parseFloat(nLen.value) || 0.5);
    sLen.value = Math.min(50, state.length);
    updateCalculator();
  });
}

// 4. Cable Distance
var sCab = document.getElementById('slider-cable');
var nCab = document.getElementById('num-cable');
if (sCab && nCab) {
  sCab.addEventListener('input', function() {
    state.cable = Math.max(0.5, parseFloat(sCab.value) || 0.5);
    nCab.value = state.cable;
    updateCalculator();
  });
  nCab.addEventListener('input', function() {
    state.cable = Math.max(0.5, parseFloat(nCab.value) || 0.5);
    sCab.value = Math.min(40, state.cable);
    updateCalculator();
  });
}

// 5. Wire cross-section Chips
document.querySelectorAll('#grid-wire .apple-chip-btn').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('#grid-wire .apple-chip-btn').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    state.wire = parseFloat(btn.dataset.val);
    updateCalculator();
  });
});

// Initial run
updateCalculator();
"""

FILES = [
    "/Users/karolbohdanowicz/safe_backup/tasmaled-local/public/baza-wiedzy/index.html",
    "/Users/karolbohdanowicz/safe_backup/tasmaled-local/public/wiedza.html",
    "/Users/karolbohdanowicz/safe_backup/tasmaled-local/public/wiedza/index.html",
    "/Users/karolbohdanowicz/safe_backup/prescotpl/wiedza.html",
    "/Users/karolbohdanowicz/safe_backup/prescotpl/wiedza/index.html"
]

def update_file(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Replace CSS
    css_pattern = re.compile(r'/\* =+ \s* APPLE-GRADE LIGHT & CLEAN CALCULATOR.*?\*/.*?(?=\.faq-item|\.p-card|\.p-breadcrumbs|\n\s*</style>)', re.DOTALL | re.VERBOSE)
    if css_pattern.search(html):
        html = css_pattern.sub(CALC_CSS, html)
        print(f"Updated CSS in {path}")
    else:
        # append before </style>
        html = html.replace("</style>", CALC_CSS + "\n</style>", 1)
        print(f"Appended CSS in {path}")

    # 2. Replace HTML section
    html_pattern = re.compile(r'<!-- 2\. APPLE-GRADE LIGHT CALCULATOR SECTION.*?<!-- 3\. FAQ ACCORDION SECTION', re.DOTALL)
    if html_pattern.search(html):
        html = html_pattern.sub(CALC_HTML + "\n  <!-- 3. FAQ ACCORDION SECTION", html)
        print(f"Updated HTML in {path}")

    # 3. Replace JS controller
    js_pattern = re.compile(r'// APPLE-GRADE PRESCOT LED CALCULATOR CONTROLLER.*?(?=</script>|\Z)', re.DOTALL)
    if js_pattern.search(html):
        html = js_pattern.sub(CALC_JS + "\n", html)
        print(f"Updated JS in {path}")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Saved {path}\n")

for f in FILES:
    update_file(f)
