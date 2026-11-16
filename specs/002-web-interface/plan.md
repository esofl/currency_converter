# Implementation Plan: Web Interface & SOLID Refactoring

**Spec**: `specs/002-web-interface/spec.md` | **Constitution**: v1.1.0

## Architecture

```
Browser (templates/index.html, vanilla JS)
        │  fetch JSON
        ▼
src/web.py        create_app(service)          — HTTP only (SRP)
        │
        ▼
src/rate_service.py  RateService               — orchestration: fetch → cache → fallback, convert
        │ depends on protocols (DIP)
        ├── src/ports.py  RateSource, RateCache (ISP: 1–2 methods each)
        │
        ├── src/bnm_client.py   BNMClient  implements RateSource
        ├── src/cache_manager.py CacheManager implements RateCache
        ├── src/converter.py    ConverterService (pure math)
        └── src/validator.py    InputValidator (amount + date)

main.py — composition root: wires BNMClient + CacheManager into RateService, starts Flask.
```

## Key Decisions
| Decision | Rationale |
| :--- | :--- |
| Flask + vanilla JS | Pure Python, no native DLLs (blocked by Smart App Control); no front-end build step. |
| `RateService` returns `RatesResult(rate_set, notice, offline)` | UI only renders; all messages are produced in one testable place. |
| HTTP 404 from BNM → `NoDataError` (subclass of `RateParsingError`) | BNM answers 404 for dates without publication; fallback must step back instead of reporting "no network". |
| Fallback window 7 days | Covers long holiday weekends. |
| Playwright tests use `e2e/e2e_server.py` with `FakeRateSource` | Deterministic rates and switchable offline mode without touching the real BNM (LSP in practice). |

## Removed
- `src/gui.py` (Tkinter) — replaced by `src/web.py` + `templates/index.html`.
- Hard-coded fetch date `23.09.2026` in the old GUI worker — the date now comes from the user (default today).
- `ssl.CERT_NONE` in `BNMClient` — verification enabled (FR-106).
