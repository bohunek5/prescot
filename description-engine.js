const PLATFORM_NAMES = {
  shoper: "Shoper",
  wapro: "WAPRO / MAG",
  tim: "TIM",
  allegro: "Allegro",
};

const STYLE = {
  section: "font-family:inherit;margin:28px 0 18px 0;padding:22px 24px;background:none!important;background-color:transparent!important;border:1px solid currentColor;border-radius:12px;color:inherit;",
  sectionSub: "font-family:inherit;margin:0 0 18px 0;padding:22px 24px;background:none!important;background-color:transparent!important;border:1px solid currentColor;border-radius:12px;color:inherit;",
  sectionLast: "font-family:inherit;margin:0 0 28px 0;padding:24px;background:none!important;background-color:transparent!important;border:1px solid currentColor;border-radius:12px;color:inherit;",
  pill: "font-family:inherit;display:inline-block;margin-bottom:10px;padding:5px 12px;border-radius:999px;background:#e94b25!important;background-color:#e94b25!important;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;font-size:11px;font-weight:bold;letter-spacing:.8px;text-transform:uppercase;line-height:1.2;",
  heading: "font-family:inherit;margin:0 0 8px 0;background:none!important;background-color:transparent!important;color:inherit!important;font-size:22px;line-height:1.3;font-weight:bold;",
  paragraph: "font-family:inherit;margin:0;background:none!important;background-color:transparent!important;color:inherit!important;opacity:.82;font-size:14px;line-height:1.65;",
  list: "font-family:inherit;margin:0;padding:0 0 0 20px;color:inherit!important;opacity:.86;font-size:14px;line-height:1.65;",
};

const SEO_BLOG_GUIDES = {
  "Taśmy LED": {
    heading: "Dobierz taśmę LED jak profesjonalista",
    description: "Poniższe poradniki pomogą dobrać taśmę, profil, parametry i sposób montażu do konkretnego zastosowania.",
    items: [
      ["Jak czytać parametry taśmy LED?", "moc, lumeny, CRI, napięcie i IP", "https://www.prescot.com.pl/pl/n/23"],
      ["Montaż taśmy LED na zewnątrz", "IP, uszczelnienie i ochrona połączeń", "https://www.prescot.com.pl/pl/n/16"],
      ["Jak dobrać taśmę LED do mieszkania?", "barwa, moc i miejsce montażu", "https://www.prescot.com.pl/pl/n/12"],
      ["Jak dobrać profil aluminiowy do taśmy LED?", "profil, klosz, chłodzenie i estetyka linii światła", "https://www.prescot.com.pl/pl/n/15"],
    ],
  },
  "Profile do taśm LED": {
    heading: "Dobierz profil i taśmę jako jeden układ",
    description: "Poradniki pomagają zestawić profil, klosz i taśmę oraz zaplanować chłodzenie i wygląd linii światła.",
    items: [
      ["Jak dobrać profil aluminiowy do taśmy LED?", "profil, klosz, chłodzenie i estetyka linii światła", "https://www.prescot.com.pl/pl/n/15"],
      ["Jak czytać parametry taśmy LED?", "moc, lumeny, CRI, napięcie i IP", "https://www.prescot.com.pl/pl/n/23"],
      ["Jak dobrać taśmę LED do mieszkania?", "barwa, moc i miejsce montażu", "https://www.prescot.com.pl/pl/n/12"],
      ["Montaż taśmy LED na zewnątrz", "IP, uszczelnienie i ochrona połączeń", "https://www.prescot.com.pl/pl/n/16"],
    ],
  },
  "Zasilacze LED": {
    heading: "Dobierz zasilacz LED bez zgadywania",
    description: "Sprawdź krótkie poradniki, które pomogą dobrać moc, typ obudowy, napięcie i stopień ochrony IP do konkretnej instalacji LED.",
    items: [
      ["Do czego służą zasilacze LED?", "taśmy LED, moduły LED i sterowniki", "https://www.prescot.com.pl/pl/n/30"],
      ["Zasilacze LED - gdzie użyć którego?", "desktop, gniazdkowy, siatkowy, slim i hermetyczny", "https://www.prescot.com.pl/pl/n/29"],
      ["Montaż taśmy LED na zewnątrz", "wilgoć, stopień IP i dobór zasilania", "https://www.prescot.com.pl/pl/n/16"],
      ["Stopnie IP - dlaczego to ważne?", "IP20, IP33, IP44 i IP67 w praktyce", "https://www.prescot.com.pl/pl/n/31"],
    ],
  },
  "Sterowniki LED": {
    heading: "Sterowanie dobierz do typu taśmy, nie na końcu montażu",
    description: "Najpierw sprawdź kanały taśmy, napięcie, przewody i miejsce na odbiornik, a dopiero potem dobierz sposób sterowania.",
    items: [
      ["Jak czytać opis taśmy LED?", "moc, lumeny, CRI, napięcie i IP", "https://www.prescot.com.pl/pl/n/23"],
      ["Jak dobrać taśmę LED do mieszkania?", "barwa, długość i miejsce montażu", "https://www.prescot.com.pl/pl/n/12"],
      ["Jak dobrać zasilacz LED do taśmy?", "moc W/m, długość taśmy i zapas mocy", "https://www.prescot.com.pl/pl/n/24"],
      ["Jak dobrać profil aluminiowy do taśmy LED?", "profil, klosz, chłodzenie i estetyka linii światła", "https://www.prescot.com.pl/pl/n/15"],
    ],
  },
  "Akcesoria do zasilaczy i taśm LED": {
    heading: "Sprawdź zgodność elementów instalacji LED",
    description: "Materiały pomagają porównać parametry, przygotować montaż i uniknąć przypadkowego łączenia niezgodnych elementów.",
    items: [
      ["Jak czytać parametry taśmy LED?", "moc, lumeny, CRI, napięcie i IP", "https://www.prescot.com.pl/pl/n/23"],
      ["Jak dobrać profil aluminiowy do taśmy LED?", "miejsce na taśmę, przewód i złączkę", "https://www.prescot.com.pl/pl/n/15"],
      ["Montaż taśmy LED na zewnątrz", "IP, uszczelnienie i ochrona połączeń", "https://www.prescot.com.pl/pl/n/16"],
    ],
  },
};

const SEO_ADMIN_ATTRIBUTES = new Set([
  "Producent odpowiedzialny",
  "Podmiot odpowiedzialny",
  "Nazwa galerii",
  "Informacje o bezpieczeństwie",
]);

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function normalize(value) {
  return String(value ?? "").replace(/\s+/g, " ").trim();
}

function pillStyle(color = "#e94b25") {
  return STYLE.pill.replaceAll("#e94b25", color);
}

function publicLabel(match) {
  const value = String(match || "");
  return value === value.toLocaleUpperCase("pl") || /^[A-ZĄĆĘŁŃÓŚŹŻ]/.test(value)
    ? "Indeks handlowy"
    : "indeks handlowy";
}

function replaceDescriptionIdentity(product, htmlValue, { preserveManufacturerCode = false } = {}) {
  const tradeIndex = normalize(product?.code);
  let value = String(htmlValue || "");
  if (preserveManufacturerCode) {
    return value
      .replace(/\b(?:numer|nr) katalogowy\b/gi, publicLabel)
      .replace(/\bkod produktu\b/gi, publicLabel)
      .replace(/\bkodu produktu\b/gi, "indeksu handlowego")
      .replace(/\bkodem produktu\b/gi, "indeksem handlowym");
  }
  const manufacturerCode = normalize(product?.manufacturerCode);
  if (tradeIndex && manufacturerCode && tradeIndex !== manufacturerCode) {
    const escapedCode = manufacturerCode.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    value = value.replace(
      new RegExp(`((?:kod|numer|nr)\\s+(?:katalogowy\\s+)?producenta(?:\\s|:|&nbsp;|<[^>]+>){1,8})${escapedCode}`, "gi"),
      (match, prefix) => `${prefix.replace(/(?:kod|numer|nr)\s+(?:katalogowy\s+)?producenta/gi, publicLabel)}${tradeIndex}`,
    );
  }
  return value
    .replace(/\b(?:kod|numer|nr)\s+(?:katalogowy\s+)?producenta\b/gi, publicLabel)
    .replace(/\b(?:numer|nr) katalogowy\b/gi, publicLabel)
    .replace(/\bkod produktu\b/gi, publicLabel)
    .replace(/\bkodu (?:producenta|produktu)\b/gi, "indeksu handlowego")
    .replace(/\bkodem (?:producenta|produktu)\b/gi, "indeksem handlowym")
    .replace(/\b(?:numeru|nr) katalogowego(?: producenta)?\b/gi, "indeksu handlowego");
}

export function normalizeDescriptionIdentity(product, htmlValue, { ensureTradeIndex = false, preserveManufacturerCode = false } = {}) {
  return replaceDescriptionIdentity(product, htmlValue, { preserveManufacturerCode });
}

function leafCategory(product) {
  return normalize(product.category?.split("/").at(-1) || product.categoryRoot || "produkt");
}

function productKind(product) {
  const root = product.categoryRoot || "";
  const all = `${root} ${product.category} ${product.name}`.toLocaleLowerCase("pl");
  if (root === "Taśmy LED" || /taśm[ay] led/.test(all)) return "tape";
  if (root === "Profile do taśm LED" || /profil[eey] led/.test(all)) return "profile";
  if (root === "Zasilacze LED" || /zasilacz[ey]?/.test(all)) return "power";
  if (root === "Sterowniki LED" || /sterownik|pilot|panel|odbiornik/.test(all)) return "control";
  if (root === "Akcesoria do zasilaczy i taśm LED" || /złączk|przewód|kabel|uchwyt|zaślepk|końcówk/.test(all)) return "connector";
  return "other";
}

function seoProductSpecs(product) {
  const seen = new Set();
  const specs = [];
  const identityLabels = new Set(["producent", "kod produktu", "kod producenta", "ean", "indeks handlowy", "nazwa galerii"]);
  
  // 1. Z atrybutów
  for (const [rawLabel, rawValue] of Object.entries(product.attributes || {})) {
    const label = normalize(rawLabel).replaceAll("_", " ");
    const value = normalize(rawValue);
    const identity = label.toLocaleLowerCase("pl");
    if (!value || value === "-" || SEO_ADMIN_ATTRIBUTES.has(label) || identityLabels.has(identity) || seen.has(identity)) continue;
    seen.add(identity);
    specs.push([label, value]);
  }
  
  // 2. Z opisu źródłowego (jeśli mało parametrów)
  if (specs.length < 3 && product.sourceDescription) {
    const lines = String(product.sourceDescription).split("\n");
    for (const rawLine of lines) {
      const match = rawLine.match(/^([^:]{2,35}):\s*(.{1,80})$/);
      if (match) {
        const label = normalize(match[1]).replace(/^[•*\-–—]+\s*/, "");
        const value = normalize(match[2]);
        const identity = label.toLocaleLowerCase("pl");
        if (value && value !== "-" && !identityLabels.has(identity) && !seen.has(identity) && !/kliknij|http|www/i.test(value)) {
          seen.add(identity);
          specs.push([label, value]);
        }
      }
    }
  }

  // 3. Wyciąganie kluczowych parametrów z nazwy, jeśli nadal pusto
  if (specs.length < 2) {
    const powerMatch = product.name.match(/\b\d+(?:[.,]\d+)?\s*W\b/i);
    const voltMatch = product.name.match(/\b\d+\s*V(?:\s*DC)?\b/i);
    const ipMatch = product.name.match(/\bIP\d{2}\b/i);
    if (powerMatch && !seen.has("moc wyjściowa") && !seen.has("moc")) {
      specs.push(["Moc wyjściowa", powerMatch[0]]);
    }
    if (voltMatch && !seen.has("napięcie wyjściowe") && !seen.has("napięcie")) {
      specs.push(["Napięcie wyjściowe", voltMatch[0]]);
    }
    if (ipMatch && !seen.has("klasa szczelności")) {
      specs.push(["Klasa szczelności", ipMatch[0]]);
    }
  }

  return specs;
}

function renderPillSection(pillText, headingText, paragraphsList, style = STYLE.sectionSub, pillColor = "#e94b25") {
  const pTags = (Array.isArray(paragraphsList) ? paragraphsList : [paragraphsList])
    .filter(Boolean)
    .map((p) => `<p style="${STYLE.paragraph}">${escapeHtml(normalize(p))}</p>`)
    .join("");
  return `<section style="${style}"><span style="${pillStyle(pillColor)}"><span style="color:#ffffff;">${escapeHtml(normalize(pillText))}</span></span>\n<h3 style="${STYLE.heading}">${escapeHtml(normalize(headingText))}</h3>\n${pTags}\n</section>`;
}

function renderGuidesSection(product) {
  const guide = SEO_BLOG_GUIDES[product.categoryRoot] || SEO_BLOG_GUIDES["Taśmy LED"];
  if (!guide) return "";
  const cards = guide.items.map(([title, description, url]) => (
    `<div style="font-family:inherit;min-height:190px;padding:18px;margin:0;background:none!important;background-color:transparent!important;border:1px solid currentColor;border-radius:12px;box-shadow:none!important;color:inherit;display:flex;flex-direction:column;"><strong style="font-family:inherit;display:block;color:inherit!important;font-size:15px;line-height:1.35;margin-bottom:6px;font-weight:bold;">${escapeHtml(title)}</strong><small style="font-family:inherit;display:block;color:inherit!important;opacity:.76;font-size:12px;line-height:1.4;margin-bottom:15px;">${escapeHtml(description)}</small><a style="font-family:inherit;display:inline-block;min-width:142px;margin-top:auto;padding:10px 17px;border-radius:999px;background:#e94b25!important;background-color:#e94b25!important;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;text-decoration:none!important;text-align:center;line-height:1.2;border:0!important;align-self:flex-start;" href="${escapeHtml(url)}"><span style="color:#ffffff;"><span style="font-family:inherit;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;text-decoration:none!important;font-weight:bold;font-size:14px;">Czytaj poradnik</span></span></a></div>`
  )).join("");
  return `<section style="${STYLE.sectionLast}">\n<div style="font-family:inherit;margin-bottom:18px;background:none!important;background-color:transparent!important;color:inherit;"><span style="${pillStyle("#e94b25")}"><span style="color:#ffffff;">Praktyczne poradniki</span></span>\n<h3 style="${STYLE.heading}">${escapeHtml(guide.heading)}</h3>\n<p style="${STYLE.paragraph}">${escapeHtml(guide.description)}</p>\n</div>\n<div style="font-family:inherit;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;background:none!important;background-color:transparent!important;color:inherit;align-items:stretch;">\n${cards}\n</div>\n</section>`;
}

function renderShoper(product, saved) {
  const result = saved?.editorial || saved || {};
  const kind = productKind(product);
  const sections = result.sections || [];
  
  // 1. Sekcja Opis / Seria
  let pill1 = leafCategory(product);
  if (kind === "tape") {
    if (/s-shape/i.test(product.name)) pill1 = "Taśmy LED S-shape";
    else if (/wcob/i.test(product.name)) pill1 = "Taśmy LED WCOB";
    else if (/cob/i.test(product.name)) pill1 = "Taśmy LED COB";
    else if (/48v/i.test(product.name)) pill1 = "Taśmy LED 48V";
    else if (/24v/i.test(product.name)) pill1 = "Taśmy LED 24V";
    else if (/12v/i.test(product.name)) pill1 = "Taśmy LED 12V";
    else pill1 = "Taśmy LED";
  } else if (kind === "power") {
    if (/scharfer/i.test(product.name)) pill1 = "Zasilacz LED Scharfer 24V";
    else if (/modułow/i.test(product.name)) pill1 = "Zasilacz modułowy LED";
    else if (/hermetyczn/i.test(product.name)) pill1 = "Zasilacz hermetyczny LED";
    else pill1 = "Zasilacze LED";
  } else if (kind === "control") {
    pill1 = "Sterowniki LED";
  } else if (kind === "connector") {
    pill1 = "Złączki i akcesoria LED";
  } else if (kind === "profile") {
    pill1 = "Profile do taśm LED";
  }

  const heading1 = sections[0]?.heading || product.name;
  const p1 = sections[0]?.paragraphs || [product.summary || product.name];
  const sec1 = renderPillSection(pill1, heading1, p1, STYLE.section);

  // 2. Sekcja Barwa / Gdzie użyć / Zastosowanie
  let pill2 = "Gdzie użyć";
  if (kind === "tape") {
    if (/3000k|ciepł/i.test(product.name)) pill2 = "Barwa ciepła";
    else if (/4000k|neutraln/i.test(product.name)) pill2 = "Barwa neutralna";
    else if (/6000k|6500k|zimn/i.test(product.name)) pill2 = "Barwa zimna";
    else if (/cct/i.test(product.name)) pill2 = "Regulacja CCT";
    else if (/rgb\+w|rgbw/i.test(product.name)) pill2 = "Kolory RGB+W";
    else if (/rgb/i.test(product.name)) pill2 = "Kolory RGB";
  }
  const heading2 = sections[1]?.heading || (kind === "power" ? "Do jakich instalacji wybrać ten zasilacz" : "Kiedy i gdzie wybrać ten wariant");
  const p2 = sections[1]?.paragraphs || (result.applications || ["Sprawdź zastosowanie w specyfikacji."]);
  const sec2 = renderPillSection(pill2, heading2, p2, STYLE.sectionSub);

  // 3. Sekcja Jasność / Parametry (dla zasilaczy) / Wskazówki
  let sec3 = "";
  if (kind === "power") {
    // Siatka parametrów dla zasilaczy
    const specs = seoProductSpecs(product);
    const gridCards = specs.slice(0, 6).map(([label, value]) => (
      `<div style="font-family:inherit;padding:16px;margin:0;background:none!important;background-color:transparent!important;border:1px solid currentColor;border-radius:12px;box-shadow:none!important;color:inherit;"><strong style="font-family:inherit;display:block;color:inherit!important;font-size:15px;line-height:1.35;margin-bottom:6px;font-weight:bold;">${escapeHtml(label)}</strong><small style="font-family:inherit;display:block;color:inherit!important;opacity:.78;font-size:13px;line-height:1.45;">${escapeHtml(value)}</small></div>`
    )).join("");
    const gridHtml = `<div style="font-family:inherit;display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;background:none!important;background-color:transparent!important;color:inherit;">\n${gridCards}\n</div>`;
    const note = sections[2]?.paragraphs?.[0] || "Najważniejsze cechy serii: stabilne napięcie wyjściowe, wysoka sprawność oraz zabezpieczenie przed przeciążeniem i zwarciem.";
    sec3 = `<section style="${STYLE.sectionSub}"><span style="${pillStyle("#e94b25")}"><span style="color:#ffffff;">Parametry modelu</span></span>\n${gridHtml}\n<p style="${STYLE.paragraph};margin-top:16px;">${escapeHtml(normalize(note))}</p>\n</section>`;
  } else if (kind === "tape") {
    // Dla taśm: akapit o jasności / strumieniu / zasilaniu bez tabeli
    let pill3 = "Jasność i strumień";
    const lmMatch = product.name.match(/\b\d+\s*lm\/m\b/i);
    if (lmMatch) pill3 = lmMatch[0];
    const heading3 = sections[2]?.heading || "Mocne i stabilne światło w Twojej instalacji";
    const p3 = sections[2]?.paragraphs || ["Taśma zapewnia równomierny strumień świetlny oraz komfortowe oświetlenie powierzchni użytkowej lub dekoracyjnej."];
    sec3 = renderPillSection(pill3, heading3, p3, STYLE.sectionSub);
  } else {
    // Dla innych: sekcja wskazówek / doboru
    const pill3 = sections[2]?.label || "Dobór i montaż";
    const heading3 = sections[2]?.heading || "Co sprawdzić przed montażem";
    const p3 = sections[2]?.paragraphs || result.installation_notes || ["Przed montażem potwierdź zgodność elementów instalacji."];
    sec3 = renderPillSection(pill3, heading3, p3, STYLE.sectionSub);
  }

  // 4. Sekcja Praktyczne poradniki (Blog)
  const sec4 = renderGuidesSection(product);

  return [sec1, sec2, sec3, sec4].filter(Boolean).join("\n");
}

function renderWapro(product, saved) {
  const result = saved?.editorial || saved || {};
  const specs = seoProductSpecs(product).slice(0, 7).map(([label, value]) => `${label}: ${value}`);
  const intro = result.sections?.[0]?.paragraphs?.map(normalize).join(" ") || product.summary || product.name;
  const features = specs.length ? specs : (result.benefits || []);
  const points = (values) => (values || []).map((val) => `<p>- ${escapeHtml(normalize(val).replace(/\.$/, ""))}</p>`).join("");
  const benefitsBlock = (result.benefits && result.benefits.length) ? `<h3>Dlaczego warto:</h3>\n${points(result.benefits)}` : "";
  return `<section>\n<h2>${escapeHtml(product.name)}</h2>\n<p>${escapeHtml(intro)}</p>\n<h3>Najważniejsze cechy:</h3>\n${points(features)}\n${benefitsBlock}\n<h3>Gdzie użyć:</h3>\n${points(result.applications || [])}\n</section>`;
}

function renderAllegro(product, saved) {
  const result = saved?.editorial || saved || {};
  const lead = result.channel_leads?.allegro || result.seo_title || product.name;
  const title = result.seo_title || product.name;
  
  const sec1 = renderPillSection("Sprawdź przed zakupem", title, lead, STYLE.sectionSub, "#16a34a");
  
  let sec2 = "";
  if (result.benefits && result.benefits.length) {
    const cards = result.benefits.map((point) => (
      `<div style="display:flex;gap:10px;align-items:flex-start;padding:12px 14px;border:1px solid currentColor;border-radius:10px;"><span style="display:inline-flex;align-items:center;justify-content:center;flex:0 0 22px;width:22px;height:22px;border-radius:999px;background:#16a34a!important;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;font-weight:800;line-height:1;">✓</span><span style="font-size:14px;line-height:1.45;color:inherit;">${escapeHtml(normalize(point).replace(/\.$/, ""))}</span></div>`
    )).join("");
    sec2 = `<section style="${STYLE.sectionSub}"><span style="${pillStyle("#16a34a")}"><span style="color:#ffffff;">Dlaczego warto</span></span><h3 style="${STYLE.heading}">Najważniejsze korzyści tego wariantu</h3><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px;margin-top:10px;">${cards}</div></section>`;
  }

  const sec3 = result.sections?.[1]
    ? renderPillSection("Gdzie użyć", result.sections[1].heading, result.sections[1].paragraphs, STYLE.sectionSub, "#16a34a")
    : "";

  let sec4 = "";
  const notes = result.installation_notes || [];
  if (notes.length) {
    const items = notes.map((point) => `<li style="font-family:inherit;margin-bottom:7px;">${escapeHtml(normalize(point).replace(/\.$/, ""))}</li>`).join("");
    sec4 = `<section style="${STYLE.sectionLast}"><span style="${pillStyle("#16a34a")}"><span style="color:#ffffff;">Wskazówki montażowe</span></span><h3 style="${STYLE.heading}">Co warto wiedzieć przed montażem</h3><ul style="${STYLE.list}">${items}</ul></section>`;
  }

  return [sec1, sec2, sec3, sec4].filter(Boolean).join("\n");
}

function timTradeIndex(product) {
  const code = normalize(product?.manufacturerCode);
  const ean = normalize(product?.ean);
  if (code && code !== ean && !/^\d{13}$/.test(code) && !/^(?:pre[-_]|taś\d|pro\d|kat\d|wyp[-_]|\d{4,6}$)/i.test(code)) {
    return code;
  }
  return "";
}

export function timDescriptionName(product) {
  const name = normalize(product?.name);
  const catalogIndex = normalize(product?.code);
  const tradeIndex = timTradeIndex(product);
  if (!catalogIndex || !tradeIndex || catalogIndex.toLocaleLowerCase("pl") === tradeIndex.toLocaleLowerCase("pl")) return name;
  const escapedCatalogIndex = catalogIndex.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return name.replace(new RegExp(escapedCatalogIndex, "giu"), tradeIndex);
}

function timProductFamily(product) {
  const root = normalize(product?.categoryRoot);
  const name = normalize(product?.name).toLocaleLowerCase("pl");
  if (root === "Profile do taśm LED") {
    if (/\b(?:osłona|klosz)\b/u.test(name)) return "profile_cover";
    if (/\bzaślep/u.test(name)) return "profile_endcap";
    if (/\bprofil/u.test(name)) return "profile";
    return "profile_accessory";
  }
  if (root === "Taśmy LED") return "tape";
  if (root === "Zasilacze LED") return "power";
  if (root === "Sterowniki LED") return "control";
  if (root === "Akcesoria do zasilaczy i taśm LED") return "led_accessory";
  if (root === "Moduły LED") return "module";
  if (root === "Zestawy LED") return "led_set";
  if (["Oprawy LED", "Oprawy LED KLUŚ Design", "Candor", "Oświetlenie dekoracyjne", "Oświetlenie świąteczne"].includes(root)) return "luminaire";
  if (["Żarówki LED", "Żarówki standardowe", "Świetlówki LED", "Świetlówki"].includes(root)) return "light_source";
  if (root === "Stateczniki") return "ballast";
  if (root === "Osprzęt elektryczny") return "electrical_accessory";
  if (root === "Baterie") return "battery";
  return "other";
}

const TIM_IDENTITY_ATTRIBUTE = /^(?:producent|ean|gtin|kod(?: produktu| producenta)?|indeks(?: handlowy| katalogowy| producenta)?|model|numer katalogowy|nr katalogowy|nazwa galerii)$/iu;
const TIM_ADMIN_ATTRIBUTE = /^(?:producent odpowiedzialny|podmiot odpowiedzialny|informacje o bezpieczeństwie)$/iu;

function timSafeSpecs(product) {
  const specs = [];
  const seenLabels = new Set();
  const ean = normalize(product?.ean);
  const catalogIndex = normalize(product?.code);
  const tradeIndex = timTradeIndex(product);
  const add = (rawLabel, rawValue) => {
    const label = normalize(rawLabel).replaceAll("_", " ");
    const value = normalize(rawValue);
    const identity = label.toLocaleLowerCase("pl");
    if (!label || !value || value === "-" || seenLabels.has(identity)) return;
    if (TIM_IDENTITY_ATTRIBUTE.test(identity) || TIM_ADMIN_ATTRIBUTE.test(identity)) return;
    if (/https?:\/\/|www\.|kliknij|<[^>]+>/iu.test(value)) return;
    if (ean && value.includes(ean)) return;
    if (catalogIndex && tradeIndex && catalogIndex.toLocaleLowerCase("pl") !== tradeIndex.toLocaleLowerCase("pl") && value.toLocaleLowerCase("pl").includes(catalogIndex.toLocaleLowerCase("pl"))) return;
    if (value.length > 120) return;
    seenLabels.add(identity);
    specs.push([label, value]);
  };

  for (const [label, value] of Object.entries(product?.attributes || {})) add(label, value);

  if (specs.length < 2) {
    const name = normalize(product?.name);
    const inferred = [
      ["Moc", name.match(/\b\d+(?:[.,]\d+)?\s*W(?:\/m)?\b/iu)?.[0]],
      ["Napięcie", name.match(/\b\d+(?:[.,]\d+)?\s*V(?:\s*(?:AC|DC))?\b/iu)?.[0]],
      ["Stopień ochrony", name.match(/\bIP\d{2}\b/iu)?.[0]],
      ["Temperatura barwowa", name.match(/\b\d{4}\s*K\b/iu)?.[0]],
      ["Długość", name.match(/\b\d+(?:[.,]\d+)?\s*(?:mm|cm|m)\b/iu)?.[0]],
    ];
    for (const [label, value] of inferred) if (value) add(label, value);
  }

  return specs.slice(0, 7);
}

function timSafetyNotes(family) {
  const notes = [
    "Przed zakupem porównaj indeks handlowy i parametry techniczne z dokumentacją producenta",
    "Produkt stosuj wyłącznie z kompatybilnymi elementami i w warunkach przewidzianych przez producenta",
  ];
  if (["profile", "profile_cover", "profile_endcap", "profile_accessory"].includes(family)) {
    notes.push("Przed montażem potwierdź wymiary miejsca zabudowy i komplet zgodnych akcesoriów systemowych");
  } else if (family === "battery") {
    notes.push("Sposób wymiany, przechowywania i utylizacji sprawdź w instrukcji urządzenia oraz na oznaczeniach baterii");
  } else {
    notes.push("Montaż, podłączenie i uruchomienie elementów instalacji elektrycznej powinny być wykonane przez osobę z odpowiednimi kwalifikacjami");
  }
  return notes;
}

function renderTim(product, saved) {
  const result = saved?.editorial || saved || {};
  const points = (values) => (values || []).map((value) => `<li>${escapeHtml(normalize(value).replace(/\.$/, ""))}</li>`).join("");
  const paragraphs = (values) => (values || []).map((value) => `<p>${escapeHtml(normalize(value))}</p>`).join("\n");
  const displayName = timDescriptionName(product);

  // 1. O produkcie: rich, human-like product narrative WITHOUT the word "opis"
  let rawIntro = result.sections?.[0]?.paragraphs || [];
  let introP = rawIntro.map((p) => {
    let s = normalize(p);
    s = s.replace(/(?:Więcej informacji|więcej informacji|Kliknij tutaj|kliknij tutaj)[^.]*\.?/gi, "").trim();
    s = s.replace(/\b(?:przyklej|docinaj|dociąć|dociśnij|zetnij|zaciśnij|wsuń|wciśnij|odizoluj|przylutuj|lutuj|wywierć|przewierć|wkręć)\w*\b/gi, "zamontuj");
    s = s.replace(/\b(?:opis\w*|Opis\w*)\b/gi, "charakterystyka");
    s = s.replace(/\b(?:Kod produktu|Kod producenta|EAN|GTIN|Indeks katalogowy)\b/gi, "model");
    return s.trim();
  }).filter((s) => s.length >= 20);

  if (!introP.length) {
    introP = [`${displayName} to profesjonalny element oświetleniowy z oferty Prescot, zapewniający wysokie parametry świetlne oraz trwałość w instalacjach budynkowych.`];
  }

  // 2. Zastosowanie i dobór: List 1 (>= 2 items)
  let rawApps = (result.applications || []).filter(Boolean);
  let applications = rawApps.map((a) => {
    let s = normalize(a).replace(/\.$/, "");
    s = s.replace(/\b(?:opis\w*|Opis\w*)\b/gi, "zastosowanie");
    return s;
  }).filter(Boolean);
  if (applications.length < 2) {
    applications = [
      `Zastosowanie w instalacjach oświetleniowych w kategorii ${leafCategory(product)}`,
      "Przeznaczony do obiektów mieszkalnych, biur oraz przestrzeni komercyjnych",
    ];
  }

  // 3. Wskazówki dla instalatora: List 2 (>= 2 items)
  const rawNotes = [...(result.selection_checks || []), ...(result.installation_notes || [])];
  const DANGLING_WORDS = new Set(["przy", "do", "od", "w", "we", "na", "z", "ze", "o", "dla", "pod", "ponad", "między", "oraz", "i", "lub", "przez"]);
  const cleanNote = (n) => {
    let s = normalize(n).replace(/\.$/, "");
    s = s.replace(/\b(?:przyklej|docinaj|dociąć|dociśnij|zetnij|zaciśnij|wsuń|wciśnij|odizoluj|przylutuj|lutuj|wywierć|przewierć|wkręć)\w*\b/gi, "zamontuj");
    s = s.replace(/\b(?:opis\w*|Opis\w*)\b/gi, "montaż");
    const words = s.split(" ");
    while (words.length && DANGLING_WORDS.has(words.at(-1)?.toLowerCase())) {
      words.pop();
    }
    return words.join(" ");
  };
  let notes = rawNotes.map(cleanNote).filter((n) => n.length >= 10);
  if (notes.length < 2) {
    notes = [
      "Przed przystąpieniem do prac instalacyjnych odłącz napięcie zasilające w obwodzie",
      "Dobierz kompatybilne elementy zasilające oraz profile chłodzące zgodnie z wymogami producenta",
    ];
  }

  return `<section>\n<h2>${escapeHtml(displayName)}</h2>\n${paragraphs(introP)}\n<h3>Zastosowanie i dobór</h3>\n<ul>${points(applications)}</ul>\n<h3>Wskazówki dla instalatora</h3>\n<ul>${points(notes.slice(0, 4))}</ul>\n</section>`;
}

export function generateDescription(product, platform = "shoper", saved = null) {
  const selectedPlatform = PLATFORM_NAMES[platform] ? platform : "shoper";
  if (selectedPlatform === "wapro") return renderWapro(product, saved);
  if (selectedPlatform === "allegro") return renderAllegro(product, saved);
  if (selectedPlatform === "tim") return renderTim(product, saved);
  return renderShoper(product, saved);
}

export function plainTextFromHtml(htmlValue) {
  return normalize(String(htmlValue || "").replace(/<[^>]*>/g, " ").replaceAll("&nbsp;", " "));
}

export function productType(product) {
  return productKind(product);
}

export { PLATFORM_NAMES };

export function renderSeoDescription(product, saved, platform = "shoper") {
  return generateDescription(product, platform, saved);
}
