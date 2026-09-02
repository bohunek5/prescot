#!/usr/bin/env node

import assert from "node:assert/strict";
import { generateDescription, plainTextFromHtml } from "../description-engine.js";
import { validateTimDescription } from "./tim_description_quality.mjs";

const tape = {
  name: "Taśma LED Premium 12V 480led/m COB 10.5W/m 2700K IP20 950lm/m 8mm CRI90 2Y 5m",
  code: "Taś000717",
  manufacturerCode: "12EC480WW275",
  ean: "5905475367915",
  category: "Taśmy LED/Taśmy LED 12V",
  categoryRoot: "Taśmy LED",
  attributes: {},
};

const html = generateDescription(tape, "tim");
const text = plainTextFromHtml(html);

assert.match(text, /Barwa światła i zastosowanie/u);
assert.match(text, /Dobór i bezpieczeństwo/u);
assert.match(text, /2-letnią gwarancją/u);
assert.doesNotMatch(text, /Parametry produktu|Indeks handlowy|Opis dotyczy produktu|Wariant ma moc/u);
assert.doesNotMatch(text, /5905475367915|Taś000717/u);
assert.deepEqual(validateTimDescription(tape, html), []);

const power = {
  name: "Zasilacz modułowy LED 300W-Auto 12V/24V 25A/12.5A",
  code: "Zas000410",
  manufacturerCode: "PR-MAD300-1224",
  ean: "5905475368127",
  category: "Zasilacze LED/Zasilacze LED modułowe siatkowe",
  categoryRoot: "Zasilacze LED",
  attributes: {},
};
const powerHtml = generateDescription(power, "tim");
const powerText = plainTextFromHtml(powerHtml);
assert.match(powerText, /Indeks handlowy: PR-MAD300-1224/u);
assert.match(powerText, /Napięcie: 12V\/24V/u);
assert.match(powerText, /Prąd znamionowy: 25A\/12\.5A/u);
assert.doesNotMatch(powerText, /5905475368127|Zas000410/u);
assert.deepEqual(validateTimDescription(power, powerHtml), []);

const controller = {
  name: "Sterownik LED Mono 1x30A potencjometr 12-24V Prescot",
  code: "STR000002",
  manufacturerCode: "PR-MONO-360-WALL-P",
  ean: "5904162806294",
  category: "Sterowniki LED/Sterowniki manualne",
  categoryRoot: "Sterowniki LED",
  attributes: {},
};
const controllerHtml = generateDescription(controller, "tim");
const controllerText = plainTextFromHtml(controllerHtml);
assert.match(controllerText, /Indeks handlowy: PR-MONO-360-WALL-P/u);
assert.match(controllerText, /Napięcie: 12-24V/u);
assert.match(controllerText, /Prąd znamionowy: 1x30A/u);
assert.doesNotMatch(controllerText, /5904162806294|STR000002/u);
assert.deepEqual(validateTimDescription(controller, controllerHtml), []);

const endcapKit = {
  name: "Zestaw zaślepek i kleju do taśmy LED Premium 24V 320led/m COB IP67 10mm 10szt.",
  code: "PRE-TEST-ACCESSORY",
  manufacturerCode: "24EC320IP67-ZAS",
  ean: "5905475368226",
  category: "Taśmy LED",
  categoryRoot: "Taśmy LED",
  attributes: {},
};
const endcapKitHtml = generateDescription(endcapKit, "tim");
const endcapKitText = plainTextFromHtml(endcapKitHtml);
assert.match(endcapKitText, /Jest to element przeznaczony do kompletacji zgodnego systemu LED/u);
assert.doesNotMatch(endcapKitText, /Jest to taśma LED/u);
assert.doesNotMatch(endcapKitText, /Długość rolki/u);
assert.doesNotMatch(endcapKitText, /5905475368226|PRE-TEST-ACCESSORY/u);
assert.deepEqual(validateTimDescription(endcapKit, endcapKitHtml), []);

console.log("TIM description engine: regression checks passed.");
