# Feature Specification: Web Interface & SOLID Refactoring

**Feature Branch**: `specs/002-web-interface`
**Created**: 2026-11-16
**Status**: Approved
**Supersedes**: UI section of `001-currency-converter` (Tkinter desktop window → browser UI)
**Constitution**: v1.1.0

---

## Summary
Replace the Tkinter desktop window with a locally served web interface, move all orchestration logic out of the UI into a testable application service built on SOLID principles, and cover user-visible behaviour with Playwright end-to-end tests. Domain rules from `001` (BNM source, nominal-aware conversion, validation, cache, holiday fallback) remain unchanged.

---

## User Scenarios & Acceptance

### US1 — Convert in the browser (P1)
1. **Given** rates are loaded, **When** the user enters `100`, selects `EUR` → `USD` and clicks «Конвертировать», **Then** the result `X USD` is shown together with the rate date and the source «Национальный Банк Молдовы (BNM)».
2. **Given** a result for `EUR → USD`, **When** the user clicks «⇄» (swap) and converts the shown amount back, **Then** the original amount is returned (±0.01).
3. **Given** the same currency on both sides, **When** the user converts `50`, **Then** `50 X` is shown without an error.

### US2 — Validation (P1)
1. **Given** the amount field is empty, `abc`, `-25` or `0`, **Then** the convert button is disabled and an inline message explains why.
2. **Given** `150,50` or `150.50`, **Then** the button becomes active.
3. **Given** a date in the future, **Then** an error is shown and no request to BNM is made.
4. The server re-validates every request; the browser is not trusted.

### US3 — Offline (P1)
1. **Given** the network is unavailable and a cache exists, **Then** the page shows a banner «Нет связи с BNM. Используется сохранённый курс от DD.MM.YYYY» and conversion works with cached rates.
2. **Given** the network is unavailable and no cache exists, **Then** a clear error is shown, the page does not crash, the convert button stays disabled.
3. The cache survives a restart of the application.

### US4 — Weekends & holidays (P2)
1. **Given** the user selects a date for which BNM returns an empty list or HTTP 404, **Then** the service steps back day by day (up to 7 days) and shows «Курс на DD.MM.YYYY не опубликован, показан последний доступный курс от DD.MM.YYYY».

---

## Functional Requirements
- **FR-101** Web page served at `http://127.0.0.1:5000`, opened automatically on start.
- **FR-102** Controls: amount input, source currency select, target currency select, swap button, rate date input (default = today), convert button, result area, rate date + source line, status banner.
- **FR-103** Convert button disabled until amount is valid and both currencies are selected.
- **FR-104** JSON API: `GET /api/rates?date=YYYY-MM-DD`, `POST /api/convert`.
- **FR-105** `RateService` owns the fetch → cache → fallback flow; the HTTP layer contains no business rules.
- **FR-106** TLS verification enabled for BNM requests.
- **FR-107** Unit tests: XML parsing, conversion in both directions, empty/invalid source response, input validation, service fallback logic. Single command: `python -m pytest`.
- **FR-108** E2E tests (Playwright): all scenarios US1–US4 with a fake rate source. Single command: `npx playwright test`.

## Out of Scope
Historical charts (Lab 4), user accounts, deployment to a public server.
