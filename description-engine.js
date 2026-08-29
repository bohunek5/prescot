const PLATFORM_NAMES = {
  shoper: "Shoper",
  wapro: "WAPRO / MAG",
  tim: "TIM",
  allegro: "Allegro",
};

const INTERNAL_ATTRIBUTES = new Set([
  "Producent",
  "Kod_produktu",
  "Kod_producenta",
  "EAN",
  "Nazwa galerii",
  "Producent odpowiedzialny",
  "Podmiot odpowiedzialny",
  "Informacje o bezpieczeństwie",
]);

const BLOGS = {
  tape: [
    ["Jak czytać parametry taśmy LED?", "moc, lumeny, CRI, napięcie i IP", "https://www.prescot.com.pl/pl/n/23"],
    ["Jak dobrać taśmę LED do mieszkania?", "barwa, moc i miejsce montażu", "https://www.prescot.com.pl/pl/n/12"],
    ["Jak dobrać profil aluminiowy?", "profil, klosz, chłodzenie i linia światła", "https://www.prescot.com.pl/pl/n/15"],
    ["Montaż taśmy LED na zewnątrz", "IP, uszczelnienie i ochrona połączeń", "https://www.prescot.com.pl/pl/n/16"],
  ],
  power: [
    ["Jak dobrać zasilacz LED do taśmy?", "napięcie, moc i bezpieczny zapas", "https://www.prescot.com.pl/pl/n/28"],
    ["Zasilacze LED — gdzie użyć którego?", "desktop, modułowy czy hermetyczny", "https://www.prescot.com.pl/pl/n/29"],
    ["Do czego służą zasilacze LED?", "zmiana napięcia 230 V na napięcie instalacji", "https://www.prescot.com.pl/pl/n/30"],
    ["Stopnie IP — dlaczego są ważne?", "dobór obudowy do miejsca montażu", "https://www.prescot.com.pl/pl/n/31"],
  ],
  control: [
    ["Jak czytać parametry taśmy LED?", "napięcie, moc, liczba kanałów i IP", "https://www.prescot.com.pl/pl/n/23"],
    ["Jak dobrać taśmę LED do mieszkania?", "barwa, moc i miejsce montażu", "https://www.prescot.com.pl/pl/n/12"],
    ["Jak dobrać zasilacz LED do taśmy?", "zasilanie zgodne ze sterownikiem i odbiornikiem", "https://www.prescot.com.pl/pl/n/28"],
  ],
  connector: [
    ["Jak czytać parametry taśmy LED?", "szerokość PCB, napięcie i klasa IP", "https://www.prescot.com.pl/pl/n/23"],
    ["Jak dobrać profil aluminiowy?", "miejsce na taśmę, przewód i złączkę", "https://www.prescot.com.pl/pl/n/15"],
    ["Montaż taśmy LED na zewnątrz", "uszczelnienie i ochrona połączeń", "https://www.prescot.com.pl/pl/n/16"],
  ],
  profile: [
    ["Jak dobrać profil aluminiowy?", "szerokość taśmy, klosz i sposób montażu", "https://www.prescot.com.pl/pl/n/15"],
    ["Jak czytać parametry taśmy LED?", "szerokość, moc, chłodzenie i IP", "https://www.prescot.com.pl/pl/n/23"],
    ["Jak dobrać taśmę LED do mieszkania?", "barwa, moc i miejsce montażu", "https://www.prescot.com.pl/pl/n/12"],
    ["Montaż taśmy LED na zewnątrz", "profil, uszczelnienie i ochrona połączeń", "https://www.prescot.com.pl/pl/n/16"],
  ],
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function hash(value) {
  let result = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    result ^= value.charCodeAt(index);
    result = Math.imul(result, 16777619);
  }
  return result >>> 0;
}

function pick(product, platform, salt, options) {
  return options[hash(`${product.key}|${platform}|${salt}`) % options.length];
}

function normalize(value) {
  return String(value ?? "").replace(/\s+/g, " ").trim();
}

function attr(product, ...names) {
  const entries = Object.entries(product.attributes || {});
  for (const name of names) {
    const exact = product.attributes?.[name];
    if (exact && exact !== "-") return normalize(exact);
    const lower = name.toLocaleLowerCase("pl");
    const found = entries.find(([key, value]) => key.toLocaleLowerCase("pl") === lower && value && value !== "-");
    if (found) return normalize(found[1]);
  }
  return "";
}

function leafCategory(product) {
  return normalize(product.category?.split("/").at(-1) || product.categoryRoot || "produkt");
}

function productKind(product) {
  const root = product.categoryRoot || "";
  const all = `${root} ${product.category} ${product.name}`.toLocaleLowerCase("pl");
  if (root === "Taśmy LED" || /taśm[ay] led/.test(all)) return "tape";
  if (root === "Zasilacze LED") return "power";
  if (root === "Sterowniki LED") return "control";
  if (root === "Profile do taśm LED") return "profile";
  if (root === "Akcesoria do zasilaczy i taśm LED" && /złącz|zlacz|wtycz|gniazd|przew[oó]d|rozdziel|przedłuż/.test(all)) return "connector";
  if (root === "Żarówki LED" || root === "Żarówki standardowe") return "bulb";
  if (root === "Świetlówki LED" || root === "Świetlówki") return "tube";
  if (root === "Zestawy LED") return "kit";
  if (root === "Moduły LED") return "module";
  if (root === "Stateczniki") return "ballast";
  if (root === "Osprzęt elektryczny") return "electrical";
  if (root === "Oświetlenie świąteczne") return "seasonal";
  if (root === "Baterie") return "battery";
  if (/opraw|oświetlenie|candor/i.test(root)) return "luminaire";
  if (root === "Outlet") return "outlet";
  return "other";
}

const STYLE = {
  section: "font-family:inherit;margin:0 0 18px 0;padding:22px 24px;background:none!important;background-color:transparent!important;border:1px solid currentColor;border-radius:12px;color:inherit;",
  pill: "font-family:inherit;display:inline-block;margin-bottom:10px;padding:5px 12px;border-radius:999px;background:#e94b25!important;background-color:#e94b25!important;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;font-size:11px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;line-height:1.2;",
  heading: "font-family:inherit;margin:0 0 8px 0;background:none!important;background-color:transparent!important;color:inherit!important;font-size:22px;line-height:1.3;font-weight:700;",
  paragraph: "font-family:inherit;margin:0;background:none!important;background-color:transparent!important;color:inherit!important;opacity:.84;font-size:14px;line-height:1.65;",
  list: "font-family:inherit;margin:0;padding:0 0 0 20px;color:inherit!important;opacity:.86;font-size:14px;line-height:1.65;",
};

function section(label, heading, body) {
  return `<section style="${STYLE.section}"><span style="${STYLE.pill}"><font color="#ffffff">${escapeHtml(label)}</font></span><h3 style="${STYLE.heading}">${escapeHtml(heading)}</h3>${body}</section>`;
}

function paragraph(text) {
  return `<p style="${STYLE.paragraph}">${escapeHtml(text)}</p>`;
}

function paragraphHtml(text) {
  return `<p style="${STYLE.paragraph}">${text}</p>`;
}

function list(items) {
  const content = items
    .filter(Boolean)
    .map((item) => `<li style="font-family:inherit;margin-bottom:6px;">${item}</li>`)
    .join("");
  return `<ul style="${STYLE.list}">${content}</ul>`;
}

function important(label, value) {
  return `<strong style="font-family:inherit;color:inherit!important;">${escapeHtml(label)}:</strong> ${escapeHtml(value)}`;
}

function identitySection(product, platform) {
  const labels = {
    shoper: ["Najważniejsze informacje", "Produkt opisany na podstawie aktualnej karty"],
    wapro: ["Identyfikacja produktu", "Dokładne oznaczenie wariantu"],
    tim: ["Dane do doboru", "Model i przeznaczenie produktu"],
    allegro: ["Co kupujesz", "Sprawdź model przed dodaniem do koszyka"],
  };
  const [label, fallbackHeading] = labels[platform] || labels.shoper;
  const heading = pick(product, platform, "identity-heading", [
    product.name,
    fallbackHeading,
    `${leafCategory(product)} — ${product.manufacturerCode || product.code || product.name}`,
  ]);
  const identifiers = [
    product.producer ? `producent: ${product.producer}` : "",
    product.manufacturerCode ? `kod producenta: ${product.manufacturerCode}` : "",
    product.code && product.code !== product.manufacturerCode ? `kod produktu: ${product.code}` : "",
    product.ean ? `EAN: ${product.ean}` : "",
  ].filter(Boolean);
  const intro = pick(product, platform, "identity-copy", [
    `${product.name}. Produkt należy do kategorii „${leafCategory(product)}”. ${identifiers.join("; ")}.`,
    `Dokładny wariant: ${product.name}. Przy zamówieniu porównaj oznaczenia: ${identifiers.join("; ")}.`,
    `${product.name} — ${identifiers.join("; ")}. Kategoria katalogowa: ${leafCategory(product)}.`,
  ]);
  return section(label, heading, paragraph(intro));
}

function parseNumber(value) {
  const match = String(value || "").replace(",", ".").match(/\d+(?:\.\d+)?/);
  return match ? Number(match[0]) : null;
}

function tapeNarrative(product, platform) {
  const voltage = attr(product, "Napięcie wejściowe", "Napięcie Wejściowe");
  const color = attr(product, "Barwa światła", "Kolor");
  const brightness = attr(product, "Jasność");
  const power = attr(product, "Moc");
  const diode = attr(product, "Typ diody");
  const width = attr(product, "Szerokość taśmy");
  const ip = attr(product, "Klasa szczelności");
  const cut = attr(product, "Moduł cięcia");
  const roll = attr(product, "Rolka", "Wymiar", "Długość");
  const cri = attr(product, "CRI");

  const facts = [voltage && `zasilanie ${voltage}`, color && `barwa ${color}`, brightness && `jasność ${brightness}`, power && `moc ${power}`, diode && `diody ${diode}`, width && `szerokość ${width}`, cri && `CRI ${cri}`].filter(Boolean);
  let use = "Dobierz profil, zasilacz i sposób sterowania do parametrów konkretnego wariantu.";
  const lumens = parseNumber(brightness);
  if (lumens !== null) {
    if (lumens <= 600) use = `Poziom ${brightness} jest przeznaczony przede wszystkim do światła dekoracyjnego, orientacyjnego i bliskiego podświetlenia półek lub wnęk.`;
    else if (lumens <= 1200) use = `Poziom ${brightness} sprawdzi się jako wyraźne światło pomocnicze, między innymi w zabudowie meblowej i nad blatem.`;
    else use = `Poziom ${brightness} pozwala planować mocne oświetlenie użytkowe; przed montażem sprawdź wymagane chłodzenie i oblicz całkowite obciążenie zasilacza.`;
  }

  const checks = [];
  if (voltage) checks.push(`Zastosuj zasilacz o napięciu wyjściowym ${voltage}; mocy nie dobieraj wyłącznie na podstawie długości rolki.`);
  if (width) checks.push(`Profil i złączki muszą pasować do szerokości PCB ${width}.`);
  if (cut) checks.push(`Taśmę tnij wyłącznie w oznaczonych miejscach — moduł cięcia: ${cut}.`);
  if (ip) {
    if (/IP20/i.test(ip)) checks.push("IP20 oznacza wariant do suchych wnętrz, bez ochrony przed wodą.");
    else checks.push(`Deklarowana klasa ${ip} dotyczy taśmy; połączenia, sterownik i zasilacz wymagają osobno dobranej ochrony.`);
  }
  if (roll) {
    const length = parseNumber(roll);
    if (length && length >= 50) checks.push(`${roll} to dłuższy wariant przeznaczony do większych realizacji i ograniczenia liczby osobnych opakowań.`);
    else if (length && length <= 5) checks.push(`${roll} traktuj jako odcinek lub wariant cięty z metra — przed zakupem policz długość każdej linii.`);
  }

  return [
    section(
      pick(product, platform, "tape-label", ["Parametry światła", "Dobór taśmy", "Światło i zasilanie"]),
      facts.length ? facts.join(" • ") : "Taśma dopasowana do konkretnej instalacji",
      paragraph(use),
    ),
    section("Przed montażem", "Sprawdź zgodność całego zestawu", list(checks.length ? checks.map(escapeHtml) : [escapeHtml("Porównaj napięcie, szerokość PCB, klasę IP i długość modułu cięcia z pozostałymi elementami instalacji.")])),
  ];
}

function profileNarrative(product, platform) {
  const all = `${product.name} ${product.category}`.toLocaleLowerCase("pl");
  const length = attr(product, "Długość", "Wymiar");
  const material = attr(product, "Wykonanie (materiał)");
  const mount = attr(product, "Montaż");
  const profileColor = attr(product, "Kolor profilu", "Kolor", "Wykończenie");
  const coverColor = attr(product, "Kolor osłony");
  const width = attr(product, "Szerokość profilu", "Szerokość osłony");
  const facts = [length && `długość ${length}`, material && `materiał ${material}`, mount && `montaż ${mount}`, profileColor && `kolor/wykończenie ${profileColor}`, coverColor && `osłona ${coverColor}`, width && `szerokość ${width}`].filter(Boolean);

  let purpose = "Element systemu profili LED należy dobrać do konkretnej serii, wymiarów oraz sposobu montażu.";
  if (/zaślepk/.test(all)) purpose = "Zaślepka służy do wykończenia końca zgodnego profilu. Porównaj nazwę serii, stronę zaślepki i ewentualny otwór na przewód.";
  else if (/osłon|klosz/.test(all)) purpose = "Osłonę dobierz do konkretnego profilu i oczekiwanego efektu optycznego. Sama długość nie potwierdza kompatybilności systemowej.";
  else if (/uchwyt|sprężyn|mocowa/.test(all)) purpose = "Akcesorium montażowe służy do zamocowania zgodnego profilu. Przed zakupem sprawdź serię oraz liczbę elementów potrzebnych na całą długość.";
  else if (/alumini/.test(`${material} ${all}`)) purpose = "Profil aluminiowy porządkuje montaż taśmy i pomaga odprowadzać wytwarzane przez nią ciepło. Dobierz osłonę, zaślepki i uchwyty z tej samej serii.";
  else if (/pcv|pvc/.test(`${material} ${all}`)) purpose = "Profil z tworzywa służy do prowadzenia i osłonięcia taśmy w zgodnym systemie. Sprawdź dopuszczalną szerokość taśmy oraz sposób mocowania.";

  return [
    section(
      pick(product, platform, "profile-label", ["Zastosowanie", "Dobór systemu", "Element profilu LED"]),
      facts.length ? facts.join(" • ") : leafCategory(product),
      paragraph(purpose),
    ),
    section("Przed zakupem", "Seria i wymiary muszą się zgadzać", list([
      escapeHtml("Porównaj kod producenta z oznaczeniem profilu lub akcesorium, które już masz."),
      escapeHtml("Sprawdź długość, szerokość oraz wariant kolorystyczny."),
      escapeHtml("Osłony, zaślepki i uchwyty dobieraj w obrębie zgodnego systemu."),
    ])),
  ];
}

function powerNarrative(product, platform) {
  const input = attr(product, "Napięcie Wejściowe", "Napięcie wejściowe");
  const output = attr(product, "Napięcie Wyjściowe", "Napięcie wyjściowe");
  const power = attr(product, "Moc");
  const current = attr(product, "Prąd");
  const ip = attr(product, "Klasa szczelności");
  const size = attr(product, "Wymiar");
  const type = attr(product, "Typ") || leafCategory(product);
  const facts = [input && `wejście ${input}`, output && `wyjście ${output}`, power && `moc ${power}`, current && `prąd ${current}`, ip && ip, size && `wymiar ${size}`].filter(Boolean);
  const guidance = [
    output ? `Napięcie wyjściowe zasilacza (${output}) musi być identyczne z napięciem odbiornika.` : "Sprawdź napięcie wyjściowe wymagane przez odbiornik.",
    power ? `Zsumuj moc wszystkich odbiorników i porównaj wynik z mocą znamionową ${power}, uwzględniając zalecenia producenta dotyczące rezerwy i warunków chłodzenia.` : "Oblicz łączne obciążenie i dobierz moc zasilacza według zaleceń producenta.",
    ip ? `Klasa ${ip} opisuje ochronę obudowy; sposób podłączenia i miejsce montażu również muszą spełniać wymagania instalacji.` : "Dobierz obudowę i miejsce montażu do wilgotności, temperatury oraz wentylacji.",
  ];
  return [
    section(
      pick(product, platform, "power-label", ["Parametry zasilania", "Dobór zasilacza", "Napięcie i obciążenie"]),
      facts.length ? facts.join(" • ") : type,
      paragraph(`${product.name} to model z grupy „${type}”. O zgodności decydują napięcie wyjściowe, dostępna moc, sposób montażu i klasa ochrony.`),
    ),
    section("Dobór", "Policz obciążenie przed podłączeniem", list(guidance.map(escapeHtml))),
  ];
}

function controllerNarrative(product, platform) {
  const all = `${product.name} ${product.category}`.toUpperCase();
  const system = ["RGB+CCT", "RGBCCT", "RGBW", "RGB", "CCT", "MONO"].find((name) => all.includes(name)) || leafCategory(product);
  const voltage = attr(product, "Napięcie Wyjściowe", "Napięcie wyjściowe", "Napięcie wejściowe");
  const maxCurrent = attr(product, "Prąd maksymalny");
  const channelCurrent = attr(product, "Prąd na 1 kanał");
  const communication = attr(product, "Komunikacja");
  const zones = attr(product, "Ilość stref");
  const range = attr(product, "Zasięg");
  const facts = [system && `system ${system}`, voltage && `napięcie ${voltage}`, maxCurrent && `prąd maks. ${maxCurrent}`, channelCurrent && `na kanał ${channelCurrent}`, communication && communication, zones && `${zones} stref`, range && `zasięg ${range}`].filter(Boolean);
  return [
    section(
      pick(product, platform, "control-label", ["Sterowanie", "Zgodność systemu", "Parametry sterownika"]),
      facts.length ? facts.join(" • ") : "Sterowanie dopasowane do rodzaju taśmy",
      paragraph(`Ten wariant jest opisany jako ${system}. Sterownik, odbiornik, pilot i taśma muszą pracować w tym samym systemie kanałów oraz w zgodnym zakresie napięcia.`),
    ),
    section("Przed uruchomieniem", "Sprawdź kanały, napięcie i obciążenie", list([
      escapeHtml(`Porównaj typ taśmy z systemem ${system}.`),
      escapeHtml(voltage ? `Zasilanie i odbiornik muszą obsługiwać zakres ${voltage}.` : "Zweryfikuj zakres napięcia w instrukcji urządzenia."),
      escapeHtml(maxCurrent || channelCurrent ? "Nie przekraczaj dopuszczalnego prądu łącznego ani obciążenia pojedynczego kanału." : "Sprawdź maksymalne obciążenie łączne i obciążenie każdego kanału."),
      escapeHtml("Przed zabudową wykonaj parowanie i test całego zestawu."),
    ])),
  ];
}

function connectorNarrative(product, platform) {
  const width = attr(product, "Szerokość taśmy", "Szerokość profilu");
  const current = attr(product, "Prąd maksymalny", "Prąd");
  const cable = attr(product, "Przekrój przewodu", "Długość przewodu");
  const type = attr(product, "Typ") || leafCategory(product);
  const all = `${product.name} ${product.category}`.toUpperCase();
  const channels = ["RGB+CCT", "RGBCCT", "RGBW", "RGB", "CCT", "MONO"].find((name) => all.includes(name));
  const facts = [type, channels, width && `szerokość ${width}`, current && `obciążenie ${current}`, cable && `przewód ${cable}`].filter(Boolean);
  return [
    section(
      pick(product, platform, "connector-label", ["Zgodność", "Dobór akcesorium", "Połączenie instalacji"]),
      facts.length ? facts.join(" • ") : leafCategory(product),
      paragraph("Akcesorium dobierz jednocześnie do rodzaju taśmy lub zasilacza, liczby torów, szerokości elementu oraz planowanego obciążenia. Podobny wygląd nie oznacza zgodności elektrycznej ani mechanicznej."),
    ),
    section("Kontrola przed montażem", "Porównaj wszystkie oznaczenia", list([
      escapeHtml(width ? `Sprawdź zgodność z szerokością ${width}.` : "Sprawdź szerokość taśmy, przewodu, wtyku lub gniazda."),
      escapeHtml(channels ? `Element jest opisany dla systemu ${channels}; porównaj liczbę pinów i układ pól lutowniczych.` : "Porównaj liczbę pinów oraz polaryzację połączenia."),
      escapeHtml(current ? `Nie przekraczaj wartości ${current}.` : "Dobierz obciążalność elementu do prądu w obwodzie."),
    ])),
  ];
}

function lightingNarrative(product, platform, kind) {
  const voltage = attr(product, "Napięcie Wejściowe", "Napięcie wejściowe");
  const power = attr(product, "Moc");
  const brightness = attr(product, "Jasność");
  const color = attr(product, "Barwa światła", "Kolor");
  const angle = attr(product, "Kąt świecenia", "Szerokość świecenia");
  const ip = attr(product, "Klasa szczelności");
  const size = attr(product, "Wymiar", "Długość");
  const base = attr(product, "Trzonek", "Gwint");
  const material = attr(product, "Wykonanie (materiał)");
  const facts = [base && `trzonek ${base}`, voltage && `zasilanie ${voltage}`, power && `moc ${power}`, brightness && `strumień ${brightness}`, color && `barwa ${color}`, angle && `kąt ${angle}`, ip && ip, size && `wymiar ${size}`, material && `materiał ${material}`].filter(Boolean);
  const labels = {
    bulb: "Źródło światła",
    tube: "Świetlówka",
    module: "Moduł LED",
    luminaire: "Oprawa oświetleniowa",
    seasonal: "Oświetlenie dekoracyjne",
    kit: "Zestaw LED",
  };
  const checks = [];
  if (base) checks.push(`Porównaj trzonek lub gwint: ${base}.`);
  if (voltage) checks.push(`Sprawdź zgodność z napięciem ${voltage}.`);
  if (size) checks.push(`Zweryfikuj miejsce montażu i wymiar ${size}.`);
  if (ip) checks.push(`Klasa ${ip} musi odpowiadać warunkom pracy całej instalacji.`);
  if (!ip) checks.push("Nie zakładaj odporności na wilgoć bez potwierdzonej klasy IP w dokumentacji.");
  if (kind === "tube") checks.push("Sprawdź schemat zasilania i zgodność oprawy przed wymianą świetlówki.");
  if (kind === "kit") checks.push("Zakres zestawu ustal na podstawie listy elementów w aktualnej ofercie.");
  return [
    section(
      pick(product, platform, "lighting-label", ["Parametry produktu", "Światło i montaż", labels[kind] || "Zastosowanie"]),
      facts.length ? facts.join(" • ") : leafCategory(product),
      paragraph(`${product.name} to produkt z grupy „${leafCategory(product)}”. Dobierając wariant, porównaj parametry elektryczne, wymiary i sposób instalacji z miejscem zastosowania.`),
    ),
    section("Przed zakupem", "Sprawdź zgodność z oprawą i instalacją", list(checks.map(escapeHtml))),
  ];
}

function electricalNarrative(product, platform) {
  const color = attr(product, "Kolor", "Kolor profilu");
  const material = attr(product, "Wykonanie (materiał)");
  const mount = attr(product, "Montaż");
  const size = attr(product, "Wymiar");
  const voltage = attr(product, "Napięcie Wejściowe", "Napięcie wejściowe");
  const facts = [color && `kolor ${color}`, material && `materiał ${material}`, mount && `montaż ${mount}`, size && `wymiar ${size}`, voltage && `napięcie ${voltage}`].filter(Boolean);
  return [
    section(
      pick(product, platform, "electrical-label", ["Osprzęt elektryczny", "Wariant i seria", "Dane montażowe"]),
      facts.length ? facts.join(" • ") : leafCategory(product),
      paragraph(`${product.name} należy do grupy „${leafCategory(product)}”. Przy kompletowaniu osprzętu liczy się zgodność serii, mechanizmu, ramki, wariantu kolorystycznego i sposobu montażu.`),
    ),
    section("Kompletowanie", "Nie łącz elementów wyłącznie na podstawie wyglądu", list([
      escapeHtml("Porównaj producenta, serię i kod katalogowy każdego elementu."),
      escapeHtml("Sprawdź liczbę modułów, sposób mocowania i wymagane akcesoria."),
      escapeHtml("Podłączenie instalacji sieciowej powierz osobie z odpowiednimi kwalifikacjami."),
    ])),
  ];
}

function genericNarrative(product, platform, kind) {
  if (kind === "tape") return tapeNarrative(product, platform);
  if (kind === "profile") return profileNarrative(product, platform);
  if (kind === "power") return powerNarrative(product, platform);
  if (kind === "control") return controllerNarrative(product, platform);
  if (kind === "connector") return connectorNarrative(product, platform);
  if (["bulb", "tube", "module", "luminaire", "seasonal", "kit"].includes(kind)) return lightingNarrative(product, platform, kind);
  if (kind === "electrical") return electricalNarrative(product, platform);

  const type = leafCategory(product);
  const special = kind === "outlet"
    ? "Produkt znajduje się w kategorii Outlet. Przed zamówieniem sprawdź aktualny opis stanu, kompletność oraz warunki oferty na karcie produktu."
    : kind === "battery"
      ? "Porównaj oznaczenie ogniwa, napięcie i wymiary z urządzeniem, w którym ma pracować. Baterii o podobnym wyglądzie nie należy traktować jako zamiennych bez sprawdzenia symbolu."
      : kind === "ballast"
        ? "Statecznik dobierz do typu i mocy źródła światła oraz schematu połączeń oprawy. Samo dopasowanie wymiaru obudowy nie potwierdza zgodności elektrycznej."
        : `Produkt należy do kategorii „${type}”. Dobór oprzyj na kodzie katalogowym, wymiarach i parametrach podanych w aktualnej karcie.`;
  return [
    section(
      pick(product, platform, "generic-label", ["Zastosowanie", "Dobór produktu", "Najważniejsze informacje"]),
      type,
      paragraph(special),
    ),
  ];
}

function usefulSourceText(product) {
  const name = product.name.toLocaleLowerCase("pl");
  const lines = String(product.sourceDescription || "")
    .split("\n")
    .map(normalize)
    .filter((line) => line.length >= 20)
    .filter((line) => {
      const low = line.toLocaleLowerCase("pl");
      if ((name.includes("bez led") || name.includes("bez źródła")) && /zawiera źródło światła|ze źródłem światła/.test(low)) return false;
      if (name.includes("bez zasilacza") && /zasilacz (?:jest |w )?komplecie|zawiera zasilacz/.test(low)) return false;
      return true;
    });
  const text = lines.join(" ");
  if (text.length < 45) return "";
  const normalizedName = name.replace(/[^a-ząćęłńóśźż0-9]+/g, " ").trim();
  const normalizedText = text.toLocaleLowerCase("pl").replace(/[^a-ząćęłńóśźż0-9]+/g, " ").trim();
  if (normalizedText === normalizedName) return "";
  return text.slice(0, 3000);
}

function sourceSection(product, platform) {
  const source = usefulSourceText(product);
  if (!source) return "";
  const label = pick(product, platform, "source-label", ["Cechy i zastosowanie", "Informacje dodatkowe", "Opis produktu"]);
  const heading = pick(product, platform, "source-heading", [
    "Informacje zachowane z aktualnej karty produktu",
    "Szczegóły dotyczące tego wariantu",
    "Dodatkowe informacje producenta lub dostawcy",
  ]);
  return section(label, heading, paragraph(source));
}

function technicalSection(product, platform) {
  const items = [];
  for (const [label, rawValue] of Object.entries(product.attributes || {})) {
    const value = normalize(rawValue);
    if (!value || value === "-" || INTERNAL_ATTRIBUTES.has(label)) continue;
    items.push(important(label, value));
  }
  if (product.producer) items.unshift(important("Producent", product.producer));
  if (product.manufacturerCode) items.push(important("Kod producenta", product.manufacturerCode));
  if (product.code && product.code !== product.manufacturerCode) items.push(important("Kod produktu", product.code));
  if (product.ean) items.push(important("EAN", product.ean));
  return section(
    pick(product, platform, "technical-label", ["Dane techniczne", "Specyfikacja", "Parametry katalogowe"]),
    "Parametry tego konkretnego wariantu",
    list(items.length ? items : [escapeHtml("Brak dodatkowych parametrów technicznych w bieżącym eksporcie. Dobór oprzyj na nazwie oraz kodzie produktu.")]),
  );
}

function blogSection(product, platform, kind) {
  const links = BLOGS[kind];
  if (!links) return "";
  const cards = links.map(([title, subtitle, url]) => (
    `<div style="font-family:inherit;min-height:176px;padding:18px;margin:0;background:none!important;background-color:transparent!important;border:1px solid currentColor;border-radius:12px;box-shadow:none!important;color:inherit;display:flex;flex-direction:column;"><strong style="font-family:inherit;display:block;color:inherit!important;font-size:15px;line-height:1.35;margin-bottom:6px;font-weight:700;">${escapeHtml(title)}</strong><small style="font-family:inherit;display:block;color:inherit!important;opacity:.76;font-size:12px;line-height:1.4;margin-bottom:15px;">${escapeHtml(subtitle)}</small><a href="${escapeHtml(url)}" style="font-family:inherit;display:inline-block;min-width:142px;margin-top:auto;padding:10px 17px;border-radius:999px;background:#e94b25!important;background-color:#e94b25!important;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;text-decoration:none!important;text-align:center;line-height:1.2;border:0!important;align-self:flex-start;"><font color="#ffffff"><span style="font-family:inherit;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;text-decoration:none!important;font-weight:700;font-size:14px;">Czytaj poradnik</span></font></a></div>`
  )).join("");
  const heading = pick(product, platform, "blog-heading", [
    "Dobierz elementy instalacji bez zgadywania",
    "Praktyczna wiedza przed montażem",
    "Sprawdź dobór i zasady instalacji",
  ]);
  return `<section style="${STYLE.section}"><span style="${STYLE.pill}"><font color="#ffffff">Praktyczne poradniki</font></span><h3 style="${STYLE.heading}">${escapeHtml(heading)}</h3><p style="${STYLE.paragraph};margin-bottom:18px;">Materiały pomagają porównać parametry, przygotować montaż i uniknąć przypadkowego łączenia niezgodnych elementów.</p><div style="font-family:inherit;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;background:none!important;background-color:transparent!important;color:inherit;align-items:stretch;">${cards}</div></section>`;
}

const SEO_ADMIN_ATTRIBUTES = new Set([
  "Producent odpowiedzialny",
  "Podmiot odpowiedzialny",
  "Nazwa galerii",
  "Informacje o bezpieczeństwie",
]);

const SEO_BLOG_GUIDES = {
  "Taśmy LED": {
    heading: "Dobierz taśmę LED bez zgadywania",
    description: "Cztery poradniki prowadzą przez parametry, barwę, profil i warunki montażu potrzebne przed zakupem taśmy.",
    items: [
      ["Jak czytać parametry taśmy LED?", "Moc, lumeny, CRI, napięcie i IP", "https://www.prescot.com.pl/pl/n/23"],
      ["Montaż taśmy LED na zewnątrz", "IP, uszczelnienie i ochrona połączeń", "https://www.prescot.com.pl/pl/n/16"],
      ["Jak dobrać taśmę LED do mieszkania?", "Barwa, moc i miejsce montażu", "https://www.prescot.com.pl/pl/n/12"],
      ["Jak dobrać profil aluminiowy?", "Profil, klosz, chłodzenie i linia światła", "https://www.prescot.com.pl/pl/n/15"],
    ],
  },
  "Profile do taśm LED": {
    heading: "Dobierz profil i taśmę jako jeden układ",
    description: "Poradniki pomagają zestawić profil, klosz i taśmę oraz zaplanować chłodzenie i wygląd linii światła.",
    items: [
      ["Jak dobrać profil aluminiowy?", "Profil, klosz, chłodzenie i estetyka linii światła", "https://www.prescot.com.pl/pl/n/15"],
      ["Jak czytać parametry taśmy LED?", "Moc, lumeny, CRI, napięcie i IP", "https://www.prescot.com.pl/pl/n/23"],
      ["Jak dobrać taśmę LED do mieszkania?", "Barwa, moc i miejsce montażu", "https://www.prescot.com.pl/pl/n/12"],
    ],
  },
  "Zasilacze LED": {
    heading: "Dobierz zasilacz LED do instalacji",
    description: "Sprawdź sposób obliczania mocy, typ obudowy i stopień ochrony przed skompletowaniem układu LED.",
    items: [
      ["Jak dobrać zasilacz LED do taśmy?", "Moc W/m, długość taśmy i zapas mocy", "https://www.prescot.com.pl/pl/n/24"],
      ["Zasilacze LED — gdzie użyć którego?", "Desktop, gniazdkowy, siatkowy, slim i hermetyczny", "https://www.prescot.com.pl/pl/n/25"],
      ["Do czego służą zasilacze LED?", "Taśmy LED, moduły LED i sterowniki", "https://www.prescot.com.pl/pl/n/26"],
      ["Stopnie IP — dlaczego to ważne?", "IP20, IP33, IP44 i IP67 w praktyce", "https://www.prescot.com.pl/pl/n/27"],
    ],
  },
  "Sterowniki LED": {
    heading: "Skompletuj sterowanie i zasilanie LED",
    description: "Materiały wyjaśniają zależności między sterownikiem, taśmą, zasilaczem i profilem w jednym układzie.",
    items: [
      ["Jak dobrać zasilacz LED do taśmy?", "Moc W/m, długość odcinka i zapas mocy", "https://www.prescot.com.pl/pl/n/24"],
      ["Do czego służą zasilacze LED?", "Zasilacz, sterownik i taśma w jednym układzie", "https://www.prescot.com.pl/pl/n/26"],
      ["Jak czytać parametry taśmy LED?", "Napięcie, moc, lumeny i CRI w praktyce", "https://www.prescot.com.pl/pl/n/23"],
    ],
  },
  "Akcesoria do zasilaczy i taśm LED": {
    heading: "Sprawdź zgodność elementów instalacji LED",
    description: "Poradniki pomagają porównać napięcie, taśmę, profil i warunki montażu przed doborem osprzętu.",
    items: [
      ["Jak czytać parametry taśmy LED?", "Moc, lumeny, CRI, napięcie i IP", "https://www.prescot.com.pl/pl/n/23"],
      ["Jak dobrać profil aluminiowy?", "Profil, klosz, chłodzenie i linia światła", "https://www.prescot.com.pl/pl/n/15"],
      ["Montaż taśmy LED na zewnątrz", "IP, uszczelnienie i ochrona połączeń", "https://www.prescot.com.pl/pl/n/16"],
    ],
  },
};

function seoPillStyle(color) {
  return STYLE.pill.replaceAll("#e94b25", color);
}

function seoProductSpecs(product) {
  const seen = new Set();
  const specs = [];
  for (const [rawLabel, rawValue] of Object.entries(product.attributes || {})) {
    const label = normalize(rawLabel).replaceAll("_", " ");
    const value = normalize(rawValue);
    const identity = label.toLocaleLowerCase("pl");
    if (!value || value === "-" || SEO_ADMIN_ATTRIBUTES.has(label) || seen.has(identity)) continue;
    seen.add(identity);
    specs.push([label, value]);
  }
  return specs;
}

function seoSection(data, { color = "#e94b25", label = "", heading = "" } = {}) {
  const paragraphs = (data.paragraphs || []).map((value, index) => (
    `<p style="${STYLE.paragraph}${index ? "margin-top:10px;" : ""}">${escapeHtml(normalize(value))}</p>`
  )).join("");
  return `<section style="${STYLE.section}"><span style="${seoPillStyle(color)}"><font color="#ffffff">${escapeHtml(normalize(label || data.label))}</font></span><h3 style="${STYLE.heading}">${escapeHtml(normalize(heading || data.heading))}</h3>${paragraphs}</section>`;
}

function seoPoints(label, heading, points, color = "#e94b25") {
  const items = points.map((point) => `<li style="font-family:inherit;margin-bottom:7px;">${escapeHtml(normalize(point).replace(/\.$/, ""))}</li>`).join("");
  return `<section style="${STYLE.section}"><span style="${seoPillStyle(color)}"><font color="#ffffff">${escapeHtml(label)}</font></span><h3 style="${STYLE.heading}">${escapeHtml(heading)}</h3><ul style="${STYLE.list}">${items}</ul></section>`;
}

function seoSpecs(product, color = "#475569") {
  const items = seoProductSpecs(product).map(([label, value]) => (
    `<div style="display:flex;flex-direction:column;min-width:0;word-break:break-word;"><span style="font-size:12px;color:#64748b;margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px;">${escapeHtml(label)}</span><span style="font-size:15px;font-weight:700;color:inherit;">${escapeHtml(value)}</span></div>`
  )).join("");
  const code = product.manufacturerCode || product.code;
  return `<section style="${STYLE.section}"><span style="${seoPillStyle(color)}"><font color="#ffffff">Parametry</font></span><h3 style="${STYLE.heading}">Dane wariantu ${escapeHtml(code)}</h3><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:16px;margin-top:6px;">${items}</div></section>`;
}

function seoBenefits(points) {
  const cards = points.map((point) => (
    `<div style="display:flex;gap:10px;align-items:flex-start;padding:12px 14px;border:1px solid currentColor;border-radius:10px;"><span style="display:inline-flex;align-items:center;justify-content:center;flex:0 0 22px;width:22px;height:22px;border-radius:999px;background:#16a34a!important;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;font-weight:800;line-height:1;">✓</span><span style="font-size:14px;line-height:1.45;color:inherit;">${escapeHtml(normalize(point).replace(/\.$/, ""))}</span></div>`
  )).join("");
  return `<section style="${STYLE.section}"><span style="${seoPillStyle("#16a34a")}"><font color="#ffffff">Dlaczego warto</font></span><h3 style="${STYLE.heading}">Najważniejsze korzyści tego wariantu</h3><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px;margin-top:10px;">${cards}</div></section>`;
}

function seoGuides(product) {
  const guide = SEO_BLOG_GUIDES[product.categoryRoot];
  if (!guide) return "";
  const cards = guide.items.map(([title, description, url]) => (
    `<div style="font-family:inherit;min-height:190px;padding:18px;margin:0;background:none!important;background-color:transparent!important;border:1px solid currentColor;border-radius:12px;box-shadow:none!important;color:inherit;display:flex;flex-direction:column;"><strong style="font-family:inherit;display:block;color:inherit!important;font-size:15px;line-height:1.35;margin-bottom:6px;">${escapeHtml(title)}</strong><small style="font-family:inherit;display:block;color:inherit!important;opacity:.78;font-size:13px;line-height:1.45;margin-bottom:14px;">${escapeHtml(description)}</small><a href="${escapeHtml(url)}" style="font-family:inherit;display:inline-block;min-width:142px;margin-top:auto;padding:10px 17px;border-radius:999px;background:#e94b25!important;background-color:#e94b25!important;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;font-size:14px;font-weight:700;text-decoration:none!important;text-align:center;line-height:1.2;border:0!important;align-self:flex-start;">Czytaj poradnik</a></div>`
  )).join("");
  return `<section style="${STYLE.section}"><div style="font-family:inherit;margin-bottom:18px;background:none!important;background-color:transparent!important;color:inherit;"><span style="${seoPillStyle("#e94b25")}"><font color="#ffffff">Praktyczne poradniki</font></span><h3 style="${STYLE.heading}">${escapeHtml(guide.heading)}</h3><p style="${STYLE.paragraph}">${escapeHtml(guide.description)}</p></div><div style="font-family:inherit;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;background:none!important;background-color:transparent!important;color:inherit;align-items:stretch;">${cards}</div></section>`;
}

function seoWapro(product, result) {
  const identifierLabels = new Set(["producent", "kod produktu", "kod producenta", "ean"]);
  const specs = seoProductSpecs(product);
  const features = specs.filter(([label]) => !identifierLabels.has(label.toLocaleLowerCase("pl"))).slice(0, 7).map(([label, value]) => `${label}: ${value}`);
  const identifiers = specs.filter(([label]) => ["kod produktu", "kod producenta", "ean"].includes(label.toLocaleLowerCase("pl"))).map(([label, value]) => `${label}: ${value}`);
  const points = (values) => values.map((value) => `<p>- ${escapeHtml(normalize(value).replace(/\.$/, ""))}</p>`).join("");
  const intro = result.sections[0].paragraphs.map(normalize).join(" ");
  const featurePoints = features.length ? features : result.benefits;
  const benefitBlock = features.length ? `<h3>Dlaczego warto:</h3>${points(result.benefits)}` : "";
  return `<section><h2>${escapeHtml(product.name)}</h2><p>${escapeHtml(intro)}</p><h3>Najważniejsze cechy:</h3>${points(featurePoints)}${benefitBlock}<h3>Gdzie użyć:</h3>${points(result.applications)}<h3>Dobór bez pomyłki:</h3>${points([...result.selection_checks, ...identifiers])}</section>`;
}

function seoTim(product, result) {
  const code = product.manufacturerCode || product.code;
  const points = (values) => values.map((value) => `<li>${escapeHtml(normalize(value).replace(/\.$/, ""))}</li>`).join("");
  const specs = seoProductSpecs(product).map(([label, value]) => `${label}: ${value}`);
  return `<section><h2>Opis dla TIM.pl: ${escapeHtml(product.name)}</h2><p>${escapeHtml(normalize(result.channel_leads.tim))}</p><h3>Dane techniczne modelu ${escapeHtml(code)}</h3><ul>${points(specs)}</ul><h3>Zastosowanie i dobór</h3><ul>${points([...result.applications, ...result.selection_checks])}</ul><h3>Uwagi dla instalatora</h3><ul>${points(result.installation_notes)}</ul></section>`;
}

export function renderSeoDescription(product, saved, platform = "shoper") {
  const result = saved?.editorial || saved;
  if (!result?.sections?.length) return generateDescription(product, platform);
  const selected = PLATFORM_NAMES[platform] ? platform : "shoper";
  if (selected === "wapro") return seoWapro(product, result);
  if (selected === "shoper") {
    const family = result.rule_family || "";
    const identifier = product.ean || product.manufacturerCode || product.code;
    const sourceSections = result.sections.map((item) => ({ ...item, paragraphs: [...(item.paragraphs || [])] }));
    const narration = normalize(sourceSections.flatMap((item) => [item.heading, ...item.paragraphs]).join(" "));
    if (identifier && !narration.includes(identifier)) {
      sourceSections[0].paragraphs.push(`Identyfikacja wariantu: kod ${product.manufacturerCode || product.code}; EAN ${product.ean || "nie nadano"}.`);
    }
    const sections = sourceSections.map((item) => seoSection(item));
    if (family === "power") {
      return [sections[0], sections[1], seoSpecs(product), seoGuides(product)].filter(Boolean).join("\n");
    }
    return [...sections, seoGuides(product)].filter(Boolean).join("\n");
  }
  if (selected === "tim") return seoTim(product, result);
  return [
    seoSection({ label: "Sprawdź przed zakupem", heading: result.seo_title, paragraphs: [result.channel_leads.allegro] }, { color: "#16a34a" }),
    seoBenefits(result.benefits),
    seoSection(result.sections[1], { color: "#16a34a", label: "Gdzie użyć" }),
    seoSpecs(product, "#16a34a"),
    seoPoints("Dobór bez pomyłki", "Co sprawdzić przed montażem", [...result.selection_checks, ...result.installation_notes], "#16a34a"),
  ].join("\n");
}

export function generateDescription(product, platform = "shoper") {
  const selectedPlatform = PLATFORM_NAMES[platform] ? platform : "shoper";
  const kind = productKind(product);
  const parts = [
    identitySection(product, selectedPlatform),
    ...genericNarrative(product, selectedPlatform, kind),
    sourceSection(product, selectedPlatform),
    technicalSection(product, selectedPlatform),
    blogSection(product, selectedPlatform, kind),
  ];
  return parts.filter(Boolean).join("\n");
}

export function plainTextFromHtml(htmlValue) {
  return normalize(String(htmlValue || "").replace(/<[^>]*>/g, " ").replaceAll("&nbsp;", " "));
}

export function productType(product) {
  return productKind(product);
}

export { PLATFORM_NAMES };
