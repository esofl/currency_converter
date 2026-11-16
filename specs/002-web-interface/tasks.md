# Tasks: Web Interface & SOLID Refactoring

**Spec**: `spec.md` | **Plan**: `plan.md`

## Phase 1: Core refactoring (branch `feat/web-interface`)
- [x] **T101** `src/ports.py`: `RateSource.fetch_rates(date) -> ExchangeRateSet`, `RateCache.save_rates/load_rates`.
- [x] **T102** `BNMClient`: enable TLS verification; map HTTP 404 to `NoDataError`; fallback window 7 days.
- [x] **T103** `InputValidator.validate_date(iso)`: format `YYYY-MM-DD`, real calendar date, not in the future.
- [x] **T104** `src/rate_service.py`: `RateService.get_rates(date)` (live → save cache; network error → cache with `offline=True`; nothing → `RatesUnavailableError`), holiday notice when returned date ≠ requested; `RateService.convert(amount_raw, from, to, date)`.

## Phase 2: Web UI (branch `feat/web-interface`)
- [x] **T201** `src/web.py`: `create_app(service)`; `GET /api/rates`, `POST /api/convert`; domain errors → 400/503 JSON with Russian messages.
- [x] **T202** `templates/index.html`: controls from FR-102, live validation, disabled button, banner for offline/notice, result line with date and source, swap.
- [x] **T203** `main.py`: composition root, open browser.
- [x] **T204** Delete `src/gui.py`.

## Phase 3: Tests (branch `test/web-and-e2e`)
- [x] **T301** Unit: `tests/test_rate_service.py` (fakes), `validate_date`, 404 → fallback.
- [x] **T302** E2E: `e2e/e2e_server.py` with `FakeRateSource` (switchable offline / holiday) + `e2e/converter.spec.js` covering US1–US4.

## Phase 4: Docs (branch `docs/web-report`)
- [x] **T401** README: run & test commands, architecture.
- [x] **T402** REPORT.md: section for iteration 2 — what changed, what the agent got wrong.
