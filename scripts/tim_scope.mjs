import { readFileSync } from "node:fs";

const configUrl = new URL("../config/tim-scope.json", import.meta.url);

export const TIM_SCOPE_CONFIG = JSON.parse(readFileSync(configUrl, "utf8"));

const allowedProducers = new Set(TIM_SCOPE_CONFIG.allowedProducers);
const includedCategoryRoots = new Set(TIM_SCOPE_CONFIG.includedCategoryRoots);
const deniedProducers = new Set(TIM_SCOPE_CONFIG.deniedProducers || []);
const deniedPatterns = TIM_SCOPE_CONFIG.deniedPatterns.map((pattern) => new RegExp(pattern, "iu"));

export function normalizeText(value) {
  return String(value ?? "").replace(/\s+/g, " ").trim();
}

export function numericValue(value) {
  const normalized = normalizeText(value).replace(",", ".");
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : 0;
}

export function timScopeText(product) {
  return normalizeText([product.producer, product.name, product.category].join(" "));
}

export function timExclusionReasons(product) {
  const text = timScopeText(product);
  const reasons = deniedPatterns
    .filter((pattern) => pattern.test(text))
    .map((pattern) => `deny_pattern:${pattern.source}`);
  if (deniedProducers.has(normalizeText(product.producer))) reasons.unshift(`deny_producer:${normalizeText(product.producer)}`);
  return [...new Set(reasons)];
}

export function timInclusionReasons(product) {
  const reasons = [];
  if (allowedProducers.has(product.producer)) reasons.push(`producer:${product.producer}`);
  if (includedCategoryRoots.has(product.categoryRoot)) reasons.push(`category_root:${product.categoryRoot}`);
  return reasons;
}

export function timScopeDecision(product) {
  const inclusionReasons = timInclusionReasons(product);
  const exclusionReasons = timExclusionReasons(product);
  return {
    included: inclusionReasons.length > 0 && exclusionReasons.length === 0,
    inclusionReasons,
    exclusionReasons,
  };
}

export function isTimScopeProduct(product) {
  return timScopeDecision(product).included;
}

export function selectTimScope(products) {
  return products.filter(isTimScopeProduct);
}

export function groupCounts(values, selector) {
  const counts = new Map();
  for (const value of values) {
    const key = normalizeText(selector(value)) || "(brak)";
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  return Object.fromEntries(
    [...counts.entries()].sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0], "pl")),
  );
}
