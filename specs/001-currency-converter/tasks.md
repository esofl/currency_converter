# Tasks: Desktop Currency Converter Implementation

**Input**: [spec.md](./spec.md), [plan.md](./plan.md), [data-model.md](./data-model.md)  
**Status**: Ready for Implementation  

---

## Phase 1: Setup & Domain Models
- [x] **TASK-001**: Define custom exceptions in `src/exceptions.py` (`NetworkError`, `RateParsingError`, `ValidationError`, `CacheError`).
- [x] **TASK-002**: Implement `Valute` and `ExchangeRateSet` dataclasses in `src/models.py` with `unit_rate()` calculating `value / nominal`.

## Phase 2: Data & Persistence Layer
- [x] **TASK-003**: Implement `CacheManager` in `src/cache_manager.py` with JSON serialization/deserialization into `cache/exchange_rates.json`.
- [x] **TASK-004**: Implement `BNMClient` in `src/bnm_client.py` using `urllib.request` and `xml.etree.ElementTree`:
  - Fetch XML from `https://www.bnm.md/ru/official_exchange_rates?get_xml=1&date=DD.MM.YYYY`.
  - Handle SSL, user-agent headers, and timeout.
  - Automatically insert base currency `MDL` (value=1.0, nominal=1).
  - Implement weekend/holiday fallback (decrementing date until valid rates found).

## Phase 3: Business Logic & Validation
- [x] **TASK-005**: Implement `InputValidator` in `src/validator.py`:
  - Clean input string (strip whitespace, comma to period).
  - Verify positive decimal number ($>0$).
  - Reject zeroes, negatives, letters, symbols.
- [x] **TASK-006**: Implement `ConverterService` in `src/converter.py`:
  - Handle identity conversion (same currency returns exact amount).
  - Convert source currency to MDL, then MDL to target currency.
  - Round to 4 decimal places (or 2 for major currency pairs).

## Phase 4: Desktop GUI (Tkinter/ttk)
- [x] **TASK-007**: Implement `CurrencyConverterApp` in `src/gui.py`:
  - Window layout: title, icon, amount entry, currency selectors (`ttk.Combobox`), Convert button, result card, status bar.
  - Real-time input validation listener disabling the Convert button until input is valid.
  - Background thread execution for rate updates to keep UI responsive.
  - Offline mode indicator and alert messages when network fails.
- [x] **TASK-008**: Implement application entry point `main.py`.

## Phase 5: Automated Unit Testing
- [ ] **TASK-009**: Implement `tests/test_parser.py` (XML parsing, nominals, MDL base).
- [ ] **TASK-010**: Implement `tests/test_converter.py` (cross-conversion, reverse conversion, identity).
- [ ] **TASK-011**: Implement `tests/test_validator.py` (negative numbers, zero, strings, commas).
- [ ] **TASK-012**: Implement `tests/test_cache.py` (JSON saving, loading, corruption recovery).
- [ ] **TASK-013**: Implement `tests/test_network_fallback.py` (weekend/holiday empty XML handling).

## Phase 6: Documentation & Reporting
- [ ] **TASK-014**: Create comprehensive `REPORT.md` answering all 5 laboratory questions and documenting agent adjustments.
- [ ] **TASK-015**: Polish root `README.md` with usage instructions, single-command test line, and GitHub styling.
