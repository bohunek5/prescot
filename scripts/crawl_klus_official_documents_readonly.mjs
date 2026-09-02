import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const snapshotPath = resolve(process.argv[2]
  || "exports/tim/remediation/buffer-current-live-readonly-after-activations-2026-09-01.json");
const outputPath = resolve(process.argv[3]
  || "exports/tim/remediation/klus-official-document-map-2026-09-01.json");

const snapshot = JSON.parse(await readFile(snapshotPath, "utf8"));
const sourceItems = Array.isArray(snapshot.items) ? snapshot.items : snapshot.products;
if (!Array.isArray(sourceItems)) throw new Error("Snapshot nie zawiera tablicy items ani products.");
const products = sourceItems
  .filter((item) => /KLUŚ|KLUS/iu.test(`${item.expectedBrand || ""} ${item.manufacturerName || ""} ${item.manufacturerPath || ""}`))
  .map((item) => ({
    id: Number(item.id),
    ean: String(item.ean || "").trim(),
    model: String(item.model || "").trim(),
    timName: String(item.timName || "").trim(),
    state: String(item.state || "").trim(),
  }));

const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
const context = browser.contexts()[0];
if (!context) throw new Error("Brak kontekstu zalogowanej przeglądarki Chrome.");
const page = await context.newPage();
await page.goto("https://klusdesign.eu/en/", { waitUntil: "domcontentloaded", timeout: 30_000 });

const records = [];
for (let start = 0; start < products.length; start += 6) {
  const batch = products.slice(start, start + 6);
  const crawled = await page.evaluate(async (rows) => Promise.all(rows.map(async (row) => {
    const absolute = (href) => new URL(href, location.origin).href;
    const classify = (label, url) => {
      const text = `${label} ${url}`.toLowerCase();
      if (/specification sheet|product.?datasheet|product card|karta produktu|kartyproduktowe/.test(text)) return "dataSheet";
      if (/mounting instruction|general instruction|instructions?|instrukcj/.test(text)) return "instruction";
      if (/declaration of conformity|declaration of compliance|deklaracj|conformity|declaration_ce|ce_declaration/.test(text)
        && !/ukca|responsible|quality management|epd/.test(text)) return "certification";
      if (/\.pdf(?:$|\?)/i.test(url)) return "otherPdf";
      return "other";
    };
    const normalize = (value) => String(value || "").trim().toUpperCase();
    const model = normalize(row.model);
    const familyModel = model.replace(/_[123]$/, "");
    try {
      const searchUrl = `/en/search/${encodeURIComponent(row.model)}?lang=en`;
      const searchResponse = await fetch(searchUrl, { credentials: "same-origin", cache: "no-store" });
      const searchHtml = await searchResponse.text();
      const searchDoc = new DOMParser().parseFromString(searchHtml, "text/html");
      const productUrls = [...new Set([...searchDoc.querySelectorAll('a[href*="/en/product/"]')]
        .map((anchor) => absolute(anchor.getAttribute("href"))))];
      const candidates = [];
      for (const productUrl of productUrls.slice(0, 5)) {
        const response = await fetch(productUrl, { credentials: "same-origin", cache: "no-store" });
        const html = await response.text();
        const doc = new DOMParser().parseFromString(html, "text/html");
        const text = normalize(doc.body?.innerText || doc.body?.textContent || "");
        const exactModelInPage = Boolean(model) && text.includes(model);
        const familyModelInPage = Boolean(familyModel) && text.includes(familyModel);
        const documents = [...doc.querySelectorAll("a[href]")]
          .map((anchor) => ({
            label: String(anchor.textContent || "").replace(/\s+/g, " ").trim(),
            url: absolute(anchor.getAttribute("href")),
          }))
          .filter((docLink) => /\.pdf(?:$|\?)/i.test(docLink.url))
          .map((docLink) => ({ ...docLink, type: classify(docLink.label, docLink.url) }))
          .filter((docLink, index, all) => all.findIndex((other) => other.url === docLink.url) === index);
        candidates.push({
          productUrl,
          http: response.status,
          productName: String(doc.querySelector("h1")?.textContent || "").replace(/\s+/g, " ").trim(),
          exactModelInPage,
          familyModelInPage,
          documents,
        });
      }
      candidates.sort((a, b) => Number(b.exactModelInPage) - Number(a.exactModelInPage)
        || Number(b.familyModelInPage) - Number(a.familyModelInPage)
        || b.documents.length - a.documents.length);
      return {
        ...row,
        searchUrl: absolute(searchUrl),
        searchHttp: searchResponse.status,
        searchResults: productUrls.length,
        best: candidates[0] || null,
        candidates,
      };
    } catch (error) {
      return { ...row, error: String(error?.message || error) };
    }
  })), batch);
  records.push(...crawled);
  console.log(`KLUŚ: odczytano ${Math.min(start + batch.length, products.length)}/${products.length}`);
}

await page.close();
await browser.close();

const report = {
  generatedAt: new Date().toISOString(),
  source: "official KLUŚ website search and product pages",
  readOnly: true,
  snapshotPath,
  counts: {
    total: records.length,
    exactPageMatch: records.filter((row) => row.best?.exactModelInPage).length,
    familyPageMatch: records.filter((row) => !row.best?.exactModelInPage && row.best?.familyModelInPage).length,
    noResult: records.filter((row) => !row.best).length,
    withDataSheet: records.filter((row) => row.best?.documents.some((doc) => doc.type === "dataSheet")).length,
    withInstruction: records.filter((row) => row.best?.documents.some((doc) => doc.type === "instruction")).length,
    withCertification: records.filter((row) => row.best?.documents.some((doc) => doc.type === "certification")).length,
    errors: records.filter((row) => row.error).length,
  },
  records,
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify(report.counts, null, 2));
console.log(`Raport: ${outputPath}`);
