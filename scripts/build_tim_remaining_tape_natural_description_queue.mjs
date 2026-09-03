import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

import { timDescriptionName, timTradeIndex } from "../description-engine.js";
import { validateTimDescription } from "./tim_description_quality.mjs";

const snapshotPath = resolve(process.argv[2]
  || "exports/tim/remediation/active-brand-offer-prescot-night-final-complete-2026-09-02.json");
const catalogPath = resolve(process.argv[3] || "data/catalog.json");
const outputPath = resolve(process.argv[4]
  || "exports/tim/remediation/prescot-active-positive-remaining-tape-natural-description-queue-2026-09-03.json");

const [snapshot, catalog] = await Promise.all([
  readFile(snapshotPath, "utf8").then(JSON.parse),
  readFile(catalogPath, "utf8").then(JSON.parse),
]);

const clean = (value) => String(value || "").replace(/\s+/gu, " ").trim();
const escapeHtml = (value) => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");
const canonical = (html) => String(html || "")
  .trim()
  .replace(/^<section>\s*/iu, "")
  .replace(/\s*<\/section>$/iu, "")
  .trim();

function oldDescriptionNeedsNaturalRewrite(html) {
  const source = String(html || "");
  const text = source.replace(/<[^>]+>/gu, " ");
  return !source
    || /\bEconomic\b|Opis dotyczy produktu|Indeks handlowy\s*:|Wariant ma moc|Jest to taśma LED do tworzenia|Zastosowanie i dobór|Parametry i cechy techniczne|Wskazówki montażowe i bezpieczeństwo/iu.test(text)
    || !source.includes("Barwa światła i zastosowanie")
    || !source.includes("Dobór i bezpieczeństwo");
}

function warrantyYears(product) {
  const name = clean(product.name);
  const explicit = name.match(/\b(?:PL)?([1-9])Y\b/iu)?.[1]
    || name.match(/\b([1-9])\s*(?:lat|lata|rok|roku)\s+gwarancji\b/iu)?.[1];
  if (explicit) return Number(explicit);
  const months = Number(clean(product.attributes?.Gwarancja).match(/\b(\d+)\b/u)?.[1] || 0);
  return months > 0 && months % 12 === 0 ? months / 12 : 0;
}

function seriesName(product) {
  const name = clean(product.name);
  const code = clean(product.manufacturerCode);
  if (/\bDelux\b|\bPL7Y\b/iu.test(name)) return "Delux";
  if (/\bStandard\b|\bEconomic\b/iu.test(name)) return "Standard";
  if (/\bPremium\b/iu.test(name) || /^EHP/iu.test(code) || /COB/iu.test(name)) return "Premium";
  if (/^PR|^EH(?!P)/iu.test(code)) return "Standard";
  return "";
}

function seriesBucket(product) {
  const series = seriesName(product) || "Other";
  const years = warrantyYears(product);
  return years ? `${series}${years}Y` : `${series}Unknown`;
}

function lightVariant(product) {
  const name = clean(product.name);
  const code = clean(product.manufacturerCode);
  const source = `${name} ${code}`;
  if (/RGB\s*\+\s*CCT|RGB.?CCT/iu.test(source)) return {
    lead: "Połączenie RGB i CCT pozwala uzyskać światło kolorowe oraz regulować odcień bieli.",
    use: "Sprawdzi się w salonach, strefach wypoczynku, ekspozycjach i instalacjach, w których potrzebne jest zarówno światło funkcjonalne, jak i dekoracyjne.",
    controller: "RGB+CCT",
  };
  if (/RGB\s*\+\s*(?:NW|W|WW)|RGBW/iu.test(source)) {
    const white = /RGB\s*\+\s*WW|RGB\+WW/iu.test(source) ? "ciepłej"
      : /RGB\s*\+\s*NW|RGB\+NW/iu.test(source) ? "neutralnej" : "chłodnej";
    return {
      lead: `Połączenie RGB z niezależnym kanałem bieli ${white} umożliwia tworzenie kolorowych scen i korzystanie z białego światła.`,
      use: "Sprawdzi się w salonach, witrynach, meblach, wnękach i strefach rozrywki, w których jedna instalacja ma pełnić funkcję dekoracyjną i użytkową.",
      controller: "RGBW",
    };
  }
  if (/\bCCT\b/iu.test(source)) return {
    lead: "Regulowana barwa biała pozwala przechodzić od ciepłego światła wypoczynkowego do chłodniejszego światła zadaniowego.",
    use: "Sprawdzi się w salonach, kuchniach, gabinetach i innych wnętrzach, w których charakter oświetlenia ma zmieniać się zależnie od pory dnia lub wykonywanej czynności.",
    controller: "CCT",
  };
  if (/\bRGB\b/iu.test(source)) return {
    lead: "Światło RGB pozwala tworzyć różne kolory i wyraźne efekty dekoracyjne.",
    use: "Sprawdzi się w podświetleniu witryn, mebli, wnęk, stref rozrywki i dekoracji wymagających zmiennego koloru światła.",
    controller: "RGB",
  };

  const colors = [
    [/\b(?:czerwon\p{L}*|red)\b|(?:^|-)R(?:\d|$|-)/iu, "Czerwone światło tworzy mocny, wyraźny akcent kolorystyczny.", "witryn, mebli, wnęk, dekoracji i oznaczeń, w których potrzebna jest jednolita czerwona linia światła"],
    [/\b(?:zielon\p{L}*|green)\b|(?:^|-)G(?:\d|$|-)/iu, "Zielone światło tworzy świeży, wyraźny akcent kolorystyczny.", "witryn, mebli, wnęk, dekoracji i oznaczeń, w których potrzebna jest jednolita zielona linia światła"],
    [/\b(?:żółt\p{L}*|zolt\p{L}*|yellow)\b|(?:^|-)Y(?:\d|$|-)/iu, "Żółte światło tworzy wyrazisty, nasycony akcent kolorystyczny.", "witryn, mebli, wnęk, dekoracji i oznaczeń, w których potrzebna jest jednolita żółta linia światła"],
    [/\b(?:pomarańcz\p{L}*|pomarancz\p{L}*|orange|amber|bursztyn\p{L}*)\b|(?:^|-)O(?:\d|$|-)/iu, "Pomarańczowe światło tworzy wyrazisty, dekoracyjny akcent kolorystyczny.", "witryn, mebli, wnęk, dekoracji i oznaczeń, w których potrzebna jest jednolita pomarańczowa linia światła"],
    [/\b(?:niebiesk\p{L}*|blue)\b|(?:^|-)B(?:\d|$|-)/iu, "Niebieskie światło tworzy chłodny, wyraźny akcent kolorystyczny.", "witryn, mebli, wnęk, dekoracji i stref rozrywki, w których potrzebna jest jednolita niebieska linia światła"],
  ];
  for (const [pattern, lead, applications] of colors) {
    if (pattern.test(source)) return { lead, use: `Sprawdzi się w podświetleniu ${applications}.`, controller: "" };
  }

  const temperatures = [...source.matchAll(/\b(\d{4,5})\s*K\b/giu)].map((match) => Number(match[1]));
  const temperature = temperatures.length ? Math.round(temperatures.reduce((sum, value) => sum + value, 0) / temperatures.length) : 0;
  if (temperature && temperature <= 3500 || /(?:^|-)WW(?:\d|$|-)/iu.test(code)) return {
    lead: "Ciepła biała barwa tworzy spokojne, przytulne światło.",
    use: "Dobrze sprawdza się w salonach, sypialniach, strefach wypoczynku oraz w dekoracyjnym podświetleniu mebli i wnęk.",
    controller: "",
  };
  if (temperature >= 3600 && temperature <= 5000 || /(?:^|-)NW(?:\d|$|-)/iu.test(code)) return {
    lead: "Neutralna biała barwa daje naturalne, uniwersalne światło.",
    use: "Pasuje do kuchni, blatów roboczych, biur, korytarzy, witryn oraz podświetlenia mebli i zabudowy.",
    controller: "",
  };
  if (temperature > 5000 || /(?:^|-)W(?:\d|$|-)/iu.test(code)) return {
    lead: "Chłodna biała barwa daje wyraźne światło o technicznym charakterze.",
    use: "Sprawdzi się w warsztatach, pomieszczeniach użytkowych, ekspozycjach i miejscach wymagających kontrastowego podświetlenia.",
    controller: "",
  };
  return {
    lead: "Ten wariant tworzy równomierną linię światła do zastosowań dekoracyjnych i uzupełniających.",
    use: "Sprawdzi się w podświetleniu mebli, wnęk, witryn i elementów zabudowy.",
    controller: "",
  };
}

function naturalDescription(product) {
  const name = timDescriptionName(product)
    .replace(/\bEconomic\b/giu, "Standard")
    .replace(/\b3\s+lat\s+gwarancji\b/giu, "3 lata gwarancji");
  const series = seriesName(product);
  const years = warrantyYears(product);
  const polish = clean(product.attributes?.["Polska produkcja"]).toLocaleLowerCase("pl") === "tak";
  const isCob = /\bW?COB\b/iu.test(`${product.name} ${product.manufacturerCode}`);
  const ip = clean(product.name).match(/\bIP(\d{2})\b/iu)?.[1] || "";
  const voltage = clean(product.name).match(/\b(12|24|36|48)\s*V\b/iu)?.[1]
    || clean(product.manufacturerCode).match(/^(12|24|36|48)/u)?.[1]
    || "";
  const width = clean(product.name).match(/\b(\d+(?:[.,]\d+)?)\s*mm\b/iu)?.[1] || "";
  const variant = lightVariant(product);

  let intro = series
    ? `Taśma LED z serii ${series} jest przeznaczona do instalacji oświetlenia liniowego i dekoracyjnego.`
    : "Taśma LED jest przeznaczona do instalacji oświetlenia liniowego i dekoracyjnego.";
  if (series === "Standard") intro = "Taśma LED z serii Standard to przystępny cenowo wybór do prostych instalacji dekoracyjnych i uzupełniających.";
  if (isCob) intro += " Technologia COB pomaga uzyskać jednolitą linię światła bez wyraźnych punktów świetlnych.";
  if (polish) intro += " Produkt został wyprodukowany w Polsce.";
  if (years) intro += ` Produkt jest objęty ${years === 1 ? "roczną gwarancją" : `${years}-letnią gwarancją`}.`;

  let use = variant.use;
  if (Number(ip) >= 62) {
    use += ` Wariant IP${ip} można stosować w miejscach wymagających ochrony odpowiadającej deklarowanemu stopniowi IP.`;
  }

  let selection = variant.controller
    ? `Do taśmy należy dobrać sterownik ${variant.controller}${voltage ? ` oraz zasilacz ${voltage} V` : " i odpowiedni zasilacz"}, uwzględniając łączną moc podłączonego odcinka oraz wymagany zapas mocy.`
    : `Do taśmy należy dobrać ${voltage ? `zasilacz ${voltage} V` : "zasilacz o zgodnym napięciu"}, uwzględniając łączną moc podłączonego odcinka oraz wymagany zapas mocy.`;
  selection += " W ofercie Prescot można dobrać odpowiedni zasilacz, profil aluminiowy i akcesoria połączeniowe.";
  let safety = "Przed podłączeniem należy sprawdzić napięcie, polaryzację oraz warunki pracy instalacji.";
  safety += width ? ` Profil dobieramy do rzeczywistej szerokości taśmy wynoszącej ${width} mm.` : " Profil dobieramy do rzeczywistej szerokości taśmy.";
  if (Number(ip) >= 62) safety += " Połączenia, przewody i miejsca podziału należy zabezpieczyć odpowiednio do warunków montażu.";

  return `<section>\n<h2>${escapeHtml(name)}</h2>\n<p>${escapeHtml(intro)}</p>\n<h3>Barwa światła i zastosowanie</h3>\n<p>${escapeHtml(variant.lead)}</p>\n<p>${escapeHtml(use)}</p>\n<h3>Dobór i bezpieczeństwo</h3>\n<p>${escapeHtml(selection)}</p>\n<p>${escapeHtml(safety)}</p>\n</section>`;
}

const byEan = new Map();
for (const product of catalog.products || []) {
  if (product.categoryRoot !== "Taśmy LED") continue;
  const ean = clean(product.ean);
  if (!ean) continue;
  if (!byEan.has(ean)) byEan.set(ean, []);
  byEan.get(ean).push(product);
}

// The current supplier XML shortens this one trade code to "RGBCC", while
// both the exact-EAN product name and the existing TIM card identify the
// function as RGB+CCT. Keep TIM's live trade index as the write guard and do
// not put either code in customer-facing copy.
const verifiedLiveModelAliases = new Map([
  ["5905475363498", {
    catalogModel: "24EC840-036-12-RGBCC",
    liveModel: "24EC840-036-12-RGB+CCT",
    evidence: "exact EAN; source and TIM names both state RGB+CCT",
  }],
]);

const accepted = [];
const rejected = [];
for (const live of snapshot.products || []) {
  if (live.expectedBrand !== "Prescot" || live.state !== "active" || live.published !== true || Number(live.stock) <= 0) continue;
  const matches = byEan.get(clean(live.ean)) || [];
  if (matches.length !== 1 || !oldDescriptionNeedsNaturalRewrite(live.descriptionHtml)) continue;
  const product = matches[0];
  const tradeIndex = timTradeIndex(product);
  const alias = verifiedLiveModelAliases.get(clean(live.ean));
  const aliasMatches = alias
    && tradeIndex === alias.catalogModel
    && clean(live.model) === alias.liveModel;
  if (!tradeIndex || (tradeIndex !== clean(live.model) && !aliasMatches)) {
    rejected.push({ id: live.id, ean: live.ean, model: live.model, reason: "catalog_trade_index_mismatch" });
    continue;
  }
  const fullDescription = naturalDescription(product);
  const errors = validateTimDescription(product, fullDescription);
  if (errors.length) {
    rejected.push({ id: live.id, ean: live.ean, model: live.model, reason: "description_quality_guard_failed", errors });
    continue;
  }
  const descriptionHtml = canonical(fullDescription);
  const forbidden = /\b\d{13}\b|\b(?:PRE[-_ ]?\d+|TAŚ\d+|PRO\d+|KAT\d+)\b|\bEconomic\b|kontrol[aię].{0,20}TIM|TIM.{0,20}kontrol/iu.test(descriptionHtml);
  if (forbidden) {
    rejected.push({ id: live.id, ean: live.ean, model: live.model, reason: "forbidden_description_content" });
    continue;
  }
  accepted.push({
    pimcoreId: Number(live.id),
    ean: clean(live.ean),
    manufacturerCode: aliasMatches ? clean(live.model) : tradeIndex,
    name: timDescriptionName(product),
    descriptionHtml,
    sourceProductKey: product.key,
    sourceUrl: product.url,
    series: seriesBucket(product),
    liveStock: Number(live.stock),
    timIndex: clean(live.timIndex),
    ...(aliasMatches ? { sourceModelAlias: alias } : {}),
  });
}

const priority = (series) => {
  const order = ["Delux7Y", "Premium5Y", "Premium3Y", "Premium2Y", "PremiumUnknown", "Standard3Y", "Standard2Y", "Standard1Y", "StandardUnknown", "OtherUnknown"];
  const index = order.indexOf(series);
  return index === -1 ? order.length : index;
};
accepted.sort((left, right) => priority(left.series) - priority(right.series)
  || right.liveStock - left.liveStock || left.ean.localeCompare(right.ean));

const output = {
  generatedAt: new Date().toISOString(),
  sourceSnapshot: snapshotPath,
  sourceCatalog: catalogPath,
  rules: [
    "only active published Prescot LED tapes with positive stock and an old generic TIM description",
    "exact unique EAN and exact live model equals manufacturer trade index",
    "three natural copy blocks without a parameter list",
    "no EAN, internal index, Economic label, TIM-control phrase or procedural installation steps",
    "warranty and Polish production only from the product name or explicit source attributes",
    "never change name, price, EAN, stock, identifiers, documents or workflow",
  ],
  counts: {
    activePositiveNeedsUpdate: accepted.length,
    bySeries: Object.fromEntries([...new Set(accepted.map((item) => item.series))].map((series) => [
      series,
      accepted.filter((item) => item.series === series).length,
    ])),
    rejected: rejected.length,
  },
  stages: {
    activePositiveNeedsUpdate: accepted,
    activePositiveCurrent: [],
    activeZeroNeedsUpdate: [],
    activeZeroCurrent: [],
  },
  rejected,
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(output, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ outputPath, counts: output.counts }, null, 2));
