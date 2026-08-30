import { loadProducts, buildState } from './app.js';
import { generateDescription } from './description-engine.js';
(async () => {
  const products = await loadProducts();
  const state = await buildState();
  const p13123 = products.find(p => p.sku === '13123');
  const saved13123 = state.generated?.products?.[p13123?.key];
  if (p13123) console.log(generateDescription(p13123, 'shoper', saved13123?.editorial || saved13123));
})();
