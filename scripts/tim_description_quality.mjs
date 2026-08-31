import {
  normalizeDescriptionIdentity,
  plainTextFromHtml,
  renderSeoDescription,
  timDescriptionName,
  timTradeIndex,
} from "../description-engine.js";

const FORBIDDEN_TEXT = /Opis dla TIM\.pl|Dane techniczne|Producent\s*:|\bEAN\b|\bGTIN\b|\bKod produktu\b|\bKod producenta\b|\bIndeks katalogowy\b|\bNumer katalogowy\b|\bwyc\.?\b|Dane służą do porównania wariantu|Opis wyjaśnia funkcję produktu|Kliknij tutaj/i;
const PROCEDURAL_INSTALLATION_TEXT = /\b(?:przyklej|doci(?:ąć|nij)|zetnij|zaciśnij|wsuń|wciśnij|ściągnij izolację|odizoluj|przylutuj|lutuj|wywierć|przewierć|wkręć|podłącz kanał|połącz kanał)\b/iu;
const DANGLING_WORDS = new Set(["przy", "do", "od", "w", "we", "na", "z", "ze", "o", "dla", "pod", "ponad", "między", "oraz", "i", "lub", "przez"]);

function occurrences(value, pattern) {
  return (String(value || "").match(pattern) || []).length;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function listItems(html) {
  return [...String(html || "").matchAll(/<li>([\s\S]*?)<\/li>/gi)]
    .map((match) => plainTextFromHtml(match[1]));
}

export function danglingTimItems(html) {
  return listItems(html).filter((item) => {
    if (item.includes(":")) return false;
    const lastWord = item.toLocaleLowerCase("pl").split(/\s+/).at(-1)?.replace(/[.,;:!?]+$/g, "");
    return DANGLING_WORDS.has(lastWord);
  });
}

export function timBodyFingerprint(html) {
  return plainTextFromHtml(
    String(html || "").replace(/<h[23]>[\s\S]*?<\/h[23]>/gi, " "),
  ).toLocaleLowerCase("pl");
}

export function renderTimDescription(product, saved, editedHtml = "") {
  const html = editedHtml || renderSeoDescription(product, saved, "tim");
  return normalizeDescriptionIdentity(product, html, { ensureTradeIndex: false, preserveManufacturerCode: true });
}

export function validateTimDescription(product, html) {
  const errors = [];
  const text = plainTextFromHtml(html);
  const expectedUseHeading = "<h3>Zastosowanie i dobór</h3>";
  const expectedSpecsHeading = "<h3>Parametry produktu</h3>";
  const expectedSafetyHeading = "<h3>Dobór i bezpieczeństwo</h3>";
  const lists = [...String(html || "").matchAll(/<ul>([\s\S]*?)<\/ul>/gi)]
    .map((match) => occurrences(match[1], /<li\b/gi));

  if (text.length < 140) errors.push(`description_too_short:${text.length}`);
  if (occurrences(html, /<section\b/gi) !== 1 || occurrences(html, /<\/section>/gi) !== 1) errors.push("invalid_section_count");
  if (/\sstyle=/i.test(html)) errors.push("inline_style_not_allowed");
  if (/<table\b/i.test(html)) errors.push("table_not_allowed");
  if (/<a\b/i.test(html)) errors.push("link_not_allowed");
  if (FORBIDDEN_TEXT.test(text)) errors.push("repeated_card_identity_or_forbidden_word");
  if (PROCEDURAL_INSTALLATION_TEXT.test(text)) errors.push("procedural_installation_instruction");
  if (!String(html).includes(expectedUseHeading)) errors.push("missing_use_heading");
  if (!String(html).includes(expectedSpecsHeading)) errors.push("missing_specs_heading");
  if (!String(html).includes(expectedSafetyHeading)) errors.push("missing_safety_heading");
  if (occurrences(html, /<h2\b/gi) !== 1 || occurrences(html, /<h3\b/gi) !== 3) errors.push("invalid_heading_count");
  if (lists.length !== 3 || lists[0] < 2 || lists[1] < 1 || lists[2] < 2) errors.push("invalid_list_structure");

  const dangling = danglingTimItems(html);
  if (dangling.length) errors.push(`dangling_sentence:${dangling.join(" | ")}`);
  if (product.ean && text.includes(String(product.ean))) errors.push("ean_repeated_in_description");
  const tradeIndex = timTradeIndex(product);
  if (!tradeIndex) {
    errors.push("missing_trade_index_source");
  } else {
    const expectedTradeIndex = `Indeks handlowy: ${tradeIndex}`;
    if (!text.includes(expectedTradeIndex)) errors.push("missing_or_wrong_trade_index");
  }
  if (product.code && product.manufacturerCode && String(product.code).toLocaleLowerCase("pl") !== String(product.manufacturerCode).toLocaleLowerCase("pl")) {
    const escapedCatalogIndex = String(product.code).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    if (new RegExp(`(?:Indeks handlowy|model|kod)\\s*:\\s*${escapedCatalogIndex}(?:\\s|$)`, "iu").test(text)) errors.push("catalog_index_used_as_trade_index");
    if (/^(?:PRE(?:-|$)|Taś\d|Zas\d|Pro\d|Opr\d|Wyp\d|Kat\d|Swl\d|Osp\d)/iu.test(String(product.code)) && text.toLocaleLowerCase("pl").includes(String(product.code).toLocaleLowerCase("pl"))) errors.push("catalog_index_repeated_in_description");
  }

  return errors;
}
