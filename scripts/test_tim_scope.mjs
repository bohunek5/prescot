#!/usr/bin/env node

import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { isTimScopeProduct, selectTimScope } from "./tim_scope.mjs";

const catalog = JSON.parse(await readFile(new URL("../data/catalog.json", import.meta.url), "utf8"));
const scope = selectTimScope(catalog.products);
const byCode = new Map(catalog.products.map((product) => [product.code, product]));

assert.equal(scope.length, 2651);
assert.equal(scope.filter((product) => product.categoryRoot === "Profile do taśm LED").length, 911);
assert.equal(scope.filter((product) => product.category.includes("aluminiowe")).length, 758);
assert.equal(scope.filter((product) => product.category.includes("PCV")).length, 153);
assert.ok(isTimScopeProduct(byCode.get("PRE-KPL-00002")), "Błędnie opisany jako MeanWell profil PCV musi pozostać w zakresie.");
for (const code of ["00826", "00827", "00828", "00829", "ZYR-00003", "K-5242", "LPXML-LP-3176/1P S SM"]) {
  assert.ok(!isTimScopeProduct(byCode.get(code)), `${code} powinien być poza TIM.`);
}
assert.ok(scope.every((product) => !/kaja|light\s*prestige/i.test(`${product.producer} ${product.name} ${product.category}`)));
assert.ok(!isTimScopeProduct({ producer: "LIGHT", name: "Oprawa", category: "Profile do taśm LED", categoryRoot: "Profile do taśm LED" }));

console.log("Zakres TIM: 2651 produktów; 911 profili; Kaja i Light Prestige wykluczone.");
