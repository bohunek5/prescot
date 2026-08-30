import re

with open("description-engine.js", "r") as f:
    content = f.read()

# 1. Update identitySection to use result
content = re.sub(
    r"function identitySection\(product, platform\) \{",
    r"function identitySection(product, platform, result) {",
    content
)

content = re.sub(
    r"  const intro = \[\];\n  intro\.push\(product\.summary \? paragraph\(product\.summary\) : paragraph\(product\.name\)\);\n  return section\(\n    pick\(product, platform, \"lighting-label\", \[\"Opis\", \"Seria\", \"Rodzina\", \"Wariant\"\]\),\n    leafCategory\(product\),\n    intro\.join\(\"\"\)\n  \);",
    r"""  let introHtml = "";
  if (result && result.sections && result.sections[0] && result.sections[0].paragraphs) {
    const pText = result.sections[0].paragraphs.map(normalize).join(" ");
    introHtml = paragraph(pText);
  } else {
    introHtml = product.summary ? paragraph(product.summary) : paragraph(product.name);
  }
  return section(
    pick(product, platform, "lighting-label", ["Opis", "Seria", "Rodzina", "Wariant"]),
    result && result.sections ? result.sections[0].heading : leafCategory(product),
    introHtml
  );""",
    content
)

# 2. Update genericNarrative to use result
content = re.sub(
    r"function genericNarrative\(product, platform, kind\) \{",
    r"function genericNarrative(product, platform, kind, result) {",
    content
)

content = re.sub(
    r"  if \(kind === \"tape\"\) return tapeNarrative\(product, platform\);\n  if \(kind === \"profile\"\) return profileNarrative\(product, platform\);\n  if \(kind === \"power\"\) return powerNarrative\(product, platform\);\n  if \(kind === \"control\"\) return controllerNarrative\(product, platform\);\n  if \(kind === \"connector\"\) return connectorNarrative\(product, platform\);\n  if \(\[\"bulb\", \"tube\", \"module\", \"luminaire\", \"seasonal\", \"kit\"\]\.includes\(kind\)\) return lightingNarrative\(product, platform, kind\);\n  if \(kind === \"electrical\"\) return electricalNarrative\(product, platform\);",
    r"""  if (result && result.sections && result.sections.length > 1) {
    const sec2 = result.sections[1];
    const sec2Html = section(
      pick(product, platform, "generic-label", ["Zastosowanie", "Dobór produktu", "Gdzie użyć"]),
      sec2.heading,
      sec2.paragraphs.map(p => paragraph(p)).join("")
    );
    let benefitsHtml = "";
    if (result.benefits && result.benefits.length > 0) {
      const bList = list(result.benefits.map(escapeHtml));
      benefitsHtml = section("Dlaczego warto", "Najważniejsze korzyści", bList, "#16a34a");
    }
    return [sec2Html, benefitsHtml].filter(Boolean);
  }

  if (kind === "tape") return tapeNarrative(product, platform);
  if (kind === "profile") return profileNarrative(product, platform);
  if (kind === "power") return powerNarrative(product, platform);
  if (kind === "control") return controllerNarrative(product, platform);
  if (kind === "connector") return connectorNarrative(product, platform);
  if (["bulb", "tube", "module", "luminaire", "seasonal", "kit"].includes(kind)) return lightingNarrative(product, platform, kind);
  if (kind === "electrical") return electricalNarrative(product, platform);""",
    content
)

# 3. Update technicalSection to use grid for power supplies and text for tapes
content = re.sub(
    r"function technicalSection\(product, platform\) \{",
    r"function technicalSection(product, platform, result) {",
    content
)

# Replace the body of technicalSection
tech_old = r"""  const items = \[\];
  for \(const \[label, rawValue\] of Object\.entries\(product\.attributes \|\| \{\}\)\) \{
    const value = normalize\(rawValue\);
    if \(!value \|\| value === \"-\" \|\| INTERNAL_ATTRIBUTES\.has\(label\)\) continue;
    items\.push\(important\(label, value\)\);
  \}
  if \(product\.producer\) items\.unshift\(important\(\"Producent\", product\.producer\)\);
  if \(product\.code\) items\.push\(important\(\"Indeks handlowy\", product\.code\)\);
  if \(product\.ean\) items\.push\(important\(\"EAN\", product\.ean\)\);
  return section\(
    pick\(product, platform, \"technical-label\", \[\"Dane techniczne\", \"Specyfikacja\", \"Parametry katalogowe\"\]\),
    \"Parametry tego konkretnego wariantu\",
    list\(items\.length \? items : \[escapeHtml\(\"Brak dodatkowych parametrów technicznych w bieżącym eksporcie\. Dobór oprzyj na nazwie oraz kodzie produktu\.\"\)\]\),
  \);"""

tech_new = r"""  const kind = productKind(product);
  const specs = seoProductSpecs(product);
  
  if (kind === "power") {
    // Generate grid table for power supplies
    const cards = specs.map(([label, value]) => `
      <div style="font-family:inherit;padding:12px 14px;background:none!important;background-color:transparent!important;border:1px solid currentColor;border-radius:10px;color:inherit;display:flex;flex-direction:column;gap:4px;">
        <span style="font-size:12px;opacity:.72;text-transform:uppercase;letter-spacing:.02em;line-height:1.2;">${escapeHtml(label)}</span>
        <strong style="font-size:14px;font-weight:700;line-height:1.3;word-break:break-word;">${escapeHtml(value)}</strong>
      </div>
    `).join("");
    const gridHtml = `<div style="font-family:inherit;display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:16px;margin-top:6px;background:none!important;background-color:transparent!important;color:inherit;">${cards}</div>`;
    return section(
      pick(product, platform, "technical-label", ["Dane techniczne", "Specyfikacja", "Parametry"]),
      "Parametry katalogowe",
      gridHtml
    );
  } else {
    // Standard list for tapes and others
    const items = specs.map(([label, value]) => important(label, value));
    return section(
      pick(product, platform, "technical-label", ["Najważniejsze cechy", "Specyfikacja", "Parametry"]),
      "Parametry tego wariantu",
      list(items.length ? items : [escapeHtml("Sprawdź parametry w nazwie i specyfikacji.")]),
    );
  }"""
content = re.sub(tech_old, tech_new, content)


# 4. Update generateDescription
old_gen = r"""export function generateDescription\(product, platform = \"shoper\"\) \{
  const selectedPlatform = PLATFORM_NAMES\[platform\] \? platform : \"shoper\";
  const kind = productKind\(product\);
  const parts = \[
    identitySection\(product, selectedPlatform\),
    \.\.\.genericNarrative\(product, selectedPlatform, kind\),
    technicalSection\(product, selectedPlatform\),
    blogSection\(product, selectedPlatform, kind\),
  \];
  return normalizeDescriptionIdentity\(product, parts\.filter\(Boolean\)\.join\(\"\\n\"\), \{ ensureTradeIndex: selectedPlatform !== \"tim\" \}\);
\}"""

new_gen = r"""export function generateDescription(product, platform = "shoper", result = null) {
  const selectedPlatform = PLATFORM_NAMES[platform] ? platform : "shoper";
  const kind = productKind(product);
  
  if (result) {
    if (selectedPlatform === "wapro") return normalizeDescriptionIdentity(product, seoWapro(product, result));
    if (selectedPlatform === "tim") return normalizeDescriptionIdentity(product, seoTim(product, result), { ensureTradeIndex: false, preserveManufacturerCode: true });
    if (selectedPlatform === "allegro") {
      return normalizeDescriptionIdentity(product, [
        seoSection({ label: "Sprawdź przed zakupem", heading: result.seo_title, paragraphs: [result.channel_leads.allegro] }, { color: "#16a34a" }),
        seoBenefits(result.benefits),
        seoSection(result.sections[1], { color: "#16a34a", label: "Gdzie użyć" }),
        seoPoints("Dobór bez pomyłki", "Co sprawdzić przed montażem", [...(result.selection_checks||[]), ...(result.installation_notes||[])], "#16a34a"),
      ].join("\n"));
    }
  }

  // Shoper layout (old graphical + new text)
  const parts = [
    identitySection(product, selectedPlatform, result),
    ...genericNarrative(product, selectedPlatform, kind, result),
    technicalSection(product, selectedPlatform, result),
    blogSection(product, selectedPlatform, kind),
  ];
  return normalizeDescriptionIdentity(product, parts.filter(Boolean).join("\n"), { ensureTradeIndex: selectedPlatform !== "tim" });
}"""

content = re.sub(old_gen, new_gen, content)


# 5. Remove renderSeoDescription as it's no longer used
content = re.sub(r"export function renderSeoDescription[\s\S]+?(?=export function generateDescription)", "", content)

with open("description-engine.js", "w") as f:
    f.write(content)

