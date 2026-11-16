// E2E: user stories US1–US4 из specs/002-web-interface/spec.md.
// Курсы фейковые: EUR = 20 MDL, USD = 16 MDL, 100 JPY = 12 MDL.
const { test, expect } = require("@playwright/test");

const URL = "http://127.0.0.1:5201/";
const mode = (request, m) => request.post(URL + "__e2e__/mode/" + m);

test.beforeEach(async ({ request }) => {
  await request.post(URL + "__e2e__/reset");
});

async function open(page) {
  await page.goto(URL);
  await expect(page.locator("#from option")).not.toHaveCount(0);
}

async function convert(page, amount, from, to) {
  await page.fill("#amount", amount);
  await page.selectOption("#from", from);
  await page.selectOption("#to", to);
  await page.click("#convert");
}

test("US1: EUR → USD, дата курса и источник", async ({ page }) => {
  await open(page);
  await convert(page, "100", "EUR", "USD");
  await expect(page.locator("#result")).toHaveText("100 EUR = 125 USD");
  await expect(page.locator("#meta")).toContainText("Курс от");
  await expect(page.locator("#meta")).toContainText("Национальный Банк Молдовы (BNM)");
});

test("US1: обратное направление через ⇄ возвращает исходную сумму", async ({ page }) => {
  await open(page);
  await convert(page, "100", "EUR", "USD");
  await page.click("#swap");
  await expect(page.locator("#from")).toHaveValue("USD");
  await page.fill("#amount", "125");
  await page.click("#convert");
  await expect(page.locator("#result")).toHaveText("125 USD = 100 EUR");
});

test("US1: номинал (100 JPY) и одинаковые валюты", async ({ page }) => {
  await open(page);
  await convert(page, "1000", "JPY", "MDL");
  await expect(page.locator("#result")).toHaveText("1000 JPY = 120 MDL");
  await convert(page, "50", "EUR", "EUR");
  await expect(page.locator("#result")).toHaveText("50 EUR = 50 EUR");
});

test("US2: некорректный ввод блокирует кнопку и объясняет причину", async ({ page }) => {
  await open(page);
  const btn = page.locator("#convert");
  await expect(btn).toBeDisabled(); // пустое поле
  for (const [value, msg] of [["abc", "только цифры"], ["-25", "только цифры"], ["0", "больше нуля"]]) {
    await page.fill("#amount", value);
    await expect(btn).toBeDisabled();
    await expect(page.locator("#amount-error")).toContainText(msg);
  }
  await page.fill("#amount", "150,50");
  await expect(btn).toBeEnabled();
  await expect(page.locator("#amount-error")).toHaveText("");
});

test("US2: сервер сам отвергает некорректную сумму", async ({ request }) => {
  const r = await request.post(URL + "api/convert", { data: { amount: "-5", from: "EUR", to: "USD", date: "2026-01-05" } });
  expect(r.status()).toBe(400);
  expect((await r.json()).error).toContain("больше нуля");
});

test("US2: будущая дата не отправляется", async ({ page, request }) => {
  await open(page);
  const r = await request.get(URL + "api/rates?date=2999-01-01");
  expect(r.status()).toBe(400);
  expect((await r.json()).error).toContain("будущую");
});

test("US3: без сети, с кэшем — баннер с датой и конвертация работает", async ({ page, request }) => {
  await open(page); // онлайн-загрузка заполнила кэш
  await mode(request, "offline");
  await page.reload();
  await expect(page.locator("#banner")).toContainText("Нет связи с BNM");
  await expect(page.locator("#banner")).toContainText("сохранённый курс от");
  await convert(page, "100", "EUR", "MDL");
  await expect(page.locator("#result")).toHaveText("100 EUR = 2000 MDL");
  await expect(page.locator("#meta")).toContainText("сохранённые данные");
});

test("US3: без сети и без кэша — понятная ошибка, кнопка неактивна", async ({ page, request }) => {
  await mode(request, "offline");
  const errors = [];
  page.on("pageerror", (e) => errors.push(e));
  await page.goto(URL);
  await expect(page.locator("#banner")).toContainText("сохранённого курса нет");
  await page.fill("#amount", "100");
  await expect(page.locator("#convert")).toBeDisabled();
  expect(errors).toEqual([]);
});

test("US4: выходной/праздник — берётся последний курс с пояснением", async ({ page, request }) => {
  await mode(request, "holiday");
  await open(page);
  await expect(page.locator("#banner")).toContainText("не опубликован");
  await expect(page.locator("#banner")).toContainText("последний доступный курс");
});
