# Cross-Artifact Consistency Check: 002-web-interface

| Requirement | Spec | Plan | Tasks | Status |
| :--- | :--- | :--- | :--- | :--- |
| Graphical web UI (non-console) | FR-101, FR-102 | Architecture | T201–T203 | MATCH |
| Button disabled until valid | FR-103, US2 | index.html | T202 | MATCH |
| Conversion both directions | US1.2 | ConverterService | T104, T302 | MATCH |
| Rate date + source shown | US1.1 | RatesResult | T202 | MATCH |
| Offline with cache / without cache | US3 | RateService | T104, T301, T302 | MATCH |
| Cache survives restart | US3.3 | CacheManager | existing `test_cache.py`, T301 | MATCH |
| Holiday / 404 fallback with notice | US4 | NoDataError, 7 days | T102, T104 | MATCH |
| Invalid input incl. future date | US2 | InputValidator | T103 | MATCH |
| SOLID | Constitution VI | ports.py, composition root | T101, T104, T203 | MATCH |
| Playwright | Constitution VII, FR-108 | e2e server with fake | T302 | MATCH |
| TLS verification | FR-106 | Removed CERT_NONE | T102 | MATCH |

No conflicts with `001-currency-converter` domain rules. Ready for implementation.
