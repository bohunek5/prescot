import { generateDescription, renderSeoDescription, PLATFORM_NAMES, plainTextFromHtml } from "./description-engine.js";

const PAGE_SIZE = 30;
const state = {
  catalog: null,
  overrides: null,
  generated: null,
  platform: "shoper",
  query: "",
  category: "",
  descriptionType: "all",
  page: 1,
  openKey: "",
  localEdits: loadLocalEdits(),
};

const elements = {
  app: document.querySelector("#app"),
  loading: document.querySelector("#loading"),
  error: document.querySelector("#error"),
  platformTabs: document.querySelector("#platform-tabs"),
  search: document.querySelector("#search"),
  category: document.querySelector("#category-filter"),
  descriptionType: document.querySelector("#description-filter"),
  resultSummary: document.querySelector("#result-summary"),
  productList: document.querySelector("#product-list"),
  pagination: document.querySelector("#pagination"),
  statProducts: document.querySelector("#stat-products"),
  statEan: document.querySelector("#stat-ean"),
  statOverrides: document.querySelector("#stat-overrides"),
  statUpdated: document.querySelector("#stat-updated"),
  exportEdits: document.querySelector("#export-edits"),
  clearEdits: document.querySelector("#clear-edits"),
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

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function productSearchText(product) {
  if (product._searchText) return product._searchText;
  product._searchText = normalize([
    product.name,
    product.category,
    product.producer,
    product.code,
    product.manufacturerCode,
    product.ean,
    Object.values(product.attributes || {}).join(" "),
  ].join(" "));
  return product._searchText;
}

function editKey(product, platform = state.platform) {
  return `${product.key}::${platform}`;
}

function manualOverrideId(product, platform = state.platform) {
  return state.overrides.products?.[product.key]?.[platform] || "";
}

function hasManualOverride(product, platform = state.platform) {
  return Boolean(manualOverrideId(product, platform));
}

function hasLocalEdit(product, platform = state.platform) {
  return Object.hasOwn(state.localEdits, editKey(product, platform));
}

function descriptionFor(product, platform = state.platform) {
  const key = editKey(product, platform);
  if (Object.hasOwn(state.localEdits, key)) return state.localEdits[key];
  const overrideId = manualOverrideId(product, platform);
  if (overrideId && state.overrides.descriptions?.[overrideId]) {
    return state.overrides.descriptions[overrideId];
  }
  const generated = state.generated.products?.[product.key];
  if (generated?.editorial) return renderSeoDescription(product, generated, platform);
  return generateDescription(product, platform);
}

function descriptionOrigin(product) {
  if (hasLocalEdit(product)) return { label: "edycja lokalna", className: "origin-local" };
  if (hasManualOverride(product)) return { label: "opis ręczny", className: "origin-manual" };
  if (state.generated.products?.[product.key]?.editorial) return { label: "opis SEO po audycie", className: "origin-generated" };
  return { label: "opis z danych", className: "origin-generated" };
}

function matchesDescriptionType(product) {
  if (state.descriptionType === "manual") return hasManualOverride(product);
  if (state.descriptionType === "generated") return !hasManualOverride(product);
  if (state.descriptionType === "edited") return hasLocalEdit(product);
  if (state.descriptionType === "missing-ean") return !product.ean;
  return true;
}

function filteredProducts() {
  const terms = normalize(state.query).split(" ").filter(Boolean);
  return state.catalog.products.filter((product) => {
    if (state.category && product.categoryRoot !== state.category) return false;
    if (!matchesDescriptionType(product)) return false;
    if (!terms.length) return true;
    const searchable = productSearchText(product);
    return terms.every((term) => searchable.includes(term));
  });
}

function renderPlatformTabs() {
  elements.platformTabs.innerHTML = Object.entries(PLATFORM_NAMES).map(([key, label]) => (
    `<button class="platform-tab platform-${key}${state.platform === key ? " active" : ""}" data-platform="${key}" type="button"><span>${escapeHtml(label)}</span></button>`
  )).join("");
}

function renderCategoryOptions() {
  const options = Object.entries(state.catalog.meta.categoryRoots || {});
  elements.category.innerHTML = [
    `<option value="">Wszystkie kategorie (${state.catalog.meta.activeProducts})</option>`,
    ...options.map(([name, count]) => `<option value="${escapeHtml(name)}">${escapeHtml(name)} (${count})</option>`),
  ].join("");
  elements.category.value = state.category;
}

function productIdentifier(product) {
  return product.manufacturerCode || product.code || product.ean || `ID ${product.id}`;
}

function stockLabel(product) {
  const numeric = Number(String(product.stock || "0").replace(",", "."));
  if (!Number.isFinite(numeric)) return "aktywny";
  if (numeric > 0) return `stan: ${new Intl.NumberFormat("pl-PL", { maximumFractionDigits: 2 }).format(numeric)}`;
  return "aktywny • stan 0";
}

function productCard(product, index) {
  const origin = descriptionOrigin(product);
  const isOpen = state.openKey === product.key;
  const price = product.price ? `${String(product.price).replace(".", ",")} zł` : "";
  const ean = product.ean || "brak EAN — używany kod produktu";
  const image = product.image
    ? `<img src="${escapeHtml(product.image)}" alt="" loading="lazy" width="72" height="72">`
    : `<span class="image-placeholder" aria-hidden="true">LED</span>`;
  return `
    <article class="product-card${isOpen ? " open" : ""}" data-key="${escapeHtml(product.key)}">
      <button class="product-summary" type="button" aria-expanded="${isOpen}" data-action="toggle">
        <span class="product-image">${image}</span>
        <span class="product-main">
          <span class="product-index">${index + 1}. ${escapeHtml(productIdentifier(product))}</span>
          <strong>${escapeHtml(product.name)}</strong>
          <span class="product-category">${escapeHtml(product.category)}</span>
          <span class="product-meta">
            <span>EAN: ${escapeHtml(ean)}</span>
            ${price ? `<span>${escapeHtml(price)}</span>` : ""}
            <span>${escapeHtml(stockLabel(product))}</span>
          </span>
        </span>
        <span class="product-badges">
          <span class="origin-badge ${origin.className}">${origin.label}</span>
          <span class="chevron" aria-hidden="true">⌄</span>
        </span>
      </button>
      ${isOpen ? productBody(product) : ""}
    </article>`;
}

function productBody(product) {
  const htmlValue = descriptionFor(product);
  const origin = descriptionOrigin(product);
  const technical = [
    product.producer && ["Producent", product.producer],
    product.code && ["Kod produktu", product.code],
    product.manufacturerCode && ["Kod producenta", product.manufacturerCode],
    product.ean && ["EAN", product.ean],
    ["ID w chmurze", product.id],
  ].filter(Boolean);

  return `
    <div class="product-body">
      <div class="product-toolbar">
        <div>
          <strong>${escapeHtml(PLATFORM_NAMES[state.platform])}</strong>
          <span class="origin-badge ${origin.className}">${origin.label}</span>
        </div>
        <div class="toolbar-actions">
          <button type="button" class="button button-secondary" data-action="copy-html">Kopiuj opis HTML</button>
          <button type="button" class="button button-secondary" data-action="edit">Edytuj</button>
          ${product.url ? `<a class="button button-link" href="${escapeHtml(product.url)}" target="_blank" rel="noopener">Karta produktu ↗</a>` : ""}
        </div>
      </div>
      <div class="description-preview" data-role="preview">${htmlValue}</div>
      <div class="editor" data-role="editor" hidden>
        <label>Opis HTML dla kanału ${escapeHtml(PLATFORM_NAMES[state.platform])}</label>
        <textarea spellcheck="false">${escapeHtml(htmlValue)}</textarea>
        <div class="editor-actions">
          <button type="button" class="button button-primary" data-action="save-edit">Zapisz lokalnie</button>
          <button type="button" class="button button-secondary" data-action="cancel-edit">Anuluj</button>
          ${hasLocalEdit(product) ? `<button type="button" class="button button-danger" data-action="reset-edit">Przywróć opis bazowy</button>` : ""}
        </div>
        <p>Edycja zapisuje się w tej przeglądarce. Użyj „Eksportuj edycje”, aby przekazać zmiany do publikacji.</p>
      </div>
      <dl class="identity-grid">
        ${technical.map(([label, value]) => `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`).join("")}
      </dl>
    </div>`;
}

function renderProducts() {
  const products = filteredProducts();
  const pages = Math.max(1, Math.ceil(products.length / PAGE_SIZE));
  if (state.page > pages) state.page = pages;
  const start = (state.page - 1) * PAGE_SIZE;
  const visible = products.slice(start, start + PAGE_SIZE);

  elements.resultSummary.innerHTML = `<strong>${products.length.toLocaleString("pl-PL")}</strong> wyników • kanał <strong>${escapeHtml(PLATFORM_NAMES[state.platform])}</strong>`;
  if (!visible.length) {
    elements.productList.innerHTML = `<div class="empty-state"><strong>Brak produktów dla tych filtrów.</strong><span>Wyczyść wyszukiwanie albo wybierz inną kategorię.</span></div>`;
  } else {
    elements.productList.innerHTML = visible.map((product, index) => productCard(product, start + index)).join("");
  }
  renderPagination(pages, products.length);
  updateUrl();
}

function paginationButton(label, page, disabled = false, active = false) {
  return `<button type="button" data-page="${page}"${disabled ? " disabled" : ""} class="${active ? "active" : ""}">${label}</button>`;
}

function renderPagination(pages, count) {
  if (count <= PAGE_SIZE) {
    elements.pagination.innerHTML = "";
    return;
  }
  const candidates = new Set([1, pages, state.page - 2, state.page - 1, state.page, state.page + 1, state.page + 2]);
  const pageNumbers = [...candidates].filter((page) => page >= 1 && page <= pages).sort((a, b) => a - b);
  const parts = [paginationButton("←", state.page - 1, state.page === 1)];
  let previous = 0;
  for (const page of pageNumbers) {
    if (previous && page - previous > 1) parts.push("<span>…</span>");
    parts.push(paginationButton(String(page), page, false, page === state.page));
    previous = page;
  }
  parts.push(paginationButton("→", state.page + 1, state.page === pages));
  elements.pagination.innerHTML = parts.join("");
}

function updateStats() {
  const meta = state.catalog.meta;
  elements.statProducts.textContent = meta.activeProducts.toLocaleString("pl-PL");
  elements.statEan.textContent = `${meta.withEan.toLocaleString("pl-PL")} / ${meta.activeProducts.toLocaleString("pl-PL")}`;
  elements.statOverrides.textContent = meta.manualOverrideProducts.toLocaleString("pl-PL");
  const date = new Date(meta.generatedAt);
  elements.statUpdated.textContent = new Intl.DateTimeFormat("pl-PL", { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function updateUrl() {
  const params = new URLSearchParams();
  if (state.query) params.set("q", state.query);
  if (state.category) params.set("category", state.category);
  if (state.platform !== "shoper") params.set("platform", state.platform);
  if (state.descriptionType !== "all") params.set("type", state.descriptionType);
  if (state.page > 1) params.set("page", String(state.page));
  if (state.openKey) params.set("product", state.openKey);
  const query = params.toString();
  history.replaceState(null, "", query ? `?${query}` : location.pathname);
}

function hydrateFromUrl() {
  const params = new URLSearchParams(location.search);
  const platform = params.get("platform");
  if (platform && PLATFORM_NAMES[platform]) state.platform = platform;
  state.query = params.get("q") || "";
  state.category = params.get("category") || "";
  state.descriptionType = params.get("type") || "all";
  state.page = Math.max(1, Number(params.get("page")) || 1);
  state.openKey = params.get("product") || "";
}

function currentProduct(card) {
  return state.catalog.products.find((product) => product.key === card.dataset.key);
}

async function copyText(text, button) {
  try {
    await navigator.clipboard.writeText(text);
    const original = button.textContent;
    button.textContent = "Skopiowano ✓";
    setTimeout(() => { button.textContent = original; }, 1800);
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.append(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
  }
}

function handleProductAction(event) {
  const actionTarget = event.target.closest("[data-action]");
  if (!actionTarget) return;
  const card = actionTarget.closest(".product-card");
  const product = card ? currentProduct(card) : null;
  if (!product) return;
  const action = actionTarget.dataset.action;

  if (action === "toggle") {
    state.openKey = state.openKey === product.key ? "" : product.key;
    renderProducts();
    if (state.openKey) requestAnimationFrame(() => document.querySelector(`[data-key="${CSS.escape(product.key)}"]`)?.scrollIntoView({ block: "nearest" }));
    return;
  }
  if (action === "copy-html") {
    copyText(descriptionFor(product), actionTarget);
    return;
  }

  const preview = card.querySelector("[data-role='preview']");
  const editor = card.querySelector("[data-role='editor']");
  const textarea = editor?.querySelector("textarea");
  if (action === "edit") {
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
      alert("Opis jest pusty albo zbyt krótki.");
      return;
    }
    state.localEdits[editKey(product)] = value;
    persistLocalEdits();
    renderProducts();
  } else if (action === "reset-edit") {
    delete state.localEdits[editKey(product)];
    persistLocalEdits();
    renderProducts();
  }
}

function exportEdits() {
  const entries = Object.entries(state.localEdits).map(([key, description]) => {
    const [productKey, platform] = key.split("::");
    const product = state.catalog.products.find((item) => item.key === productKey);
    return {
      productKey,
      platform,
      ean: product?.ean || "",
      code: product?.code || "",
      manufacturerCode: product?.manufacturerCode || "",
      name: product?.name || "",
      description,
    };
  });
  const blob = new Blob([JSON.stringify({ exportedAt: new Date().toISOString(), edits: entries }, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `prescot-opisy-${new Date().toISOString().slice(0, 10)}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

function bindEvents() {
  elements.platformTabs.addEventListener("click", (event) => {
    const button = event.target.closest("[data-platform]");
    if (!button) return;
    state.platform = button.dataset.platform;
    state.page = 1;
    state.openKey = "";
    renderPlatformTabs();
    renderProducts();
  });

  let searchTimer;
  elements.search.addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      state.query = elements.search.value;
      state.page = 1;
      state.openKey = "";
      renderProducts();
    }, 180);
  });
  elements.category.addEventListener("change", () => {
    state.category = elements.category.value;
    state.page = 1;
    state.openKey = "";
    renderProducts();
  });
  elements.descriptionType.addEventListener("change", () => {
    state.descriptionType = elements.descriptionType.value;
    state.page = 1;
    state.openKey = "";
    renderProducts();
  });
  elements.productList.addEventListener("click", handleProductAction);
  elements.pagination.addEventListener("click", (event) => {
    const button = event.target.closest("[data-page]");
    if (!button || button.disabled) return;
    state.page = Number(button.dataset.page);
    state.openKey = "";
    renderProducts();
    window.scrollTo({ top: elements.resultSummary.offsetTop - 120, behavior: "smooth" });
  });
  elements.exportEdits.addEventListener("click", exportEdits);
  elements.clearEdits.addEventListener("click", () => {
    if (!Object.keys(state.localEdits).length) return;
    if (!confirm("Usunąć wszystkie lokalne edycje opisów z tej przeglądarki?")) return;
    state.localEdits = {};
    persistLocalEdits();
    renderProducts();
  });
}

async function initialize() {
  hydrateFromUrl();
  try {
    const [catalogResponse, overridesResponse, generatedResponse] = await Promise.all([
      fetch("./data/catalog.json", { cache: "no-cache" }),
      fetch("./data/manual-overrides.json", { cache: "no-cache" }),
      fetch("./data/seo-descriptions.json", { cache: "no-cache" }),
    ]);
    if (!catalogResponse.ok || !overridesResponse.ok || !generatedResponse.ok) throw new Error("Nie udało się pobrać danych katalogu.");
    [state.catalog, state.overrides, state.generated] = await Promise.all([catalogResponse.json(), overridesResponse.json(), generatedResponse.json()]);
    renderPlatformTabs();
    renderCategoryOptions();
    elements.search.value = state.query;
    elements.descriptionType.value = state.descriptionType;
    updateStats();
    bindEvents();
    renderProducts();
    elements.loading.hidden = true;
    elements.app.hidden = false;
  } catch (error) {
    console.error(error);
    elements.loading.hidden = true;
    elements.error.hidden = false;
    elements.error.querySelector("p").textContent = error.message;
  }
}

initialize();
