import { generateDescription, normalizeDescriptionIdentity, PLATFORM_NAMES, plainTextFromHtml, timTradeIndex } from "./description-engine.js";

const PAGE_SIZE = 30;

const PLATFORM_TABS = [
  ["wapro", "WAPRO ERP", "./ikona wapro.png"],
  ["tim", "TIM", "./ikona tim.jpg"],
  ["allegro", "Allegro", "./ikona allegro.png"],
  ["shoper", "Shoper", "./ikona_shoper.svg"],
];

const ICONS = {
  tapes: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 14c.2-1 .7-1.7 1.5-2.5C17.5 10.6 18 9.3 18 8A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.9 1.2 1.5 1.5 2.5"/><path d="M9 18h6M10 22h4"/></svg>',
  controllers: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h7M15 4h5M4 12h3M11 12h9M4 20h9M17 20h3"/><path d="M11 1v6M7 9v6M17 17v6"/></svg>',
  power: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m13 2-10 12h9l-1 8 10-12h-9z"/></svg>',
  profiles: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21 8-9 5-9-5 9-5zM3 8v8l9 5 9-5V8M12 13v8"/></svg>',
  accessories: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/></svg>',
  other: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16v13H4zM8 3h8v4M8 11h8M8 15h5"/></svg>',
};

const FAMILIES = [
  { key: "tapes", label: "Taśmy LED", root: "Taśmy LED" },
  { key: "controllers", label: "Sterowniki LED", root: "Sterowniki LED" },
  { key: "power", label: "Zasilacze LED", root: "Zasilacze LED" },
  { key: "profiles", label: "Profile KLUŚ", root: "Profile do taśm LED" },
  { key: "accessories", label: "Złączki i akcesoria LED", root: "Akcesoria do zasilaczy i taśm LED" },
  { key: "other", label: "Pozostałe aktywne", root: "__other__" },
];

const state = {
  catalog: null,
  overrides: null,
  generated: null,
  timStatus: null,
  platform: "wapro",
  family: "tapes",
  query: "",
  page: 1,
  openKeys: new Set(),
  localEdits: loadLocalEdits(),
};

const elements = {
  app: document.querySelector("#app"),
  loading: document.querySelector("#loading"),
  error: document.querySelector("#error"),
  cloudState: document.querySelector("#cloud-state"),
  search: document.querySelector("#search-input"),
  platformTabs: document.querySelector("#platform-tabs"),
  familyTabs: document.querySelector("#family-tabs"),
  resultSummary: document.querySelector("#result-summary"),
  productList: document.querySelector("#product-list"),
  pagination: document.querySelector("#pagination"),
  expandAll: document.querySelector("#expand-all"),
  collapseAll: document.querySelector("#collapse-all"),
  exportEdits: document.querySelector("#export-edits"),
  importEdits: document.querySelector("#import-edits"),
  importEditsFile: document.querySelector("#import-edits-file"),
  clearEdits: document.querySelector("#clear-edits"),
  bufferState: document.querySelector("#buffer-state"),
};

const TIM_STATUS_LABELS = {
  ready: "opis gotowy do mapowania",
  review: "do weryfikacji",
  blocked: "zablokowany",
  out_of_scope: "poza zakresem TIM",
};

const TIM_REASON_LABELS = {
  missing_or_invalid_ean: "brak prawidłowego 13-cyfrowego EAN",
  duplicate_ean: "EAN powtarza się w katalogu",
  nonpositive_price: "cena źródłowa wynosi 0 lub mniej",
  zero_stock: "stan źródłowy wynosi 0",
  source_research_pending: "research danych źródłowych nie jest zakończony",
  source_description_empty: "opis źródłowy jest pusty",
  eprel_variant_requires_evidence: "EPREL: wariant wymaga dokumentu producenta",
  eprel_candidate_model_mismatch: "EPREL: identyfikator modelu nie zgadza się z kartą",
  eprel_official_pdf_missing: "EPREL: brak oficjalnego PDF",
};

function loadLocalEdits() {
  try {
    return JSON.parse(localStorage.getItem("prescot-description-edits") || "{}");
  } catch {
    return {};
  }
}

function persistLocalEdits() {
  localStorage.setItem("prescot-description-edits", JSON.stringify(state.localEdits));
}

function normalize(value) {
  return String(value ?? "").toLocaleLowerCase("pl").replace(/\s+/g, " ").trim();
}

function display(value) {
  return String(value ?? "").replace(/\s+/g, " ").trim();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function attribute(product, ...labels) {
  const entries = Object.entries(product.attributes || {});
  for (const label of labels) {
    const wanted = normalize(label).replaceAll("_", " ");
    const found = entries.find(([key, value]) => normalize(key).replaceAll("_", " ") === wanted && display(value) && value !== "-");
    if (found) return display(found[1]);
  }
  return "";
}

function familyFor(product) {
  const match = FAMILIES.find((family) => family.root !== "__other__" && product.categoryRoot === family.root);
  return match?.key || "other";
}

function timStateFor(product) {
  return state.timStatus?.products?.[product.key] || { status: "out_of_scope", hardBlocks: [], reviewFlags: [], nameWarnings: [], eprelStatus: "not_assigned" };
}

function platformProducts() {
  if (state.platform !== "tim") return state.catalog.products;
  return state.catalog.products.filter((product) => timStateFor(product).status !== "out_of_scope");
}

function familyCounts() {
  const counts = Object.fromEntries(FAMILIES.map((family) => [family.key, 0]));
  for (const product of platformProducts()) counts[familyFor(product)] += 1;
  return counts;
}

function editKey(product, platform = state.platform) {
  return `${product.key}::${platform}`;
}

function manualOverrideId(product, platform = state.platform) {
  const assignment = state.overrides.products?.[product.key];
  if (!assignment) return "";
  // Historyczne pole `wapro` zawiera bogaty, pomarańczowy układ sklepu.
  // Proste ręczne wpisy zawierają miejscami stare wartości, dlatego WAPRO
  // zawsze renderujemy na nowo w klasycznym układzie z aktualnych danych.
  let id = platform === "shoper" ? assignment.wapro : assignment[platform];
  id ||= "";
  // 45 dawnych wpisów bogatego układu ma po właściwej czwartej sekcji drugi,
  // doklejony blok blogowy. Część zawiera też parametry sprzed aktualizacji
  // chmury (np. 900 zamiast 1000 lm/m). Nie wolno ich ponownie publikować.
  if (platform === "shoper" && id && state.overrides.descriptions?.[id]?.includes('class="blog-grid"')) return "";
  // TIM zawsze dostaje aktualny, czysty opis techniczny. Allegro nie przejmuje
  // starego układu sklepowego, jeśli kiedyś wskazywało ten sam rekord.
  if (["wapro", "tim"].includes(platform)) return "";
  if (platform === "allegro" && id && id === assignment.wapro) return "";
  return id;
}

function hasManualOverride(product, platform = state.platform) {
  const id = manualOverrideId(product, platform);
  return Boolean(id && state.overrides.descriptions?.[id]);
}

function hasLocalEdit(product, platform = state.platform) {
  return Object.hasOwn(state.localEdits, editKey(product, platform));
}

function descriptionFor(product, platform = state.platform) {
  const key = editKey(product, platform);
  let html = "";
  if (Object.hasOwn(state.localEdits, key)) html = state.localEdits[key];
  const overrideId = manualOverrideId(product, platform);
  if (!html && overrideId && state.overrides.descriptions?.[overrideId]) html = state.overrides.descriptions[overrideId];
  const saved = state.generated.products?.[product.key];
  if (!html) html = generateDescription(product, platform, saved?.editorial || saved);
  return normalizeDescriptionIdentity(product, html, { ensureTradeIndex: platform !== "tim", preserveManufacturerCode: platform === "tim" });
}

function descriptionOrigin(product) {
  if (hasLocalEdit(product)) return ["edycja robocza", "edited"];
  if (hasManualOverride(product)) return ["wariant autorski", "manual"];
  return ["standard handlowy", "generated"];
}

function productSearchText(product) {
  if (product._searchText) return product._searchText;
  const editorial = state.generated.products?.[product.key]?.editorial;
  product._searchText = normalize([
    product.name,
    product.category,
    product.producer,
    product.code,
    product.manufacturerCode,
    product.ean,
    product.sourceDescription,
    Object.entries(product.attributes || {}).flat().join(" "),
    editorial?.seo_title,
    ...(editorial?.sections || []).flatMap((section) => [section.label, section.heading, ...(section.paragraphs || [])]),
  ].join(" "));
  return product._searchText;
}

function filteredProducts() {
  const terms = normalize(state.query).split(" ").filter(Boolean);
  return platformProducts().filter((product) => {
    if (terms.length) {
      const searchable = productSearchText(product);
      return terms.every((term) => searchable.includes(term));
    }
    return familyFor(product) === state.family;
  });
}

function currentPageProducts() {
  const products = filteredProducts();
  const start = (state.page - 1) * PAGE_SIZE;
  return products.slice(start, start + PAGE_SIZE);
}

function renderPlatformTabs() {
  elements.platformTabs.innerHTML = PLATFORM_TABS.map(([key, label, image]) => (
    `<button class="main-tab-btn${state.platform === key ? " active" : ""}" type="button" data-platform="${key}" aria-pressed="${state.platform === key}"><img src="${image}" alt="${escapeHtml(label)}"></button>`
  )).join("");
  document.body.className = `platform-${state.platform}`;
}

function renderFamilyTabs() {
  const counts = familyCounts();
  elements.familyTabs.innerHTML = FAMILIES.map((family) => (
    `<button class="family-tab${state.family === family.key ? " active" : ""}" type="button" data-family="${family.key}" aria-pressed="${state.family === family.key}">${ICONS[family.key]}<span>${escapeHtml(family.label)}<br>(${counts[family.key].toLocaleString("pl-PL")})</span></button>`
  )).join("");
}

function productIdentifier(product) {
  return timTradeIndex(product) || "brak indeksu handlowego";
}

function matchFromName(product, pattern) {
  return display(product.name.match(pattern)?.[0] || "");
}

function productBadge(product) {
  const family = familyFor(product);
  if (family === "tapes") {
    const values = [
      attribute(product, "Barwa światła"),
      matchFromName(product, /\b\d{4,5}\s*K\b/i),
      matchFromName(product, /\b(?:ciepła biała|neutralna biała|zimna biała|niebieska|zielona|żółta|czerwona|pomarańczowa|różowa)\b/i),
      matchFromName(product, /\b(?:12|24|36|48)\s*V\b/i),
      matchFromName(product, /\bIP\s*\d{2}\b/i),
      attribute(product, "Jasność"),
      matchFromName(product, /\b\d+(?:[.,]\d+)?\s*lm\s*\/\s*m\b/i),
      matchFromName(product, /\b(?:rolka\s*)?\d+(?:[.,]\d+)?\s*m\b/i),
    ].filter(Boolean);
    return [...new Set(values)].slice(0, 4).join(" · ") || display(product.name).replace(/^taśma\s+led\s*/i, "").slice(0, 72);
  }
  if (family === "power") {
    const values = [attribute(product, "Napięcie Wyjściowe"), matchFromName(product, /\b(?:12|24|36|48)\s*V\b/i), attribute(product, "Moc"), matchFromName(product, /\b\d+(?:[.,]\d+)?\s*W\b/i)];
    return [...new Set(values.filter(Boolean))].slice(0, 3).join(" · ") || product.category.split("/").at(-1);
  }
  if (family === "controllers") {
    const values = [matchFromName(product, /\b(?:MONO|CCT|RGB\+?CCT|RGBW?|RF|Wi-?Fi)\b/ig)?.toUpperCase(), attribute(product, "Komunikacja"), matchFromName(product, /\b\d+(?:[.,]\d+)?\s*A\b/i)];
    return [...new Set(values.filter(Boolean))].slice(0, 3).join(" · ") || "sterowanie LED";
  }
  return [product.producer, product.category.split("/").at(-1)].filter(Boolean).join(" · ");
}

function parameterEntries(product) {
  const hidden = new Set(["producent", "kod produktu", "kod producenta", "ean", "producent odpowiedzialny", "podmiot odpowiedzialny", "informacje o bezpieczeństwie", "nazwa galerii"]);
  const result = [];
  const seen = new Set();
  for (const [rawLabel, rawValue] of Object.entries(product.attributes || {})) {
    const label = display(rawLabel).replaceAll("_", " ");
    const value = display(rawValue);
    const key = normalize(label);
    if (!value || value === "-" || hidden.has(key) || seen.has(key)) continue;
    seen.add(key);
    result.push([label, value]);
  }
  return result;
}

function parameterSection(product) {
  const params = parameterEntries(product);
  const identity = [
    ["Producent", product.producer],
    ["Indeks handlowy", timTradeIndex(product)],
    ["EAN", product.ean],
  ].filter(([, value]) => value);
  const entries = [...params, ...identity];
  if (!entries.length) return "";
  return `<section class="parameter-section"><span class="parameter-label">Atrybuty</span><div class="parameter-grid">${entries.map(([label, value]) => `<div><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`).join("")}</div></section>`;
}

function sourceNumber(value, suffix = "") {
  const number = Number(String(value ?? "").replace(",", "."));
  if (!Number.isFinite(number)) return display(value) || "brak";
  return `${new Intl.NumberFormat("pl-PL", { maximumFractionDigits: 4 }).format(number)}${suffix}`;
}

function timReasonLabel(reason) {
  if (reason.startsWith("invalid_tim_description:")) return `opis TIM: ${reason.split(":").slice(1).join(":")}`;
  return TIM_REASON_LABELS[reason] || reason.replaceAll("_", " ");
}

function timOperationalSection(product) {
  if (state.platform !== "tim") return "";
  const status = timStateFor(product);
  const reasons = [...(status.hardBlocks || []), ...(status.reviewFlags || [])];
  const reasonList = reasons.length
    ? `<ul>${reasons.map((reason) => `<li>${escapeHtml(timReasonLabel(reason))}</li>`).join("")}</ul>`
    : "<p>Brak blokad treści. Przed importem nadal wymagane jest mapowanie w aktualnym szablonie MarketTIM.</p>";
  const eprelLabels = {
    verified_exact_model: "zweryfikowany dokładny model",
    review_variant_model: "wariant do potwierdzenia",
    blocked_model_mismatch: "niedopasowany - zablokowany",
    blocked_missing_official_pdf: "brak oficjalnego PDF",
    not_assigned: "brak powiązania",
  };
  const eprelValue = status.verifiedEprelUrl
    ? `<a href="${escapeHtml(status.verifiedEprelUrl)}" target="_blank" rel="noopener">${escapeHtml(eprelLabels[status.eprelStatus] || status.eprelStatus)} ↗</a>`
    : escapeHtml(eprelLabels[status.eprelStatus] || status.eprelStatus || "brak");
  return `<section class="tim-operational tim-status-${escapeHtml(status.status)}">
    <div class="tim-operational-head"><strong>Kontrola TIM</strong><span>${escapeHtml(TIM_STATUS_LABELS[status.status] || status.status)}</span></div>
    <div class="tim-operational-grid">
      <div><span>EAN</span><strong>${escapeHtml(product.ean || "brak")}</strong></div>
      <div><span>Producent XML</span><strong>${escapeHtml(product.producer || "brak")}</strong></div>
      <div><span>Cena źródłowa WAPRO</span><strong>${escapeHtml(sourceNumber(product.price, " zł"))}</strong></div>
      <div><span>Stan źródłowy WAPRO</span><strong>${escapeHtml(sourceNumber(product.stock))}</strong></div>
      <div><span>EPREL</span><strong>${eprelValue}</strong></div>
    </div>
    <div class="tim-reasons">${reasonList}</div>
  </section>`;
}

function productBody(product) {
  const description = descriptionFor(product);
  const [originLabel, originClass] = descriptionOrigin(product);
  return `<div class="product-body">
    <div class="description-preview" data-role="preview">${description}</div>
    ${["shoper", "tim"].includes(state.platform) ? "" : parameterSection(product)}
    ${timOperationalSection(product)}
    <div class="edit-panel" data-role="editor" hidden>
      <textarea class="edit-textarea" spellcheck="false">${escapeHtml(description)}</textarea>
      <div class="edit-actions">
        <button class="control-btn primary" type="button" data-action="save-edit">Zapisz opis</button>
        <button class="control-btn" type="button" data-action="cancel-edit">Anuluj</button>
        ${hasLocalEdit(product) ? '<button class="control-btn danger" type="button" data-action="reset-edit">Przywróć opis bazowy</button>' : ""}
      </div>
    </div>
    <div class="product-controls">
      <button class="control-btn" type="button" data-action="edit">Edytuj opis</button>
      <button class="control-btn" type="button" data-action="copy-html">Kopiuj HTML do ${escapeHtml(PLATFORM_NAMES[state.platform])}</button>
      ${product.url ? `<a class="control-btn control-link" href="${escapeHtml(product.url)}" target="_blank" rel="noopener">Karta produktu ↗</a>` : ""}
      <span class="origin-badge ${originClass}">${originLabel}</span>
      <span class="copy-status" data-role="copy-status" aria-live="polite"></span>
    </div>
  </div>`;
}

function productCard(product, index) {
  const open = state.openKeys.has(product.key);
  return `<article class="product-accordion${open ? " open" : ""}" data-key="${escapeHtml(product.key)}">
    <button class="product-trigger" type="button" data-action="toggle" aria-expanded="${open}">
      <span class="product-info">
        <span class="product-model">${index}. ${escapeHtml(productIdentifier(product))}</span>
        <span class="product-label-badge">${escapeHtml(productBadge(product))}</span>
      </span>
      <span class="product-arrow" aria-hidden="true">▼</span>
    </button>
    ${open ? productBody(product) : ""}
  </article>`;
}

function paginationButton(label, page, disabled = false, active = false) {
  return `<button type="button" data-page="${page}"${disabled ? " disabled" : ""}${active ? ' class="active"' : ""}>${label}</button>`;
}

function renderPagination(pages, count) {
  if (count <= PAGE_SIZE) {
    elements.pagination.innerHTML = "";
    return;
  }
  const candidates = new Set([1, pages, state.page - 2, state.page - 1, state.page, state.page + 1, state.page + 2]);
  const numbers = [...candidates].filter((page) => page >= 1 && page <= pages).sort((a, b) => a - b);
  const output = [paginationButton("←", state.page - 1, state.page === 1)];
  let previous = 0;
  for (const page of numbers) {
    if (previous && page - previous > 1) output.push("<span>…</span>");
    output.push(paginationButton(String(page), page, false, page === state.page));
    previous = page;
  }
  output.push(paginationButton("→", state.page + 1, state.page === pages));
  elements.pagination.innerHTML = output.join("");
}

function updateUrl() {
  const params = new URLSearchParams();
  if (state.query) params.set("q", state.query);
  if (state.platform !== "wapro") params.set("platform", state.platform);
  if (state.family !== "tapes") params.set("family", state.family);
  if (state.page > 1) params.set("page", String(state.page));
  const firstOpen = [...state.openKeys][0];
  if (firstOpen) params.set("product", firstOpen);
  const query = params.toString();
  history.replaceState(null, "", query ? `?${query}` : location.pathname);
}

function hydrateFromUrl() {
  const params = new URLSearchParams(location.search);
  const platform = params.get("platform");
  const family = params.get("family");
  if (PLATFORM_TABS.some(([key]) => key === platform)) state.platform = platform;
  if (FAMILIES.some((item) => item.key === family)) state.family = family;
  state.query = params.get("q") || "";
  state.page = Math.max(1, Number(params.get("page")) || 1);
  const open = params.get("product");
  if (open) state.openKeys.add(open);
}

function renderProducts() {
  const products = filteredProducts();
  const pages = Math.max(1, Math.ceil(products.length / PAGE_SIZE));
  if (state.page > pages) state.page = pages;
  const start = (state.page - 1) * PAGE_SIZE;
  const visible = products.slice(start, start + PAGE_SIZE);
  const family = FAMILIES.find((item) => item.key === state.family);
  const scope = state.query ? `wyników dla „${escapeHtml(state.query)}” we wszystkich rodzinach` : `produktów w rodzinie ${escapeHtml(family.label)}`;
  elements.resultSummary.innerHTML = `<strong>${products.length.toLocaleString("pl-PL")}</strong> ${scope} · kanał <strong>${escapeHtml(PLATFORM_NAMES[state.platform])}</strong>`;
  elements.productList.innerHTML = visible.length
    ? visible.map((product, offset) => productCard(product, start + offset + 1)).join("")
    : '<div class="empty-state"><strong>Brak aktywnych produktów dla tego wyszukiwania.</strong><span>Sprawdź EAN, kod albo fragment nazwy.</span></div>';
  renderPagination(pages, products.length);
  updateUrl();
}

function currentProduct(card) {
  return state.catalog.products.find((product) => product.key === card?.dataset.key);
}

async function copyDescription(product, button, status) {
  const value = descriptionFor(product);
  try {
    await navigator.clipboard.writeText(value);
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = value;
    document.body.append(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
  }
  const previous = button.textContent;
  button.textContent = "Skopiowano ✓";
  status.textContent = `HTML gotowy do wklejenia w ${PLATFORM_NAMES[state.platform]}.`;
  window.setTimeout(() => { button.textContent = previous; status.textContent = ""; }, 2200);
}

function validateTimDraft(product, html) {
  const documentNode = new DOMParser().parseFromString(String(html || ""), "text/html");
  const textValue = display(documentNode.body.textContent);
  const lists = [...documentNode.querySelectorAll("ul")];
  const errors = [];
  if (textValue.length < 180) errors.push("opis ma mniej niż 180 znaków");
  if (documentNode.querySelectorAll("section").length !== 1) errors.push("opis musi mieć dokładnie jedną sekcję");
  if (documentNode.querySelectorAll("h2").length !== 1 || documentNode.querySelectorAll("h3").length !== 3) errors.push("opis musi mieć jeden nagłówek H2 i trzy nagłówki H3");
  const tradeIndex = timTradeIndex(product);
  const minimumSpecs = tradeIndex ? 1 : 0;
  if (lists.length !== 3 || lists[0]?.querySelectorAll("li").length < 2 || lists[1]?.querySelectorAll("li").length < minimumSpecs || lists[2]?.querySelectorAll("li").length < 2) errors.push("opis musi mieć kompletne listy zastosowań, parametrów i zasad bezpieczeństwa");
  if (documentNode.querySelector("[style], table")) errors.push("style inline i tabele są niedozwolone");
  const headings = [...documentNode.querySelectorAll("h2, h3")].map((node) => normalize(node.textContent));
  if (!headings.some((heading) => heading.includes("co to jest"))) errors.push("brak wyjaśnienia, co to jest");
  if (!headings.some((heading) => heading.includes("zastosowanie i dobór"))) errors.push("brak zastosowania");
  if (!headings.some((heading) => heading.includes("parametry produktu"))) errors.push("brak parametrów");
  if (!headings.some((heading) => heading.includes("dobór i bezpieczeństwo"))) errors.push("brak zasad doboru i bezpieczeństwa");
  if (/Opis wyjaśnia funkcję produktu/i.test(textValue)) errors.push("opis zawiera ogólny tekst zastępczy zamiast definicji produktu");
  if (tradeIndex && !textValue.includes(tradeIndex)) errors.push("brak indeksu handlowego producenta");
  if (product.ean && textValue.includes(product.ean)) errors.push("opis powtarza EAN z karty produktu");
  if (/\b(?:PRE[-_ ]?\d+|TAŚ\d+|PRO\d+|KAT\d+|WYP[-_][\p{L}\p{N}_.-]*)\b/iu.test(textValue)) errors.push("opis zawiera wewnętrzny indeks katalogowy");
  return errors;
}

function renderBufferState() {
  const count = Object.keys(state.localEdits).length;
  elements.bufferState.textContent = `Bufor lokalny: ${count.toLocaleString("pl-PL")} ${count === 1 ? "zmiana" : "zmian"}`;
  elements.exportEdits.disabled = count === 0;
  elements.clearEdits.disabled = count === 0;
}

function handleProductAction(event) {
  const target = event.target.closest("[data-action]");
  if (!target) return;
  const card = target.closest(".product-accordion");
  const product = currentProduct(card);
  if (!product) return;
  const action = target.dataset.action;

  if (action === "toggle") {
    if (state.openKeys.has(product.key)) state.openKeys.delete(product.key);
    else state.openKeys.add(product.key);
    renderProducts();
    return;
  }

  const preview = card.querySelector("[data-role='preview']");
  const editor = card.querySelector("[data-role='editor']");
  const textarea = editor?.querySelector("textarea");
  if (action === "copy-html") {
    copyDescription(product, target, card.querySelector("[data-role='copy-status']"));
  } else if (action === "edit") {
    preview.hidden = true;
    editor.hidden = false;
    textarea.focus();
  } else if (action === "cancel-edit") {
    preview.hidden = false;
    editor.hidden = true;
    textarea.value = descriptionFor(product);
  } else if (action === "save-edit") {
    const value = textarea.value.trim();
    if (!value || plainTextFromHtml(value).length < 20) {
      window.alert("Opis jest pusty albo zbyt krótki.");
      return;
    }
    if (state.platform === "tim") {
      const errors = validateTimDraft(product, value);
      if (errors.length) {
        window.alert(`Opis TIM nie przeszedł kontroli:\n- ${errors.join("\n- ")}`);
        return;
      }
    }
    state.localEdits[editKey(product)] = value;
    persistLocalEdits();
    renderBufferState();
    renderProducts();
  } else if (action === "reset-edit") {
    delete state.localEdits[editKey(product)];
    persistLocalEdits();
    renderBufferState();
    renderProducts();
  }
}

function exportEdits() {
  const edits = Object.entries(state.localEdits).map(([key, description]) => {
    const [productKey, platform] = key.split("::");
    const product = state.catalog.products.find((item) => item.key === productKey);
    return {
      productKey,
      platform,
      ean: product?.ean || "",
      tradeIndex: product?.code || "",
      name: product?.name || "",
      description: product ? normalizeDescriptionIdentity(product, description, { ensureTradeIndex: platform !== "tim", preserveManufacturerCode: platform === "tim" }) : description,
    };
  });
  const blob = new Blob([JSON.stringify({ exportedAt: new Date().toISOString(), edits }, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `prescot-opisy-${new Date().toISOString().slice(0, 10)}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

async function importEdits(file) {
  let payload;
  try {
    payload = JSON.parse(await file.text());
  } catch {
    window.alert("Nie udało się odczytać pliku JSON bufora.");
    return;
  }
  const availablePlatforms = new Set(PLATFORM_TABS.map(([key]) => key));
  const products = new Map(state.catalog.products.map((product) => [product.key, product]));
  let imported = 0;
  let rejected = 0;
  for (const edit of payload?.edits || []) {
    const product = products.get(edit?.productKey);
    const platform = String(edit?.platform || "");
    const description = String(edit?.description || "").trim();
    if (!product || !availablePlatforms.has(platform) || plainTextFromHtml(description).length < 20) {
      rejected += 1;
      continue;
    }
    if (platform === "tim" && validateTimDraft(product, description).length) {
      rejected += 1;
      continue;
    }
    state.localEdits[editKey(product, platform)] = normalizeDescriptionIdentity(product, description, { ensureTradeIndex: platform !== "tim", preserveManufacturerCode: platform === "tim" });
    imported += 1;
  }
  persistLocalEdits();
  renderBufferState();
  renderProducts();
  window.alert(`Bufor: zaimportowano ${imported} zmian${rejected ? `, odrzucono ${rejected}` : ""}.`);
}

function bindEvents() {
  elements.platformTabs.addEventListener("click", (event) => {
    const button = event.target.closest("[data-platform]");
    if (!button) return;
    state.platform = button.dataset.platform;
    state.openKeys.clear();
    renderPlatformTabs();
    renderFamilyTabs();
    renderProducts();
  });
  elements.familyTabs.addEventListener("click", (event) => {
    const button = event.target.closest("[data-family]");
    if (!button) return;
    state.family = button.dataset.family;
    state.query = "";
    elements.search.value = "";
    state.page = 1;
    state.openKeys.clear();
    renderFamilyTabs();
    renderProducts();
  });
  let timer;
  elements.search.addEventListener("input", () => {
    window.clearTimeout(timer);
    timer = window.setTimeout(() => {
      state.query = elements.search.value;
      state.page = 1;
      state.openKeys.clear();
      renderProducts();
    }, 140);
  });
  elements.productList.addEventListener("click", handleProductAction);
  elements.pagination.addEventListener("click", (event) => {
    const button = event.target.closest("[data-page]");
    if (!button || button.disabled) return;
    state.page = Number(button.dataset.page);
    state.openKeys.clear();
    renderProducts();
    elements.resultSummary.scrollIntoView({ behavior: "smooth", block: "center" });
  });
  elements.expandAll.addEventListener("click", () => {
    for (const product of currentPageProducts()) state.openKeys.add(product.key);
    renderProducts();
  });
  elements.collapseAll.addEventListener("click", () => {
    state.openKeys.clear();
    renderProducts();
  });
  elements.exportEdits.addEventListener("click", exportEdits);
  elements.importEdits.addEventListener("click", () => elements.importEditsFile.click());
  elements.importEditsFile.addEventListener("change", async () => {
    const [file] = elements.importEditsFile.files;
    if (file) await importEdits(file);
    elements.importEditsFile.value = "";
  });
  elements.clearEdits.addEventListener("click", () => {
    if (!Object.keys(state.localEdits).length) return;
    if (!window.confirm("Usunąć wszystkie lokalne edycje opisów z tej przeglądarki?")) return;
    state.localEdits = {};
    persistLocalEdits();
    renderBufferState();
    renderProducts();
  });
}

async function initialize() {
  hydrateFromUrl();
  try {
    const responses = await Promise.all([
      fetch("./data/catalog.json", { cache: "no-cache" }),
      fetch("./data/manual-overrides.json", { cache: "no-cache" }),
      fetch("./data/seo-descriptions.json", { cache: "no-cache" }),
      fetch("./data/tim-status.json", { cache: "no-cache" }),
    ]);
    if (responses.some((response) => !response.ok)) throw new Error("Nie udało się pobrać danych katalogu.");
    [state.catalog, state.overrides, state.generated, state.timStatus] = await Promise.all(responses.map((response) => response.json()));
    elements.search.value = state.query;
    const date = new Date(state.catalog.meta.generatedAt);
    const updated = Number.isNaN(date.getTime()) ? state.catalog.meta.generatedAt : new Intl.DateTimeFormat("pl-PL", { dateStyle: "medium", timeStyle: "short" }).format(date);
    const timCounts = state.timStatus.meta.counts;
    elements.cloudState.textContent = `${state.catalog.meta.activeProducts.toLocaleString("pl-PL")} aktywnych produktów · TIM: ${timCounts.ready.toLocaleString("pl-PL")} opisów gotowych, ${timCounts.review.toLocaleString("pl-PL")} do kontroli, ${timCounts.blocked.toLocaleString("pl-PL")} zablokowanych · dane ${updated}`;
    renderPlatformTabs();
    renderFamilyTabs();
    bindEvents();
    renderBufferState();
    renderProducts();
    elements.loading.hidden = true;
    elements.app.hidden = false;
  } catch (error) {
    console.error(error);
    elements.loading.hidden = true;
    elements.error.hidden = false;
    elements.error.querySelector("span").textContent = error.message;
  }
}

initialize();
