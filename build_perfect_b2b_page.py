#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tworzy ultranowoczesną, nastawioną w 100% na konwersję i pozyskiwanie partnerów
podstronę Współpraca B2B dla Prescot LED:
- Eliminacja nachalnego formularza logowania z góry strony.
- Potężny hero section z jasnymi korzyściami biznesowymi (rabaty do 45%, wysyłka 24h, 7 lat gwarancji, darmowe wzorniki).
- 4 dedykowane filary współpracy: Instalatorzy, Hurtownie, Architekci, Producenci mebli.
- Sekcja z autentycznymi zdjęciami i kontaktami do handlowców Prescot z prescot.pl.
- Błyskawiczny, nowoczesny formularz zgłoszeniowy B2B z honeypotem.
- Dyskretny link dla obecnych klientów do platformy AB-Store.
- Baza pytań i odpowiedzi FAQ B2B.
"""

import os

HTML_CONTENT = """<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="icon" href="/wp-content/uploads/2025/09/cropped-favicon-1-32x32.png" sizes="32x32">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&family=Krona+One&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/prescot-global.css?v=20260902-b2b-v9">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
  
  <title>Współpraca B2B &amp; Program Partnerski — Prescot LED</title>
  <meta name="description" content="Dołącz do sieci partnerskiej Prescot LED. Oferta fabryczna dla Hurtowni, Instalatorów, Architektów i Producentów Mebli: rabaty hurtowe do 45%, magazyn w Giżycku, wysyłka w 24h i darmowy pakiet próbek.">
  <meta name="keywords" content="współpraca b2b led, hurtownia led, dystrybutor oświetlenia led, producent taśm led, rabaty dla instalatorów, próbki taśm cob, zasilacze ultra slim hurt, prescot giżycko">

  <style>
  :root {
    --p-primary: #e55933;
    --p-primary-hover: #c94622;
    --p-dark: #0f172a;
    --p-dark-soft: #1e293b;
    --p-text: #212a35;
    --p-text-muted: #64748b;
    --p-bg: #f8fafc;
    --p-card: #ffffff;
    --p-border: #e2e8f0;
    --p-radius: 20px;
    --p-radius-sm: 12px;
    --p-shadow-sm: 0 2px 8px rgba(0,0,0,0.04);
    --p-shadow-md: 0 12px 30px -10px rgba(0,0,0,0.08);
    --p-shadow-lg: 0 20px 45px -12px rgba(15,23,42,0.12);
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body {
    font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--p-text);
    background: var(--p-bg);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    padding-bottom: 90px;
  }

  /* 100VH LUXURY HERO */
  .p-full-hero {
    position: relative;
    width: 100%;
    min-height: 100vh;
    height: 100vh;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 80px 24px 70px 24px;
    color: #ffffff;
    overflow: hidden;
  }
  .p-full-hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.72) 0%, rgba(15, 23, 42, 0.90) 100%);
    z-index: 1;
  }
  .p-full-hero-content {
    position: relative;
    z-index: 2;
    max-width: 980px;
    margin: auto;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .p-hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(229, 89, 51, 0.22);
    color: #ff8a65;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    padding: 8px 20px;
    border-radius: 30px;
    margin-bottom: 22px;
    border: 1px solid rgba(229, 89, 51, 0.4);
    backdrop-filter: blur(8px);
  }
  .p-full-hero h1 {
    font-family: 'Outfit', sans-serif;
    font-size: clamp(34px, 4.8vw, 56px);
    color: #ffffff;
    margin-bottom: 20px;
    line-height: 1.15;
    font-weight: 800;
    text-shadow: 0 2px 10px rgba(0,0,0,0.4);
  }
  .p-full-hero p.lead {
    font-size: clamp(16px, 1.9vw, 20px);
    color: #e2e8f0;
    max-width: 860px;
    line-height: 1.65;
    margin-bottom: 34px;
    text-shadow: 0 1px 4px rgba(0,0,0,0.4);
  }

  /* HERO TRUST PILLS */
  .hero-trust-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    width: 100%;
    max-width: 880px;
    margin-bottom: 34px;
  }
  .hero-trust-pill {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.16);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    text-align: left;
    color: #ffffff;
    font-size: 13px;
    font-weight: 600;
  }
  .hero-trust-icon {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: rgba(229, 89, 51, 0.3);
    color: #ff8a65;
    display: grid;
    place-items: center;
    flex-shrink: 0;
  }

  .p-hero-actions {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    justify-content: center;
  }
  .p-hero-arrow-down {
    position: absolute;
    bottom: 28px;
    left: 50%;
    transform: translateX(-50%);
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.25);
    color: #ffffff;
    display: grid;
    place-items: center;
    text-decoration: none;
    z-index: 2;
    transition: all 0.25s ease;
    backdrop-filter: blur(6px);
  }
  .p-hero-arrow-down:hover {
    background: var(--p-primary);
    border-color: var(--p-primary);
    transform: translateX(-50%) translateY(4px);
  }

  /* BUTTONS */
  .p-btn {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 14px 28px;
    border-radius: 999px;
    font-size: 15px;
    font-weight: 700;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    border: none;
    font-family: inherit;
  }
  .p-btn-primary {
    background: var(--p-primary);
    color: #ffffff;
    box-shadow: 0 8px 24px rgba(229, 89, 51, 0.35);
  }
  .p-btn-primary:hover {
    background: var(--p-primary-hover);
    transform: translateY(-2px);
    box-shadow: 0 12px 30px rgba(229, 89, 51, 0.45);
  }
  .p-btn-outline {
    background: rgba(255, 255, 255, 0.1);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(6px);
  }
  .p-btn-outline:hover {
    background: rgba(255, 255, 255, 0.22);
    border-color: #ffffff;
    transform: translateY(-2px);
  }

  /* MAIN CONTAINER */
  .prescot-main-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 24px;
  }
  .prescot-breadcrumbs {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13.5px;
    color: var(--p-text-muted);
    margin-bottom: 36px;
  }
  .prescot-breadcrumbs a {
    color: var(--p-text-muted);
    text-decoration: none;
    transition: color 0.2s;
  }
  .prescot-breadcrumbs a:hover { color: var(--p-primary); }
  .prescot-breadcrumbs .sep { opacity: 0.5; }

  /* 4 TARGET AUDIENCES (FILARY WSPÓŁPRACY) */
  .p-pillars-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 24px;
    margin-bottom: 60px;
  }
  .p-pillar-card {
    background: #ffffff;
    border: 1px solid var(--p-border);
    border-radius: var(--p-radius);
    padding: 30px 26px;
    box-shadow: var(--p-shadow-sm);
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
  }
  .p-pillar-card:hover {
    transform: translateY(-6px);
    box-shadow: var(--p-shadow-md);
    border-color: #cbd5e1;
  }
  .p-pillar-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 16px;
  }
  .p-pillar-icon {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    background: #fff5f2;
    color: var(--p-primary);
    display: grid;
    place-items: center;
    flex-shrink: 0;
  }
  .p-pillar-title {
    font-family: 'Outfit', sans-serif;
    font-size: 18px;
    font-weight: 800;
    color: var(--p-dark);
  }
  .p-pillar-list {
    list-style: none;
    margin-top: 12px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    font-size: 13.5px;
    color: #475569;
  }
  .p-pillar-list li {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    line-height: 1.5;
  }
  .p-pillar-list li svg {
    flex-shrink: 0;
    margin-top: 3px;
    color: #10b981;
  }

  /* 6 BENEFITS TILES */
  .p-benefits-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 20px;
    margin-bottom: 60px;
  }
  .p-benefit-card {
    background: #ffffff;
    border: 1px solid var(--p-border);
    border-radius: 16px;
    padding: 24px 26px;
    box-shadow: var(--p-shadow-sm);
    display: flex;
    gap: 18px;
    align-items: flex-start;
    transition: all 0.25s ease;
  }
  .p-benefit-card:hover {
    border-color: #cbd5e1;
    transform: translateY(-3px);
    box-shadow: var(--p-shadow-md);
  }
  .p-benefit-icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: #0f172a;
    color: #ffffff;
    display: grid;
    place-items: center;
    flex-shrink: 0;
  }
  .p-benefit-body h4 {
    font-family: 'Outfit', sans-serif;
    font-size: 16.5px;
    font-weight: 700;
    color: var(--p-dark);
    margin-bottom: 6px;
  }
  .p-benefit-body p {
    font-size: 13.5px;
    color: var(--p-text-muted);
    line-height: 1.55;
  }

  /* SECTION HANDLOWCY (SALES TEAM PRESCOT) */
  .team-section-card {
    background: #ffffff;
    border: 1px solid var(--p-border);
    border-radius: var(--p-radius);
    padding: 40px;
    box-shadow: var(--p-shadow-sm);
    margin-bottom: 60px;
  }
  .team-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 24px;
    margin-top: 30px;
  }
  .team-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 24px 20px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    transition: all 0.25s ease;
  }
  .team-card:hover {
    background: #ffffff;
    border-color: var(--p-primary);
    transform: translateY(-4px);
    box-shadow: var(--p-shadow-md);
  }
  .team-avatar-wrap {
    width: 96px;
    height: 96px;
    border-radius: 50%;
    overflow: hidden;
    margin-bottom: 16px;
    border: 3px solid #ffffff;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    background: #e2e8f0;
  }
  .team-avatar-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .team-name {
    font-family: 'Outfit', sans-serif;
    font-size: 17px;
    font-weight: 800;
    color: var(--p-dark);
    margin-bottom: 4px;
  }
  .team-role {
    font-size: 12.5px;
    font-weight: 600;
    color: var(--p-primary);
    margin-bottom: 14px;
  }
  .team-contact-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 100%;
    border-top: 1px solid #e2e8f0;
    padding-top: 12px;
  }
  .team-contact-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 7px 12px;
    border-radius: 8px;
    font-size: 12.5px;
    font-weight: 600;
    text-decoration: none;
    color: #334155;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    transition: all 0.2s;
  }
  .team-contact-btn:hover {
    border-color: var(--p-primary);
    color: var(--p-primary);
    background: #fff5f2;
  }

  /* B2B REGISTRATION FORM SECTION (LUXURY CARD) */
  .b2b-form-section {
    background: linear-gradient(135deg, #ffffff 0%, #fffbf9 100%);
    border: 2px solid #e55933;
    border-radius: 24px;
    padding: 44px;
    box-shadow: 0 20px 45px -12px rgba(229, 89, 51, 0.15);
    margin-bottom: 60px;
  }
  @media (max-width: 768px) {
    .b2b-form-section { padding: 26px 20px; }
  }
  .b2b-form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
    margin-top: 24px;
  }
  @media (max-width: 768px) {
    .b2b-form-grid { grid-template-columns: 1fr; }
  }
  .b2b-field-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .b2b-field-group.full {
    grid-column: 1 / -1;
  }
  .b2b-field-group label {
    font-size: 13px;
    font-weight: 700;
    color: var(--p-dark);
  }
  .b2b-field-group input,
  .b2b-field-group select,
  .b2b-field-group textarea {
    padding: 13px 16px;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    font-size: 14px;
    font-family: inherit;
    color: var(--p-dark);
    background: #ffffff;
    outline: none;
    transition: all 0.2s;
  }
  .b2b-field-group input:focus,
  .b2b-field-group select:focus,
  .b2b-field-group textarea:focus {
    border-color: var(--p-primary);
    box-shadow: 0 0 0 3px rgba(229, 89, 51, 0.15);
  }
  .b2b-field-group textarea {
    min-height: 90px;
    resize: vertical;
  }

  /* DISCREET EXISTING PARTNERS BOX */
  .existing-partner-box {
    margin-top: 24px;
    padding: 18px 22px;
    background: #f8fafc;
    border: 1px dashed #cbd5e1;
    border-radius: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
  }
  .existing-partner-text {
    font-size: 13.5px;
    color: #475569;
  }
  .existing-partner-link {
    font-size: 13.5px;
    font-weight: 700;
    color: var(--p-primary);
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: gap 0.2s;
  }
  .existing-partner-link:hover { gap: 10px; text-decoration: underline; }

  /* FAQ ACCORDION */
  .faq-accordion-wrap {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 30px;
  }
  .faq-card {
    background: #ffffff;
    border: 1px solid var(--p-border);
    border-radius: 14px;
    padding: 20px 24px;
    cursor: pointer;
    transition: all 0.2s;
  }
  .faq-card:hover {
    border-color: #cbd5e1;
  }
  .faq-question {
    font-family: 'Outfit', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: var(--p-dark);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .faq-answer {
    margin-top: 10px;
    font-size: 14px;
    color: #475569;
    line-height: 1.6;
  }

  /* SMART LOGO */
  .prescot-smart-logo {
    position: absolute;
    top: 28px;
    left: 36px;
    z-index: 10;
  }
  .prescot-smart-logo img {
    height: 38px;
    width: auto;
  }
  @media (max-width: 768px) {
    .prescot-smart-logo { top: 20px; left: 20px; }
    .prescot-smart-logo img { height: 30px; }
  }
  </style>
</head>

<body>
<!-- SMART LOGO: TYLKO W SEKCJI HERO -->
<div class="prescot-smart-logo">
  <a href="/" title="Prescot LED Strona Główna">
    <img src="/wp-content/uploads/2025/12/biale-z-kolorem.svg" alt="Prescot LED">
  </a>
</div>

<!-- FULL-SCREEN 100VH HERO SLIDE -->
<section class="p-full-hero" style="background-image: url('/wp-content/uploads/2026/01/miasto-scharfer-1-scaled.jpg');">
  <div class="p-full-hero-content">
    <div class="p-hero-eyebrow">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7.5" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>
      Oficjalny Program Partnerski B2B
    </div>
    <h1>Zbuduj przewagę w oświetleniu LED z polskim producentem</h1>
    <p class="lead">Dedykowana oferta handlowa dla Hurtowni Elektrycznych, Elektroinstalatorów, Architektów oraz Producentów Mebli. Bezpośrednie ceny fabryczne, magazyn w Giżycku i realizacja zamówień w 24 godziny.</p>

    <!-- TRUST PILLS -->
    <div class="hero-trust-grid">
      <div class="hero-trust-pill">
        <div class="hero-trust-icon">%</div>
        <span>Do 45% rabatu hurtowego</span>
      </div>
      <div class="hero-trust-pill">
        <div class="hero-trust-icon">⚡</div>
        <span>Wysyłka w 24h z Giżycka</span>
      </div>
      <div class="hero-trust-pill">
        <div class="hero-trust-icon">🛡️</div>
        <span>5–7 lat gwarancji Door-to-Door</span>
      </div>
      <div class="hero-trust-pill">
        <div class="hero-trust-icon">📦</div>
        <span>Bezpłatne wzorniki i próbki</span>
      </div>
    </div>

    <div class="p-hero-actions">
      <a href="#dolacz-do-b2b" class="p-btn p-btn-primary">
        Dołącz do sieci B2B &amp; Odbierz rabaty
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </a>
      <a href="tel:+48877776482" class="p-btn p-btn-outline">
        Zadzwoń: +48 87 777 64 82
      </a>
    </div>
  </div>

  <a href="#content-start" class="p-hero-arrow-down" aria-label="Przewiń do treści">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M19 12l-7 7-7-7"/></svg>
  </a>
</section>

<!-- TREŚĆ PONIŻEJ HERO -->
<main id="content-start" class="prescot-main-container">
  <nav class="prescot-breadcrumbs" aria-label="Okruszki">
    <a href="/">Strona główna</a>
    <span class="sep">/</span>
    <span>Współpraca B2B</span>
  </nav>

  <!-- 1. DLA KOGO JEST PRESCOT - 4 FILARY WSPÓŁPRACY -->
  <section style="margin-bottom: 60px;">
    <div style="text-align:center; max-width:760px; margin:0 auto 36px auto;">
      <h2 style="font-family:'Outfit',sans-serif; font-size: clamp(26px, 3vw, 34px); color: var(--p-dark); margin-bottom: 10px;">Dedykowane warunki dla Twojej branży</h2>
      <p style="color: var(--p-text-muted); font-size: 15.5px;">Wiemy, że każda grupa partnerów ma inne priorytety na budowie i w handlu. Sprawdź, co przygotowaliśmy dla Twojego profilu działalności:</p>
    </div>

    <div class="p-pillars-grid">
      <!-- 1. INSTALATORZY -->
      <div class="p-pillar-card">
        <div class="p-pillar-header">
          <div class="p-pillar-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
          </div>
          <div>
            <div class="p-pillar-title">Elektroinstalatorzy</div>
            <small style="color:var(--p-text-muted);">i Wykonawcy LED</small>
          </div>
        </div>
        <p style="font-size:13.5px; color:#475569;">Pewność montażu, zero powrotów na poprawki i komponenty odporne na błędy instalacyjne.</p>
        <ul class="p-pillar-list">
          <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Podwójny podkład miedzi PCB 2oz/3oz (brak przegrzewania)</li>
          <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Szybkozłączki bez lutowania Hippo (oszczędność 70% czasu)</li>
          <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Zasilacze Ultra Slim mieszczące się w profilach</li>
          <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Wysyłka prosto na adres realizowanej budowy</li>
        </ul>
      </div>

      <!-- 2. HURTOWNIE -->
      <div class="p-pillar-card">
        <div class="p-pillar-header">
          <div class="p-pillar-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>
          </div>
          <div>
            <div class="p-pillar-title">Hurtownie &amp; Salony</div>
            <small style="color:var(--p-text-muted);">Elektrotechniczne</small>
          </div>
        </div>
        <p style="font-size:13.5px; color:#475569;">Wysoka rotacja, bezpieczna marża i pełne wsparcie w integracji systemów magazynowych.</p>
        <ul class="p-pillar-list">
          <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Pliki XML, CSV, pełna klasyfikacja ETIM 8.0/9.0</li>
          <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>98% katalogowych indeksów stale na stanie w Giżycku</li>
          <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Ekspozytory POS ze świecącymi próbkami do salonu</li>
          <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Ochrona marży i elastyczne limity kupieckie</li>
        </ul>
      </div>

      <!-- 3. ARCHITEKCI -->
      <div class="p-pillar-card">
        <div class="p-pillar-header">
          <div class="p-pillar-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.586 7.586"/><circle cx="11" cy="11" r="2"/></svg>
          </div>
          <div>
            <div class="p-pillar-title">Architekci &amp; Projektanci</div>
            <small style="color:var(--p-text-muted);">Wnętrz i Światła</small>
          </div>
        </div>
        <p style="font-size:13.5px; color:#475569;">Światło najwyższej wierności, jednolite linie bez kropek i pełne zaplecze projektowe.</p>
        <ul class="p-pillar-list">
          <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Pliki 3D oraz bryły fotometryczne IES do projektów</li>
          <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Taśmy TrueColor CRI&gt;95 oraz technologia COB Dotless</li>
          <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Bezpłatna weryfikacja techniczna i bilans mocy w 2h</li>
          <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Eleganckie próbniki do prezentacji inwestorom</li>
        </ul>
      </div>

      <!-- 4. MEBLARZE -->
      <div class="p-pillar-card">
        <div class="p-pillar-header">
          <div class="p-pillar-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3h18v18H3zM9 3v18M15 3v18M3 9h18M3 15h18"/></svg>
          </div>
          <div>
            <div class="p-pillar-title">Producenci Mebli</div>
            <small style="color:var(--p-text-muted);">i Zabudów na Wymiar</small>
          </div>
        </div>
        <p style="font-size:13.5px; color:#475569;">Komponenty konfekcjonowane pod seryjny montaż w warsztacie meblarskim.</p>
        <ul class="p-pillar-list">
          <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Taśmy LED 12V/24V docinane na dokładny wymiar</li>
          <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Profile meblowe Slim (4mm, 8mm, wpuszczane)</li>
          <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Miniaturowe włączniki bezdotykowe i czujniki PIR</li>
          <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>Pakowanie seryjne OEM pod Twoją markę</li>
        </ul>
      </div>
    </div>
  </section>

  <!-- 2. KORZYŚCI HANDLOWE (6 KAFELKÓW) -->
  <section style="margin-bottom: 60px;">
    <div style="text-align:center; max-width:720px; margin:0 auto 36px auto;">
      <h2 style="font-family:'Outfit',sans-serif; font-size: 28px; color: var(--p-dark); margin-bottom: 10px;">Dlaczego warto postawić na Prescot LED?</h2>
      <p style="color: var(--p-text-muted); font-size: 15px;">Dajemy Ci bezpośredni dostęp do polskiego producenta bez zbędnych pośredników.</p>
    </div>

    <div class="p-benefits-grid">
      <div class="p-benefit-card">
        <div class="p-benefit-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        </div>
        <div class="p-benefit-body">
          <h4>Ceny Prosto z Fabryki</h4>
          <p>Dedykowany cennik hurtowy z rabatami do 45% od cen katalogowych już od pierwszego zamówienia.</p>
        </div>
      </div>

      <div class="p-benefit-card">
        <div class="p-benefit-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>
        </div>
        <div class="p-benefit-body">
          <h4>Magazyn Giżycko — Wysyłka 24h</h4>
          <p>Zamówienia złożone do godziny 13:00 wysyłamy tego samego dnia kurierem DPD lub paletą Raben.</p>
        </div>
      </div>

      <div class="p-benefit-card">
        <div class="p-benefit-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <div class="p-benefit-body">
          <h4>Pewna Gwarancja Door-to-Door</h4>
          <p>5 do 7 lat gwarancji producenta. W razie wątpliwości wymieniamy sprzęt od ręki bez zbędnych przestojów.</p>
        </div>
      </div>

      <div class="p-benefit-card">
        <div class="p-benefit-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
        </div>
        <div class="p-benefit-body">
          <h4>Darmowy Pakiet Startowy Próbek</h4>
          <p>Dla zarejestrowanych firm wysyłamy bezpłatny zestaw demonstracyjny taśm COB, profili KLUŚ i złączek.</p>
        </div>
      </div>

      <div class="p-benefit-card">
        <div class="p-benefit-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
        </div>
        <div class="p-benefit-body">
          <h4>Wsparcie Inżyniera w 2 Godziny</h4>
          <p>Prześlij rzut lub koncepcję — nasz inżynier bezpłatnie dobierze zasilacze, sterowniki i przekroje kabli.</p>
        </div>
      </div>

      <div class="p-benefit-card">
        <div class="p-benefit-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        </div>
        <div class="p-benefit-body">
          <h4>Integracje XML, CSV &amp; ETIM</h4>
          <p>Błyskawiczne zasilenie Twojego sklepu internetowego lub systemu ERP aktualnymi cenami i stanami live.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- 3. DZIAŁ HANDLOWY PRESCOT — OPIEKUNOWIE B2B ZE ZDJĘCIAMI -->
  <section class="team-section-card">
    <div style="text-align:center; max-width:720px; margin:0 auto;">
      <span class="p-hero-eyebrow" style="font-size:11.5px; padding:5px 14px; margin-bottom:12px;">Ludzie, którzy znają Twój fach</span>
      <h2 style="font-family:'Outfit',sans-serif; font-size: 28px; color: var(--p-dark); margin-bottom: 8px;">Twój Dedykowany Zespół Handlowy</h2>
      <p style="color: var(--p-text-muted); font-size: 15px;">W Prescot nie rozmawiasz z anonimowym botem. Każdy partner B2B ma przypisanego osobistego opiekuna handlowego:</p>
    </div>

    <div class="team-grid">
      <!-- Adam Garbowski -->
      <div class="team-card">
        <div class="team-avatar-wrap">
          <img src="/wp-content/uploads/team/Adam-Garbowski.webp" alt="Adam Garbowski - Prescot LED" loading="lazy">
        </div>
        <div class="team-name">Adam Garbowski</div>
        <div class="team-role">Key Account Manager B2B</div>
        <div class="team-contact-list">
          <a href="tel:+48609428570" class="team-contact-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
            +48 609 428 570
          </a>
          <a href="mailto:adam.garbowski@prescot.pl" class="team-contact-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            adam.garbowski@prescot.pl
          </a>
        </div>
      </div>

      <!-- Iwona Baczewska -->
      <div class="team-card">
        <div class="team-avatar-wrap">
          <img src="/wp-content/uploads/team/Iwona-Baczewska.webp" alt="Iwona Baczewska - Prescot LED" loading="lazy">
        </div>
        <div class="team-name">Iwona Baczewska</div>
        <div class="team-role">Obsługa Klientów Hurtowych</div>
        <div class="team-contact-list">
          <a href="tel:+48720858005" class="team-contact-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
            +48 720 858 005
          </a>
          <a href="mailto:iwona.baczewska@prescot.pl" class="team-contact-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            iwona.baczewska@prescot.pl
          </a>
        </div>
      </div>

      <!-- Dariusz Nita -->
      <div class="team-card">
        <div class="team-avatar-wrap">
          <img src="/wp-content/uploads/team/Dariusz-Nita.webp" alt="Dariusz Nita - Prescot LED" loading="lazy">
        </div>
        <div class="team-name">Dariusz Nita</div>
        <div class="team-role">Wsparcie Inwestycji i Wykonawców</div>
        <div class="team-contact-list">
          <a href="tel:+48570123681" class="team-contact-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
            +48 570 123 681
          </a>
          <a href="mailto:dariusz.nita@prescot.pl" class="team-contact-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            dariusz.nita@prescot.pl
          </a>
        </div>
      </div>

      <!-- Anna Galor -->
      <div class="team-card">
        <div class="team-avatar-wrap">
          <img src="/wp-content/uploads/team/Anna-Galor.webp" alt="Anna Galor - Prescot LED" loading="lazy">
        </div>
        <div class="team-name">Anna Galor</div>
        <div class="team-role">Koordynator Zamówień B2B</div>
        <div class="team-contact-list">
          <a href="tel:+48730901909" class="team-contact-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
            +48 730 901 909
          </a>
          <a href="mailto:anna.galor@prescot.pl" class="team-contact-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            anna.galor@prescot.pl
          </a>
        </div>
      </div>
    </div>

    <!-- CENTRALNY KONTAKT B2B -->
    <div style="margin-top:28px; padding:16px 20px; background:#f1f5f9; border-radius:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
      <div style="font-size:13.5px; color:#334155;">
        <strong>Biuro Handlowe Giżycko:</strong> tel. <a href="tel:+48877776482" style="color:var(--p-primary); text-decoration:none; font-weight:700;">+48 87 777 64 82</a> | e-mail: <a href="mailto:komponenty@prescot.pl" style="color:var(--p-primary); text-decoration:none; font-weight:700;">komponenty@prescot.pl</a> (Pn–Pt 8:00–16:00)
      </div>
      <div style="font-size:12.5px; color:#64748b;">
        PRESCOT sp. z o.o., ul. Wileńska 1, 11-500 Giżycko
      </div>
    </div>
  </section>

  <!-- 4. SZYBKI FORMULARZ ZGŁOSZENIOWY B2B (GŁÓWNE CTA) -->
  <section class="b2b-form-section" id="dolacz-do-b2b">
    <div style="max-width: 780px; margin: 0 auto; text-align: center;">
      <span class="p-hero-eyebrow" style="font-size:12px; padding:6px 16px; margin-bottom:12px;">Rejestracja w 30 sekund</span>
      <h2 style="font-family:'Outfit',sans-serif; font-size: clamp(26px, 3.2vw, 36px); color: var(--p-dark); margin-bottom: 12px;">Zgłoś firmę do Programu Partnerskiego</h2>
      <p style="color: #475569; font-size: 15.5px; line-height: 1.6;">Wypełnij krótki formularz. Twój dedykowany opiekun handlowy aktywuje rabaty hurtowe i wyśle bezpłatny pakiet powitalny z próbkami:</p>
    </div>

    <form class="b2b-form-grid" id="b2b-reg-form" action="javascript:void(0);" novalidate style="max-width: 820px; margin: 28px auto 0 auto;">
      <!-- Honeypot -->
      <input type="text" name="b2b_hp" style="display:none;" tabindex="-1" autocomplete="off">

      <div class="b2b-field-group">
        <label for="b2b-nip">NIP Firmy *</label>
        <input type="text" id="b2b-nip" placeholder="np. 8451996500" maxlength="15" autocomplete="off" required>
      </div>

      <div class="b2b-field-group">
        <label for="b2b-company">Pełna nazwa firmy *</label>
        <input type="text" id="b2b-company" placeholder="np. Elektro-Instalacje Kowalski" maxlength="120" autocomplete="organization" required>
      </div>

      <div class="b2b-field-group">
        <label for="b2b-name">Osoba kontaktowa *</label>
        <input type="text" id="b2b-name" placeholder="Imię i nazwisko" maxlength="80" autocomplete="name" required>
      </div>

      <div class="b2b-field-group">
        <label for="b2b-email">Firmowy adres e-mail *</label>
        <input type="email" id="b2b-email" placeholder="biuro@twojafirma.pl" maxlength="100" autocomplete="email" required>
      </div>

      <div class="b2b-field-group">
        <label for="b2b-phone">Numer telefonu do kontaktu *</label>
        <input type="tel" id="b2b-phone" placeholder="+48 000 000 000" maxlength="20" autocomplete="tel" required>
      </div>

      <div class="b2b-field-group">
        <label for="b2b-type">Profil działalności</label>
        <select id="b2b-type">
          <option value="instalator" selected>Elektroinstalator / Wykonawca</option>
          <option value="hurtownia">Hurtownia Elektryczna / Salon</option>
          <option value="architekt">Architekt / Projektant Wnętrz</option>
          <option value="meble">Producent Mebli / Reklam</option>
          <option value="inwestor">Inwestor / Generalny Wykonawca</option>
        </select>
      </div>

      <div class="b2b-field-group full">
        <label for="b2b-msg">W czym możemy pomóc? (Opcjonalnie)</label>
        <textarea id="b2b-msg" placeholder="Podaj szacowane miesięczne zapotrzebowanie, najbliższy projekt lub poproś o bezpłatny zestaw próbek taśm COB..." maxlength="1000"></textarea>
      </div>

      <div class="b2b-field-group full">
        <label style="display:flex; align-items:flex-start; gap:10px; font-size:13px; color:#64748b; cursor:pointer;">
          <input type="checkbox" id="b2b-agree" required style="margin-top:3px; accent-color: var(--p-primary);" checked>
          <span>Wyrażam zgodę na kontakt ze strony PRESCOT sp. z o.o. w celu przedstawienia oferty handlowej, nadania rabatów B2B oraz wysyłki próbek.</span>
        </label>
      </div>

      <div class="b2b-field-group full" style="margin-top: 10px;">
        <button type="submit" class="p-btn p-btn-primary" style="width:100%; justify-content:center; padding:16px 30px; font-size:16px;">
          Wyślij zgłoszenie &amp; Odbierz rabat powitalny &rarr;
        </button>
      </div>

      <div id="b2b-feedback" class="b2b-field-group full" style="display:none; padding: 18px 24px; border-radius: 12px; font-size: 15px; background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; text-align: center;">
        <strong>Dziękujemy za zgłoszenie!</strong> Dział handlowy Prescot LED skontaktuje się z Tobą w ciągu max 2 godzin roboczych.
      </div>
    </form>

    <!-- DYSKRETNY LINK DLA OBECNYCH PARTNERÓW (ZAMIAST BRZYDKIEGO LOGOWANIA NA GÓRZE) -->
    <div class="existing-partner-box" style="max-width:820px; margin:28px auto 0 auto;">
      <div class="existing-partner-text">
        🔒 <strong>Masz już aktywne konto hurtowe?</strong> Nie musisz wypełniać formularza.
      </div>
      <a href="https://prescot.abstore.pl/client/loginorcreate/login" target="_blank" rel="noopener" class="existing-partner-link">
        Zaloguj się do platformy hurtowej AB-Store &rarr;
      </a>
    </div>
  </section>

  <!-- 5. FAQ DLA PARTNERÓW B2B -->
  <section style="margin-bottom: 60px;">
    <div style="text-align:center; max-width:720px; margin:0 auto 20px auto;">
      <h2 style="font-family:'Outfit',sans-serif; font-size: 26px; color: var(--p-dark); margin-bottom: 8px;">Często zadawane pytania (FAQ B2B)</h2>
      <p style="color: var(--p-text-muted); font-size: 14.5px;">Wszystko, co musisz wiedzieć przed rozpoczęciem współpracy handlowej:</p>
    </div>

    <div class="faq-accordion-wrap">
      <div class="faq-card">
        <div class="faq-question">
          <span>Jak szybko po zgłoszeniu otrzymam rabaty hurtowe?</span>
          <span style="color:var(--p-primary); font-size:20px;">+</span>
        </div>
        <div class="faq-answer">
          Twój dedykowany opiekun handlowy kontaktuje się z Tobą w ciągu maksymalnie 2 godzin roboczych. Po weryfikacji NIP firmy konto hurtowe jest natychmiast aktywne, a Ty otrzymujesz indywidualny cennik i dostęp do zamówień.
        </div>
      </div>

      <div class="faq-card">
        <div class="faq-question">
          <span>Czy obowiązuje minimalna kwota zamówienia (MOQ)?</span>
          <span style="color:var(--p-primary); font-size:20px;">+</span>
        </div>
        <div class="faq-answer">
          Nie. Wspieramy zarówno duże realizacje kubaturowe, jak i bieżące zakupy instalacyjne. Nawet przy zamówieniu pojedynczej rolki taśmy LED lub jednego zasilacza przysługuje Ci przypisany rabat wykonawczy.
        </div>
      </div>

      <div class="faq-card">
        <div class="faq-question">
          <span>Jak otrzymać bezpłatny zestaw próbek i wzorników?</span>
          <span style="color:var(--p-primary); font-size:20px;">+</span>
        </div>
        <div class="faq-answer">
          Wystarczy zaznaczyć chęć otrzymania wzorników w formularzu powyżej lub poinformować o tym opiekuna handlowego. Wysyłamy fizyczne próbniki taśm COB, profili KLUŚ i złączek Hippo bezpośrednio do Twojego biura lub warsztatu.
        </div>
      </div>

      <div class="faq-card">
        <div class="faq-question">
          <span>Jakie są warunki i terminy płatności?</span>
          <span style="color:var(--p-primary); font-size:20px;">+</span>
        </div>
        <div class="faq-answer">
          Dla pierwszych zamówień standardem jest przedpłata Proforma lub pobranie kurierskie. Od drugiego zamówienia stałym partnerom oferujemy limit kupiecki oraz odroczone terminy płatności 14–30 dni.
        </div>
      </div>

      <div class="faq-card">
        <div class="faq-question">
          <span>Czy wykonujecie darmowe projekty i dobór zasilania?</span>
          <span style="color:var(--p-primary); font-size:20px;">+</span>
        </div>
        <div class="faq-answer">
          Tak. Prześlij rzut architektoniczny lub schemat instalacji na adres <a href="mailto:komponenty@prescot.pl" style="color:var(--p-primary); text-decoration:none; font-weight:700;">komponenty@prescot.pl</a>. Nasi inżynierowie oświetlenia bezpłatnie zweryfikują spadki napięć, dobiorą moc zasilaczy i przekażą kompletną specyfikację materiałową.
        </div>
      </div>
    </div>
  </section>
</main>

<!-- FOOTER -->
<footer style="background:#0f172a; color:#94a3b8; padding:60px 24px 100px 24px; border-top:1px solid rgba(255,255,255,0.08);">
  <div style="max-width:1200px; margin:0 auto; display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:40px;">
    <div>
      <img src="/wp-content/uploads/2025/12/biale-z-kolorem.svg" alt="Prescot LED" style="height:34px; margin-bottom:16px;">
      <p style="font-size:13.5px; line-height:1.6; color:#94a3b8;">Polski producent oświetlenia LED i zasilaczy Ultra Slim. Niezawodne systemy oświetleniowe dla profesjonalistów.</p>
    </div>
    <div>
      <h4 style="color:#ffffff; font-family:'Outfit',sans-serif; margin-bottom:14px; font-size:16px;">Centrala &amp; Magazyn</h4>
      <p style="font-size:13.5px; line-height:1.7; color:#94a3b8;">
        PRESCOT sp. z o.o.<br>
        ul. Wileńska 1, 11-500 Giżycko<br>
        NIP: 8451996500 | KRS: 0001004381
      </p>
    </div>
    <div>
      <h4 style="color:#ffffff; font-family:'Outfit',sans-serif; margin-bottom:14px; font-size:16px;">Kontakt B2B</h4>
      <p style="font-size:13.5px; line-height:1.7; color:#94a3b8;">
        Dział handlowy: <a href="tel:+48877776482" style="color:#ff8a65; text-decoration:none; font-weight:700;">+48 87 777 64 82</a><br>
        E-mail: <a href="mailto:komponenty@prescot.pl" style="color:#ff8a65; text-decoration:none;">komponenty@prescot.pl</a><br>
        Godziny: Pn–Pt 8:00–16:00
      </p>
    </div>
    <div>
      <h4 style="color:#ffffff; font-family:'Outfit',sans-serif; margin-bottom:14px; font-size:16px;">Platforma B2B</h4>
      <p style="font-size:13.5px; line-height:1.6; color:#94a3b8; margin-bottom:12px;">Dla zarejestrowanych klientów hurtowych z aktywnym rabatem.</p>
      <a href="https://prescot.abstore.pl/client/loginorcreate/login" target="_blank" rel="noopener" class="p-btn p-btn-outline" style="font-size:12.5px; padding:8px 18px;">
        Logowanie AB-Store &rarr;
      </a>
    </div>
  </div>
  <div style="max-width:1200px; margin:40px auto 0 auto; padding-top:24px; border-top:1px solid rgba(255,255,255,0.06); display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; font-size:12.5px;">
    <div>&copy; 2026 PRESCOT sp. z o.o. Wszelkie prawa zastrzeżone.</div>
    <div>
      <a href="/polityka-prywatnosci/" style="color:#94a3b8; text-decoration:none; margin-right:16px;">Polityka Prywatności</a>
      <a href="/regulamin/" style="color:#94a3b8; text-decoration:none;">Regulamin</a>
    </div>
  </div>
</footer>

<!-- CANONICAL GLOBAL MENU DOCK -->
<nav class="prescot-dock" aria-label="Nawigacja główna">
  <a href="/prescotled/" class="dock-item" data-tooltip="Prescot LED" aria-label="Prescot LED">
    <svg class="dock-logo-icon" viewBox="0 0 378 258" xmlns="http://www.w3.org/2000/svg"><path fill="#e14e26" d="M0,0h106.7v50H0V0ZM0,100.9h97.7v48.2H0v-48.2ZM0,206.6h106.7v51.2H0v-51.2h0ZM149.3,100.7h82v48.4h-82v-48.4h0ZM149.3,0h87.4C317.7,0,377.9,42.6,377.9,128.9s-60.1,128.9-141.2,128.9h-87.4v-51.2h90.8c47.8,0,76.6-29.1,76.6-77.7s-27.6-78.8-76.6-78.8h-90.8V0h0Z"/></svg>
  </a>
  <a href="/produkty/" class="dock-item" data-tooltip="Oferta" aria-label="Oferta">
    <svg viewBox="0 0 576 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M542.22 32.05c-54.8 3.11-163.72 14.43-230.96 55.59-4.64 2.84-7.27 7.89-7.27 13.17v363.87c0 11.55 12.63 18.85 23.28 13.49 69.18-34.82 169.23-44.32 218.7-46.92 16.89-.89 30.02-14.43 30.02-30.66V62.75c.01-17.71-15.35-31.74-33.77-30.7zM264.73 87.64C197.5 46.48 88.58 35.17 33.78 32.05 15.36 31.01 0 45.04 0 62.75V400.6c0 16.24 13.13 29.78 30.02 30.66 49.49 2.6 149.59 12.11 218.77 46.95 10.62 5.35 23.21-1.94 23.21-13.46V100.63c0-5.29-2.62-10.14-7.27-12.99z"/></svg>
  </a>
  <a href="/tasmy-led/" class="dock-item" data-tooltip="Taśmy LED" aria-label="Taśmy LED">
    <svg viewBox="0 0 640 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M224 192c-35.3 0-64 28.7-64 64s28.7 64 64 64 64-28.7 64-64-28.7-64-64-64zm400 224H380.6c41.5-40.7 67.4-97.3 67.4-160 0-123.7-100.3-224-224-224S0 132.3 0 256s100.3 224 224 224h400c8.8 0 16-7.2 16-16v-32c0-8.8-7.2-16-16-16zm-400-64c-53 0-96-43-96-96s43-96 96-96 96 43 96 96-43 96-96 96z"/></svg>
  </a>
  <a href="/produkcja/" class="dock-item" data-tooltip="Produkcja" aria-label="Produkcja">
    <svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M475.115 163.781L336 252.309v-68.28c0-18.916-20.931-30.399-36.885-20.248L160 252.309V56c0-13.255-10.745-24-24-24H24C10.745 32 0 42.745 0 56v400c0 13.255 10.745 24 24 24h464c13.255 0 24-10.745 24-24V184.029c0-18.917-20.931-30.399-36.885-20.248z"/></svg>
  </a>
  <a href="/dystrybucja/" class="dock-item" data-tooltip="Dystrybucja" aria-label="Dystrybucja">
    <svg viewBox="0 0 640 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M624 352h-16V243.9c0-12.7-5.1-24.9-14.1-33.9L494 110.1c-9-9-21.2-14.1-33.9-14.1H416V48c0-26.5-21.5-48-48-48H48C21.5 0 0 21.5 0 48v320c0 26.5 21.5 48 48 48h16c0 53 43 96 96 96s96-43 96-96h128c0 53 43 96 96 96s96-43 96-96h48c8.8 0 16-7.2 16-16v-32c0-8.8-7.2-16-16-16zM160 464c-26.5 0-48-21.5-48-48s21.5-48 48-48 48 21.5 48 48-21.5 48-48 48zm320 0c-26.5 0-48-21.5-48-48s21.5-48 48-48 48 21.5 48 48-21.5 48-48 48zm80-208H448v-96h46.1l65.9 65.9V256z"/></svg>
  </a>
  <a href="/wspolpraca-b2b/" class="dock-item active" data-tooltip="Strefa B2B" aria-label="Strefa B2B">
    <svg viewBox="0 0 640 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M128 352H32c-17.67 0-32 14.33-32 32v96c0 17.67 14.33 32 32 32h96c17.67 0 32-14.33 32-32v-96c0-17.67-14.33-32-32-32zm-24-80h192v48h48v-48h192v48h48v-57.59c0-21.17-17.23-38.41-38.41-38.41H344v-64h40c17.67 0 32-14.33 32-32V32c0-17.67-14.33-32-32-32H256c-17.67 0-32 14.33-32 32v96c0 17.67 14.33 32 32 32h40v64H94.41C73.23 224 56 241.23 56 262.41V320h48v-48zm264 80h-96c-17.67 0-32 14.33-32 32v96c0 17.67 14.33 32 32 32h96c17.67 0 32-14.33 32-32v-96c0-17.67-14.33-32-32-32zm240 0h-96c-17.67 0-32 14.33-32 32v96c0 17.67 14.33 32 32 32h96c17.67 0 32-14.33 32-32v-96c0-17.67-14.33-32-32-32z"/></svg>
  </a>
  <a href="/baza-wiedzy/" class="dock-item" data-tooltip="Baza Wiedzy" aria-label="Baza Wiedzy & FAQ">
    <svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M256 32C132.3 32 32 132.3 32 256s100.3 224 224 224 224-100.3 224-224S379.7 32 256 32zm0 376c-17.7 0-32-14.3-32-32s14.3-32 32-32 32 14.3 32 32-14.3 32-32 32zm42.7-142.1c-13.8 11.2-26.7 21.6-26.7 46.1v10c0 8.8-7.2 16-16 16h-32c-8.8 0-16-7.2-16-16v-14c0-38.4 22.8-56.9 44.4-74.4 14.1-11.4 27.6-22.3 27.6-39.6 0-21.2-18.7-36-44-36-24.6 0-41.9 14.2-46.7 32.5-2.2 8.5-10.4 13.9-19.1 12.3l-30.8-5.6c-9.1-1.7-14.8-10.7-12.4-19.7C180.7 132.2 214.2 104 256 104c53 0 96 34.3 96 82 0 35.8-21.7 61.2-53.3 83.9z"/></svg>
  </a>
  <a href="https://prescot.com.pl/" class="dock-item" data-tooltip="Sklep B2C" aria-label="Sklep B2C" target="_blank" rel="noopener">
    <svg viewBox="0 0 576 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M576 216v16c0 13.255-10.745 24-24 24h-8l-26.113 182.788C514.509 462.435 494.257 480 470.37 480H105.63c-23.887 0-44.139-17.565-47.518-41.212L32 256h-8c-13.255 0-24-10.745-24-24v-16c0-13.255 10.745-24 24-24h67.341l106.78-146.821c10.395-14.292 30.407-17.453 44.701-7.058 14.293 10.395 17.453 30.408 7.058 44.701L170.477 192h235.046L326.12 82.821c-10.395-14.292-7.234-34.306 7.059-44.701 14.291-10.395 34.306-7.235 44.701 7.058L484.659 192H552c13.255 0 24 10.745 24 24zM312 392V280c0-13.255-10.745-24-24-24s-24 10.745-24 24v112c0 13.255 10.745 24 24 24s24-10.745 24-24zm112 0V280c0-13.255-10.745-24-24-24s-24 10.745-24 24v112c0 13.255 10.745 24 24 24s24-10.745 24-24zm-224 0V280c0-13.255-10.745-24-24-24s-24 10.745-24 24v112c0 13.255 10.745 24 24 24s24-10.745 24-24z"/></svg>
  </a>
  <a href="/kontakt/" class="dock-item" data-tooltip="Kontakt" aria-label="Kontakt">
    <svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M493.4 24.6l-104-24c-11.3-2.6-22.9 3.3-27.5 14l-48 112c-4.2 9.8-1.4 21.3 6.9 28l60.6 49.6c-36 76.7-98.9 140.5-177.2 177.2l-49.6-60.6c-6.8-8.3-18.2-11.1-28-6.9l-112 48C4.1 366.5-1.8 378.1.8 389.4l24 104C27.3 504.2 36.7 512 48 512c256.1 0 464-207.5 464-464 0-11.2-7.7-21-18.6-23.4z"/></svg>
  </a>
</nav>

<script>
// Obsługa wysyłki formularza B2B
document.getElementById('b2b-reg-form').addEventListener('submit', function(e) {
  e.preventDefault();
  var hp = document.querySelector('input[name="b2b_hp"]').value;
  if (hp) return;

  var nip = document.getElementById('b2b-nip').value.trim();
  var company = document.getElementById('b2b-company').value.trim();
  var name = document.getElementById('b2b-name').value.trim();
  var email = document.getElementById('b2b-email').value.trim();
  var phone = document.getElementById('b2b-phone').value.trim();
  var type = document.getElementById('b2b-type').value;
  var msg = document.getElementById('b2b-msg').value.trim();

  if (!nip || !company || !name || !email || !phone) {
    alert('Prosimy o uzupełnienie wymaganych pól formularza.');
    return;
  }

  // Symulacja / wysyłka mailto z gotową treścią dla pewności
  var bodyText = encodeURIComponent(
    "Zgłoszenie do Programu Partnerskiego B2B Prescot LED:\\n\\n" +
    "NIP: " + nip + "\\n" +
    "Firma: " + company + "\\n" +
    "Osoba kontaktowa: " + name + "\\n" +
    "E-mail: " + email + "\\n" +
    "Telefon: " + phone + "\\n" +
    "Profil działalności: " + type + "\\n" +
    "Wiadomość / Zapotrzebowanie: " + msg + "\\n"
  );

  var mailtoUrl = "mailto:komponenty@prescot.pl?subject=" + encodeURIComponent("Zgłoszenie B2B: " + company + " (NIP " + nip + ")") + "&body=" + bodyText;

  var feedback = document.getElementById('b2b-feedback');
  feedback.style.display = 'block';
  feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  // Opcjonalne otwarcie klienta pocztowego w tle
  try {
    var iframe = document.createElement("iframe");
    iframe.style.display = "none";
    iframe.src = mailtoUrl;
    document.body.appendChild(iframe);
  } catch(err) {}
});

// FAQ Accordion Toggle
document.querySelectorAll('.faq-card').forEach(function(card) {
  card.addEventListener('click', function() {
    var ans = card.querySelector('.faq-answer');
    var plus = card.querySelector('.faq-question span:last-child');
    if (ans.style.display === 'none') {
      ans.style.display = 'block';
      plus.textContent = '−';
    } else {
      ans.style.display = 'none';
      plus.textContent = '+';
    }
  });
});
</script>
</body>
</html>
"""

# Zapis do plików
PATHS = [
    "/Users/karolbohdanowicz/safe_backup/tasmaled-local/public/wspolpraca-b2b.html",
    "/Users/karolbohdanowicz/safe_backup/tasmaled-local/public/wspolpraca-b2b/index.html",
    "/Users/karolbohdanowicz/safe_backup/prescotpl/wspolpraca-b2b.html",
    "/Users/karolbohdanowicz/safe_backup/prescotpl/wspolpraca-b2b/index.html"
]

for p in PATHS:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print(f"✅ Wygenerowano B2B: {p}")

print("\nSukces! Strona B2B została całkowicie przebudowana na wyspecjalizowany lejek pozyskiwania partnerów.")
