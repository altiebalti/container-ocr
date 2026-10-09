// Презентація до лаби 2: Container OCR на Google Cloud Vision API
const pptxgen = require("pptxgenjs");
const path = require("path");
const { applyTheme } = require("<шлях до pptx-скіла>/scripts/apply_theme.js");

const REPO = "/Users/whoalti/Documents/uni/cloud-computing/container-ocr";
const OUT = process.argv[2] || "container-ocr-presentation.pptx";

const THEME = {
  name: "Container OCR",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "0B2545",   // глибокий синій (море)
    lt1: "FFFFFF",
    dk2: "13315C",   // синій для панелей
    lt2: "EEF2F7",   // світло-сіра підкладка карток
    accent1: "D9552B", // іржаво-помаранчевий, колір контейнера
    accent2: "8DA9C4", // сталевий
    accent3: "2A9D8F", // зелений для valid
    accent4: "E9C46A", // жовтий для попереджень
    accent5: "C8102E", // червоний для invalid
    accent6: "5C6B7A", // сірий для підписів
    hlink: "D9552B",
    folHlink: "8DA9C4",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10" x 5.625"
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "Олександр Тимченко";
pres.title = "Container OCR: номер контейнера з фото через Google Cloud Vision API";
const C = pres.SchemeColor;
const W = 10, H = 5.625, M = 0.5;

// ---------- layouts ----------
pres.defineSlideMaster({
  title: "DARK",
  background: { color: THEME.colors.dk1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 1.2, w: 6.3, h: 1.9, fontSize: 32, bold: true, color: C.background1, align: "left", valign: "bottom", margin: 0 } } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 3.2, w: W - 2 * M, h: 1.0, fontSize: 18, color: C.accent2, align: "left", valign: "top", margin: 0 } } },
  ],
});
pres.defineSlideMaster({
  title: "LIGHT",
  background: { color: THEME.colors.lt1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 0.7, fontSize: 28, bold: true, color: C.text1, align: "left", valign: "middle", margin: 0 } } },
    { text: { text: "Container OCR · Google Cloud Vision API", options: { x: M, y: H - 0.4, w: 6, h: 0.3, fontSize: 9, color: C.accent6, margin: 0 } } },
  ],
  slideNumber: { x: W - 1.0, y: H - 0.4, w: 0.5, h: 0.3, fontSize: 9, color: THEME.colors.accent6 },
});

// ---------- helpers ----------
let n = 0;
const slide = (master, section) => { n++; return pres.addSlide({ masterName: master, sectionTitle: section }); };
const title = (s, t) => s.addText(t, { placeholder: "title" });
const text = (s, t, o) => s.addText(t, Object.assign({ isTextBox: true, fontSize: 14, color: C.text1, margin: 0, valign: "top" }, o));
const bullets = (s, items, o) => s.addText(items.map((t, i) => ({ text: t, options: { bullet: { indent: 14 }, breakLine: i < items.length - 1, paraSpaceAfter: 6 } })),
  Object.assign({ isTextBox: true, fontSize: 14, color: C.text1, margin: 0, valign: "top" }, o));
const card = (s, x, y, w, h, fill) => s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill || C.background2 }, line: { color: fill || C.background2 }, rectRadius: 0.08 });
const circle = (s, x, y, d, label, fill) => {
  s.addShape(pres.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color: fill || C.accent1 }, line: { color: fill || C.accent1 } });
  s.addText(label, { x, y, w: d, h: d, isTextBox: true, fontSize: d > 0.5 ? 16 : 12, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0 });
};
const box = (s, x, y, w, h, t, fill, fontColor, fs) => {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.06 });
  s.addText(t, { x, y, w, h, isTextBox: true, fontSize: fs || 12, color: fontColor || C.background1, align: "center", valign: "middle", margin: 0.05, bold: true });
};
const arrow = (s, x1, y1, x2, y2, label) => {
  s.addShape(pres.ShapeType.line, { x: x1, y: y1, w: x2 - x1, h: y2 - y1, line: { color: C.accent6, width: 1.5, endArrowType: "triangle" } });
  if (label) s.addText(label, { x: Math.min(x1, x2), y: Math.min(y1, y2) - 0.28, w: Math.abs(x2 - x1) || 1.2, h: 0.25, isTextBox: true, fontSize: 9, color: C.accent6, align: "center", valign: "bottom", margin: 0 });
};
const mono = (s, t, o) => s.addText(t, Object.assign({ isTextBox: true, fontFace: "Courier New", fontSize: 11, color: C.text1, margin: 0.08, valign: "top" }, o));

// ================= 1. Титул =================
pres.addSection({ title: "Вступ" });
{
  const s = slide("DARK", "Вступ");
  s.addText("Лабораторна робота 2 · Хмарні обчислення", { x: M, y: 0.6, w: 6, h: 0.3, isTextBox: true, fontSize: 12, color: C.accent1, bold: true, margin: 0 });
  title(s, "Номер контейнера з фото: Google Cloud Vision API у PoC-сервісі");
  s.addText("Cloud Run · Cloud Vision · Firestore · Cloud Storage", { placeholder: "body" });
  s.addText([
    { text: "Олександр Тимченко, група ТК-41", options: { bold: true, breakLine: true } },
    { text: "КНУ імені Тараса Шевченка, факультет комп'ютерних наук та кібернетики", options: {} },
  ], { x: M, y: 4.45, w: 7, h: 0.6, isTextBox: true, fontSize: 12, color: C.background1, margin: 0 });
  // мотив: силует контейнера праворуч
  s.addShape(pres.ShapeType.roundRect, { x: 7.1, y: 0.9, w: 2.4, h: 1.5, fill: { color: C.accent1 }, line: { color: C.accent1 }, rectRadius: 0.05 });
  for (let i = 0; i < 7; i++) s.addShape(pres.ShapeType.rect, { x: 7.25 + i * 0.32, y: 1.0, w: 0.1, h: 1.3, fill: { color: THEME.colors.dk1, transparency: 75 }, line: { color: THEME.colors.dk1, transparency: 75 } });
  s.addText("CSQU 305438 3", { x: 7.1, y: 2.45, w: 2.4, h: 0.3, isTextBox: true, fontFace: "Courier New", fontSize: 12, bold: true, color: C.background1, align: "center", margin: 0 });
  s.addNotes("Тема: інтеграція з Google Cloud Vision API у PoC-сервісі для розпізнавання номерів вантажних контейнерів. План: задача, сфери застосування, сам API, архітектура, стандарт ISO 6346, API сервісу, демо, обмеження, висновки.");
}

// ================= 2. Задача =================
{
  const s = slide("LIGHT", "Вступ");
  title(s, "Задача: номер контейнера вводять руками");
  text(s, "Кожен вантажний контейнер має унікальний номер за ISO 6346. На терміналі, складі чи митниці його переписують з борту в систему вручну або диктують по рації. Будь-яка помилка в одному символі означає втрачений контейнер, затримку й ручний пошук.", { x: M, y: 1.25, w: 5.2, h: 1.6, fontSize: 14 });
  text(s, "Ідея PoC: сфотографувати двері контейнера телефоном, а хмарний OCR і перевірка контрольної цифри зроблять решту.", { x: M, y: 2.95, w: 5.2, h: 0.9, fontSize: 14, bold: true, color: C.accent1 });
  // stat callouts
  const stats = [["11", "символів у номері"], ["1", "контрольна цифра, що ловить помилку"], ["< 1 с", "на розпізнавання у хмарі"]];
  stats.forEach(([v, l], i) => {
    const y = 1.2 + i * 1.25;
    card(s, 6.1, y, 3.4, 1.05);
    text(s, v, { x: 6.3, y: y + 0.12, w: 1.3, h: 0.8, fontSize: 32, bold: true, color: C.accent1, fontFace: THEME.headFontFace, valign: "middle" });
    text(s, l, { x: 7.6, y: y + 0.12, w: 1.8, h: 0.8, fontSize: 12, color: C.accent6, valign: "middle" });
  });
  s.addNotes("Проблема ручного введення: номери довгі, нанесені на іржаві та брудні поверхні, читаються в русі. Помилка в одному символі ламає облік. Контрольна цифра в стандарті існує саме для цього, але вона лише виявляє помилку, не прибирає ручну працю.");
}

// ================= 3. Сфери застосування =================
{
  const s = slide("LIGHT", "Вступ");
  title(s, "Сфери застосування");
  const items = [
    ["Gate check", "в'їзд на термінал: фото з камери на шлагбаумі, звірка з бронюванням"],
    ["Інвентаризація", "обхід складу з телефоном замість паперового списку"],
    ["Огляд і пломби", "фіксація стану контейнера й пломби разом з фото"],
    ["Митний контроль", "швидка ідентифікація без ручного пошуку в декларації"],
    ["Звірка з документами", "номер у накладній проти номера на борту"],
    ["Логістичні застосунки", "водій підтверджує отримання одним знімком"],
  ];
  items.forEach(([h, d], i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = M + col * 3.1, y = 1.3 + row * 1.95;
    card(s, x, y, 2.9, 1.75);
    circle(s, x + 0.2, y + 0.2, 0.45, String(i + 1));
    text(s, h, { x: x + 0.8, y: y + 0.22, w: 2.0, h: 0.4, fontSize: 15, bold: true, valign: "middle" });
    text(s, d, { x: x + 0.2, y: y + 0.8, w: 2.5, h: 0.9, fontSize: 12, color: C.accent6 });
  });
  s.addNotes("Усюди один і той самий сценарій: є фото, потрібен номер у системі. Відрізняються лише джерело фото (камера на воротах чи телефон) і те, з чим номер звіряється далі.");
}

// ================= 4. Cloud Vision API =================
pres.addSection({ title: "Google Cloud Vision API" });
{
  const s = slide("LIGHT", "Google Cloud Vision API");
  title(s, "Google Cloud Vision API: що вміє");
  text(s, "Готова модель комп'ютерного зору як REST/gRPC-сервіс. Один запит images:annotate, у ньому перелік потрібних «функцій», у відповіді анотації з координатами.", { x: M, y: 1.2, w: 9, h: 0.6, fontSize: 13, color: C.accent6 });
  const feats = [
    ["TEXT_DETECTION", "OCR: текст на фото, слова з координатами. Використано в PoC"],
    ["DOCUMENT_TEXT_\nDETECTION", "OCR для щільного тексту: сторінки, блоки, абзаци"],
    ["LABEL_DETECTION", "мітки: що на зображенні"],
    ["OBJECT_LOCALIZATION", "об'єкти з рамками"],
    ["LOGO / LANDMARK", "логотипи і відомі місця"],
    ["FACE_DETECTION", "обличчя й емоції (без ідентифікації)"],
    ["SAFE_SEARCH", "небажаний контент"],
    ["WEB_DETECTION", "схожі зображення в інтернеті"],
  ];
  feats.forEach(([h, d], i) => {
    const col = i % 4, row = Math.floor(i / 4);
    const x = M + col * 2.3, y = 1.95 + row * 1.5;
    card(s, x, y, 2.15, 1.35, i === 0 ? C.accent1 : C.background2);
    text(s, h, { x: x + 0.15, y: y + 0.12, w: 1.9, h: 0.45, fontSize: 11, bold: true, fontFace: "Courier New", color: i === 0 ? C.background1 : C.text1 });
    text(s, d, { x: x + 0.15, y: y + 0.55, w: 1.9, h: 0.75, fontSize: 11, color: i === 0 ? C.background1 : C.accent6 });
  });
  text(s, "Ціна: перші 1000 зображень на місяць безкоштовно для кожної функції, далі $1,50 за 1000 (TEXT_DETECTION).", { x: M, y: 4.95, w: 9, h: 0.3, fontSize: 11, color: C.accent6 });
  s.addNotes("Vision API не треба навчати: це готова модель Google. Для нас потрібна лише функція TEXT_DETECTION. DOCUMENT_TEXT_DETECTION краща для сканів документів, а на фото контейнерів дає більше шуму. Ціна з офіційного прайсу: 1000 зображень на місяць безкоштовно.");
}

// ================= 5. Запит і відповідь Vision =================
{
  const s = slide("LIGHT", "Google Cloud Vision API");
  title(s, "Запит і відповідь Vision API");
  text(s, "POST https://vision.googleapis.com/v1/images:annotate", { x: M, y: 1.2, w: 4.4, h: 0.3, fontSize: 9.5, fontFace: "Courier New", color: C.accent1, bold: true });
  card(s, M, 1.55, 4.4, 3.5);
  mono(s, [
    "{", '  "requests": [{', '    "image": { "content": "<base64 JPEG>" },', '    "features": [', '      { "type": "TEXT_DETECTION" }', "    ],",
    '    "imageContext": {', '      "languageHints": ["en"]', "    }", "  }]", "}",
  ].join("\n"), { x: M, y: 1.55, w: 4.4, h: 3.5, fontSize: 11 });
  text(s, "Відповідь (фрагмент)", { x: 5.2, y: 1.2, w: 4.3, h: 0.3, fontSize: 11, color: C.accent1, bold: true });
  card(s, 5.2, 1.55, 4.3, 3.5);
  mono(s, [
    '"textAnnotations": [', '  { "description": "CSQU 305438 3\\n45G1\\nMAX. GROSS ..." },', '  { "description": "CSQU",', '    "boundingPoly": { "vertices": [',
    '      {"x": 643, "y": 132}, {"x": 790, "y": 132},', '      {"x": 790, "y": 217}, {"x": 643, "y": 217} ] } },', '  { "description": "305438", ... },', '  { "description": "3", ... }', "]",
  ].join("\n"), { x: 5.2, y: 1.55, w: 4.3, h: 3.5, fontSize: 10 });
  text(s, "Перший елемент — весь текст, далі кожне слово з рамкою. Саме рамки дають змогу зібрати номер зі шматків і намалювати його на фото.", { x: M, y: 5.1, w: 9, h: 0.3, fontSize: 11, color: C.accent6 });
  s.addNotes("У Python використано клієнтську бібліотеку google-cloud-vision, яка загортає цей самий REST-запит. Автентифікація через сервісний акаунт Cloud Run, ключів у коді немає.");
}

// ================= 6. Архітектура =================
pres.addSection({ title: "Архітектура PoC" });
{
  const s = slide("LIGHT", "Архітектура PoC");
  title(s, "Архітектура PoC");
  // вузли
  box(s, 0.5, 2.35, 1.7, 1.0, "Телефон / браузер\ncurl, Postman", C.accent2, C.text1, 11);
  box(s, 3.4, 2.35, 2.2, 1.0, "Cloud Run\nFastAPI (Python)", C.accent1, C.background1, 12);
  box(s, 7.3, 1.25, 2.2, 0.8, "Cloud Vision API\nTEXT_DETECTION", THEME.colors.dk2, C.background1, 11);
  box(s, 7.3, 2.5, 2.2, 0.7, "Firestore\nколекція scans", THEME.colors.dk2, C.background1, 11);
  box(s, 7.3, 3.65, 2.2, 0.7, "Cloud Storage\nфото + мініатюра", THEME.colors.dk2, C.background1, 11);
  box(s, 3.4, 4.05, 2.2, 0.6, "Cloud Build + Artifact Registry\nзбірка образу з Dockerfile", C.background2, C.accent6, 9);
  // стрілки
  arrow(s, 2.2, 2.85, 3.4, 2.85, "POST /api/scan\nX-API-Key");
  arrow(s, 5.6, 2.55, 7.3, 1.7, "");
  text(s, "фото →\nтекст + координати слів", { x: 5.3, y: 1.35, w: 1.9, h: 0.4, fontSize: 9, color: C.accent6, align: "center" });
  arrow(s, 5.6, 2.85, 7.3, 2.85, "запис сканування");
  arrow(s, 5.6, 3.15, 7.3, 3.95, "");
  text(s, "JPEG + мініатюра", { x: 5.9, y: 3.75, w: 1.4, h: 0.3, fontSize: 9, color: C.accent6, align: "center" });
  s.addShape(pres.ShapeType.line, { x: 4.5, y: 3.35, w: 0, h: 0.7, line: { color: C.accent6, width: 1, dashType: "dash" } });
  text(s, "IAM: окремий сервісний акаунт для Cloud Run з ролями datastore.user, storage.objectAdmin на один бакет, serviceUsageConsumer. Доступ ззовні лише з API-ключем, max-instances 2.", { x: M, y: 4.8, w: 9, h: 0.45, fontSize: 10, color: C.accent6 });
  s.addNotes("Усі компоненти serverless: Cloud Run масштабується до нуля, Firestore і Storage оплачуються за використання. Vision викликається від імені сервісного акаунта, тому ключів у коді немає. Збірка: gcloud run deploy --source запускає Cloud Build, образ лягає в Artifact Registry.");
}

// ================= 7. Взаємодія сервісів =================
{
  const s = slide("LIGHT", "Архітектура PoC");
  title(s, "Один запит: як взаємодіють сервіси");
  const steps = [
    ["Підготовка", "EXIF-орієнтація, зменшення до 2400 px, JPEG"],
    ["Vision API", "TEXT_DETECTION: повний текст і слова з рамками"],
    ["Пошук номера", "AAAU 000000 0 в одному слові, кількох або вертикально"],
    ["Контрольна цифра", "перевірка; виправлення O/0, I/1, S/5, B/8 лише якщо цифра зійшлась"],
    ["Код типу", "45G1 = 40 футів, high cube, універсальний"],
    ["Збереження", "запис у Firestore, фото й мініатюра в Cloud Storage"],
  ];
  steps.forEach(([h, d], i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = M + col * 3.1, y = 1.3 + row * 1.95;
    card(s, x, y, 2.9, 1.75);
    circle(s, x + 0.2, y + 0.2, 0.45, String(i + 1), i === 1 ? C.accent1 : THEME.colors.dk2);
    text(s, h, { x: x + 0.8, y: y + 0.22, w: 2.0, h: 0.4, fontSize: 15, bold: true, valign: "middle" });
    text(s, d, { x: x + 0.2, y: y + 0.8, w: 2.5, h: 0.9, fontSize: 12, color: C.accent6 });
  });
  s.addNotes("Типовий час: підготовка 40-140 мс, Vision 150-700 мс (до 2 с при холодному старті), збереження 300-400 мс. Усе разом менше секунди в теплому стані.");
}

// ================= 8. ISO 6346 =================
pres.addSection({ title: "ISO 6346" });
{
  const s = slide("LIGHT", "ISO 6346");
  title(s, "ISO 6346: структура номера і контрольна цифра");
  // розбір номера
  const parts = [["CSQ", "код власника", C.accent1], ["U", "категорія\n(U = вантажний)", THEME.colors.dk2], ["305438", "серійний номер", C.accent1], ["3", "контрольна\nцифра", C.accent3]];
  let x = M;
  parts.forEach(([v, l, col]) => {
    const w = 0.28 * v.length + 0.45;
    box(s, x, 1.25, w, 0.6, v, col, C.background1, 20);
    text(s, l, { x, y: 1.9, w: Math.max(w, 1.1), h: 0.5, fontSize: 10, color: C.accent6, align: "center" });
    x += w + 0.15;
  });
  s.addImage({ path: path.join(REPO, "samples/door_valid.jpg"), x: 6.3, y: 1.2, w: 3.2, h: 2.4, rounding: false });
  text(s, "Синтетичне фото з samples/: сервіс повертає status = valid, рамку номера і код типу 45G1", { x: 6.3, y: 3.65, w: 3.2, h: 0.45, fontSize: 9, color: C.accent6 });
  // формула
  text(s, "Як рахується контрольна цифра", { x: M, y: 2.6, w: 5.5, h: 0.3, fontSize: 13, bold: true });
  bullets(s, [
    "Літери переводяться в числа: A=10, B=12, C=13 … Z=38, значення кратні 11 пропускаються",
    "Кожен з 10 символів множиться на 2 у степені позиції (1, 2, 4 … 512), усе додається",
    "Остача від ділення на 11 і є цифра; якщо вийшло 10, пишуть 0",
  ], { x: M, y: 2.95, w: 5.6, h: 1.2, fontSize: 12 });
  card(s, M, 4.2, 5.6, 0.9);
  mono(s, "CSQU 305438: 13·1 + 30·2 + 28·4 + 32·8 + 3·16 + 0·32 + 5·64 + 4·128 + 3·256 + 8·512 = 6185\n6185 mod 11 = 3  ✓", { x: M, y: 4.2, w: 5.6, h: 0.9, fontSize: 11, valign: "middle" });
  s.addNotes("Контрольна цифра ловить будь-яку помилку в одному символі і більшість у двох. Саме тому сервіс дозволяє виправляти схожі символи OCR лише тоді, коли після виправлення цифра сходиться.");
}

// ================= 9. API сервісу =================
pres.addSection({ title: "API сервісу" });
{
  const s = slide("LIGHT", "API сервісу");
  title(s, "API сервісу");
  const rows = [
    [{ text: "Метод", options: { bold: true, color: THEME.colors.lt1, fill: { color: THEME.colors.dk2 } } }, { text: "Шлях", options: { bold: true, color: THEME.colors.lt1, fill: { color: THEME.colors.dk2 } } }, { text: "Опис", options: { bold: true, color: THEME.colors.lt1, fill: { color: THEME.colors.dk2 } } }],
    ["POST", "/api/scan?mode=text|document&save=true", "розпізнати фото (поле file)"],
    ["GET", "/api/scans?limit=20", "останні сканування з Firestore"],
    ["GET", "/api/scans/{id}", "одне сканування"],
    ["GET", "/api/scans/{id}/image?thumb=1", "фото з Cloud Storage"],
    ["GET", "/api/info", "налаштування сервісу (без ключа)"],
    ["GET", "/docs", "OpenAPI / Swagger UI"],
  ];
  s.addTable(rows, { x: M, y: 1.2, w: 5.4, colW: [0.7, 2.7, 2.0], fontSize: 10, fontFace: "Calibri", color: THEME.colors.dk1, border: { type: "solid", color: "D5DCE6", pt: 0.5 }, rowH: 0.36, valign: "middle", margin: 0.05 });
  text(s, "Захист: заголовок X-API-Key, ключ генерує deploy.sh. Усі ендпоінти, крім /api/info і /docs, вимагають ключ.", { x: M, y: 3.9, w: 5.4, h: 0.6, fontSize: 11, color: C.accent6 });
  // статуси
  text(s, "Значення status у відповіді", { x: 6.3, y: 1.2, w: 3.2, h: 0.3, fontSize: 13, bold: true });
  const st = [["valid", "номер знайдено, цифра сходиться", C.accent3], ["invalid_check_digit", "номер є, але цифра не сходиться", C.accent5], ["check_digit_missing", "цифру в рамці не прочитано, її обчислено", C.accent4], ["not_found", "номера в тексті немає", C.accent6]];
  st.forEach(([k, d, col], i) => {
    const y = 1.6 + i * 0.85;
    s.addShape(pres.ShapeType.ellipse, { x: 6.3, y: y + 0.08, w: 0.22, h: 0.22, fill: { color: col }, line: { color: col } });
    text(s, k, { x: 6.65, y, w: 2.9, h: 0.3, fontSize: 11, bold: true, fontFace: "Courier New" });
    text(s, d, { x: 6.65, y: y + 0.3, w: 2.9, h: 0.5, fontSize: 11, color: C.accent6 });
  });
  s.addNotes("FastAPI генерує OpenAPI-схему автоматично, тому /docs можна показати наживо. Статуси розрізняють помилку OCR і помилку на самому контейнері: обидві дають invalid_check_digit, і людина має глянути на фото.");
}

// ================= 10. Приклад відповіді =================
{
  const s = slide("LIGHT", "API сервісу");
  title(s, "Приклад: POST /api/scan на справжньому сервісі");
  card(s, M, 1.2, 4.4, 3.9);
  mono(s, [
    "$ curl -H \"X-API-Key: $KEY\" \\", "    -F file=@door_valid.jpg $URL/api/scan", "", "{", '  "status": "valid",', '  "container": {', '    "number": "CSQU3054383",', '    "formatted": "CSQU 305438 3",',
    '    "owner_code": "CSQ", "serial": "305438",', '    "check_digit": 3, "expected_check_digit": 3,', '    "corrected": false,', '    "box": [643, 132, 1475, 217]', "  },", '  "size_type": { "code": "45G1", "length": "40 футів", ... },',
    '  "timings_ms": { "prepare": 142, "ocr": 1706, "total": 1848 },', '  "stored": true, "image_stored": true', "}",
  ].join("\n"), { x: M, y: 1.2, w: 4.4, h: 3.9, fontSize: 9.5 });
  s.addImage({ path: path.join(REPO, "samples/real/CMAU4307598_door.jpg"), x: 5.3, y: 1.2, w: 1.6, h: 3.15 });
  s.addImage({ path: path.join(REPO, "samples/real/APZU3737897_door.jpg"), x: 7.1, y: 1.2, w: 2.15, h: 3.15 });
  text(s, "Справжні фото (Wikimedia Commons): CMAU 430759 8 і APZU 373789 7, обидва valid", { x: 5.3, y: 4.5, w: 4.2, h: 0.55, fontSize: 10, color: C.accent6 });
  s.addNotes("Відповідь містить усе для інтеграції: сам номер, розбір на частини, рамку для підсвітки на фото, таймінги. Перший запит після простою довший через холодний старт Cloud Run і Vision.");
}

// ================= 11. Демо =================
pres.addSection({ title: "Демо" });
{
  const s = slide("DARK", "Демо");
  s.addText("Демо", { x: M, y: 0.4, w: 3, h: 0.5, isTextBox: true, fontSize: 28, bold: true, color: C.background1, fontFace: THEME.headFontFace, margin: 0 });
  s.addShape(pres.ShapeType.roundRect, { x: 1.9, y: 1.0, w: 6.2, h: 3.5, fill: { color: THEME.colors.dk2 }, line: { color: C.accent2, width: 1 }, rectRadius: 0.08 });
  s.addShape(pres.ShapeType.ellipse, { x: 4.55, y: 2.3, w: 0.9, h: 0.9, fill: { color: C.accent1 }, line: { color: C.accent1 } });
  s.addShape(pres.ShapeType.triangle, { x: 4.85, y: 2.52, w: 0.42, h: 0.46, rotate: 90, fill: { color: C.background1 }, line: { color: C.background1 } });
  s.addText("Сюди вставляється demo.mp4 (Вставлення → Відео → Цей пристрій)", { x: 1.9, y: 3.95, w: 6.2, h: 0.4, isTextBox: true, fontSize: 11, color: C.accent2, align: "center", margin: 0 });
  bullets(s, [
    "Телефон: фото дверей контейнера, номер і зелений статус",
    "Фото з помилкою: червоний статус і очікувана цифра",
    "curl і JSON-відповідь, Swagger на /docs",
    "Консоль GCP: Firestore, Cloud Storage, логи Cloud Run",
  ], { x: M, y: 4.6, w: 9, h: 0.9, fontSize: 11, color: C.accent2 });
  s.addNotes("Відео приблизно 2 хвилини. Після відео можна відкрити сервіс наживо, якщо є інтернет.");
}

// ================= 12. Результати на реальних фото =================
pres.addSection({ title: "Результати" });
{
  const s = slide("LIGHT", "Результати");
  title(s, "Перевірка на справжніх фото з Wikimedia Commons");
  const stats = [["4 з 14", "загальний план здалеку,\nкілька контейнерів у кадрі"], ["3 з 10", "крупний план з тих,\nщо не впізнались"], ["7 з 14", "разом номер\nпрочитано"]];
  stats.forEach(([v, l], i) => {
    const x = M + i * 3.1;
    card(s, x, 1.25, 2.9, 1.3, i === 2 ? C.accent1 : C.background2);
    text(s, v, { x: x + 0.2, y: 1.35, w: 2.5, h: 0.6, fontSize: 28, bold: true, fontFace: THEME.headFontFace, color: i === 2 ? C.background1 : C.accent1 });
    text(s, l, { x: x + 0.2, y: 1.95, w: 2.5, h: 0.55, fontSize: 11, color: i === 2 ? C.background1 : C.accent6 });
  });
  s.addImage({ path: path.join(REPO, "samples/real/GESU2796740_door.jpg"), x: M, y: 2.8, w: 2.9, h: 1.95 });
  s.addImage({ path: path.join(REPO, "samples/real/GLDU2976203_door.jpg"), x: 3.6, y: 2.8, w: 2.9, h: 1.7 });
  s.addImage({ path: path.join(REPO, "samples/real/TCLU4684070_door.jpg"), x: 6.7, y: 2.8, w: 1.1, h: 1.95 });
  text(s, "valid: GESU 279674 0", { x: M, y: 4.8, w: 2.9, h: 0.3, fontSize: 10, color: C.accent3, bold: true });
  text(s, "invalid_check_digit: GLDU прочитано як GLOU", { x: 3.6, y: 4.55, w: 2.9, h: 0.5, fontSize: 10, color: C.accent5, bold: true });
  text(s, "not_found: вертикальний напис", { x: 6.7, y: 4.8, w: 2.9, h: 0.3, fontSize: 10, color: C.accent6, bold: true });
  text(s, "Ім'я файлу = правильний номер, тож результат перевірявся автоматично. Повна таблиця в samples/real/README.md.", { x: 7.9, y: 2.8, w: 1.6, h: 1.6, fontSize: 9, color: C.accent6 });
  s.addNotes("Фото зняті не для OCR: здалеку, з кількома контейнерами в кадрі. У цільовому сценарії користувач фотографує двері зблизька, і тоді результат помітно кращий. Три типи помилок: дрібний текст, вертикальні написи, схожі літери.");
}

// ================= 13. Обмеження =================
{
  const s = slide("LIGHT", "Результати");
  title(s, "Обмеження і що можна покращити");
  const left = [
    ["Вертикальні написи", "Vision читає їх посимвольно, номер не складається"],
    ["Дрібний текст здалеку", "потрібен крупний план або кадрування за рамкою"],
    ["Схожі літери D/O, M/H", "виправляються лише пари цифра/літера"],
    ["Цифра в рамці", "читається гірше за решту символів"],
  ];
  const right = [
    ["Document AI або власна модель на Vertex AI", "дотренувати на фото контейнерів"],
    ["Кадрування за детектором", "спочатку знайти табличку з номером, потім OCR"],
    ["Secret Manager", "замість змінної середовища для API-ключа"],
    ["Identity Platform", "справжні користувачі замість одного ключа"],
  ];
  text(s, "Що заважає зараз", { x: M, y: 1.2, w: 4.4, h: 0.3, fontSize: 14, bold: true, color: C.accent5 });
  text(s, "Наступні кроки", { x: 5.1, y: 1.2, w: 4.4, h: 0.3, fontSize: 14, bold: true, color: C.accent3 });
  const col = (items, x, color) => items.forEach(([h, d], i) => {
    const y = 1.6 + i * 0.9;
    card(s, x, y, 4.4, 0.8);
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.15, y: y + 0.28, w: 0.22, h: 0.22, fill: { color }, line: { color } });
    text(s, h, { x: x + 0.5, y: y + 0.08, w: 3.8, h: 0.3, fontSize: 12, bold: true });
    text(s, d, { x: x + 0.5, y: y + 0.4, w: 3.8, h: 0.35, fontSize: 11, color: C.accent6 });
  });
  col(left, M, C.accent5);
  col(right, 5.1, C.accent3);
  s.addNotes("Головний висновок з перевірки: загальний OCR добре читає горизонтальний текст зблизька, а для складних випадків потрібна спеціалізована модель або попередній детектор таблички.");
}

// ================= 14. Висновки =================
pres.addSection({ title: "Висновки" });
{
  const s = slide("DARK", "Висновки");
  s.addText("Висновки", { x: M, y: 0.4, w: 4, h: 0.5, isTextBox: true, fontSize: 28, bold: true, color: C.background1, fontFace: THEME.headFontFace, margin: 0 });
  bullets(s, [
    "Cloud Vision API дає готовий OCR без навчання моделі: один REST-запит, відповідь зі словами й координатами",
    "Serverless-зв'язка Cloud Run + Firestore + Cloud Storage розгортається одним скриптом і масштабується до нуля",
    "Контрольна цифра ISO 6346 перетворює «якийсь текст» на перевірений номер і дозволяє безпечно виправляти помилки OCR",
    "На крупних планах номер читається надійно; вертикальні написи й дрібний текст потребують спеціалізованої моделі",
    "Вартість PoC у межах безкоштовних лімітів: 1000 зображень Vision на місяць, 2 млн запитів Cloud Run",
  ], { x: M, y: 1.05, w: 9, h: 3.0, fontSize: 14, color: C.background1 });
  card(s, M, 4.2, 9, 0.95, THEME.colors.dk2);
  text(s, "Код і інструкція з розгортання", { x: 0.7, y: 4.3, w: 4, h: 0.3, fontSize: 11, color: C.accent2 });
  text(s, "github.com/altiebalti/container-ocr", { x: 0.7, y: 4.6, w: 5, h: 0.4, fontSize: 16, bold: true, color: C.background1, fontFace: "Courier New" });
  text(s, "42 тести pytest · deploy.sh / cleanup.sh · samples/real з атрибуцією", { x: 5.4, y: 4.45, w: 4, h: 0.6, fontSize: 11, color: C.accent2, align: "right", valign: "middle" });
  s.addNotes("Дякую за увагу. Запитання.");
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("written", OUT, "slides:", n);
})();
