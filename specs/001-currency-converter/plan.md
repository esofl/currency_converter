# Implementation Plan: Desktop Currency Converter

**Branch**: `specs/001-currency-converter`  
**Date**: 2026-09-23  
**Spec Link**: [spec.md](./spec.md)  
**Status**: Approved  

---

## 1. Architecture Overview
The application is structured following a modular layered architecture with clear separation of concerns:

```
[ Desktop GUI Layer (tkinter/ttk) ]
               │
               ▼
[ Business Logic & Service Layer ]
  - InputValidator
  - ConverterService
               │
               ▼
[ Data Access & Persistence Layer ]
  - BNMClient (urllib + xml.etree)
  - CacheManager (JSON storage)
  - ExchangeRateSet / Valute Models
```

---

## 2. Technical Stack & Context
- **Language**: Python 3.11.9
- **GUI Toolkit**: Tkinter & `ttk` (native desktop windows, themed widgets)
- **Data Source**: National Bank of Moldova (BNM) XML endpoint (`https://www.bnm.md/ru/official_exchange_rates?get_xml=1&date=DD.MM.YYYY`)
- **HTTP Transport**: Python `urllib.request` with SSL context configuration and 10s request timeout
- **Persistence**: File-based JSON caching at `cache/exchange_rates.json`
- **Testing Framework**: Python `unittest` framework (no external dependencies required)
- **Execution Command**: Single-command test runner (`python -m unittest discover tests`)

---

## 3. Component Specifications

### 3.1 Domain Models (`src/models.py`)
- `Valute`: Dataclass holding `id: str`, `num_code: str`, `char_code: str`, `nominal: int`, `name: str`, `value: float`. Provides helper method `unit_rate() -> float` which computes `value / nominal`.
- `ExchangeRateSet`: Dataclass holding `date: str`, `source_name: str`, `valutes: dict[str, Valute]`, `is_cached: bool`.

### 3.2 Network & Parsing Layer (`src/bnm_client.py`)
- Responsible for querying BNM endpoint with specified `date`.
- Traps network failures (`urllib.error.URLError`, socket timeout).
- Parses `<ValCurs>` and child `<Valute>` tags.
- Injects native base currency `MDL` (nominal=1, value=1.0) into the rate dictionary.
- Implements fallback stepping back up to 5 days if BNM returns empty rates on weekends or public holidays.

### 3.3 Cache Manager (`src/cache_manager.py`)
- Reads and writes to `cache/exchange_rates.json`.
- Safely handles directory creation, JSON encoding/decoding, and corrupted cache files.

### 3.4 Business Logic (`src/converter.py` & `src/validator.py`)
- `InputValidator.validate_amount(raw_input: str) -> float`: Replaces comma with period, verifies positive float $> 0$. Raises `ValidationError` otherwise.
- `ConverterService.convert(amount: float, from_code: str, to_code: str, rate_set: ExchangeRateSet) -> float`:
  - If `from_code == to_code`: returns `amount`.
  - Base conversion formula: $\text{MDL} = \text{amount} \times \text{from\_unit\_rate}$.
  - Target conversion formula: $\text{result} = \text{MDL} / \text{to\_unit\_rate}$.

### 3.5 Presentation Layer (`src/gui.py`)
- Built with `ttk.Frame`, `ttk.Entry`, `ttk.Combobox`, `ttk.Button`, `ttk.Label`.
- Dynamic button state: `Convert` button stays disabled (`state="disabled"`) until valid amount string is entered.
- Real-time rate loading using background threading (`threading.Thread`) so UI doesn't freeze on network latency.
- Status bar at bottom displays data source, rate date, and offline/online indicator.

---

## 4. Verification & Testing Strategy
- Automated unit test suite under `tests/`:
  - `test_parser.py`: Verifies XML parsing with mock XML, checks nominals and MDL base.
  - `test_converter.py`: Tests direct conversion, reverse conversion, cross-rate, and identical currencies.
  - `test_validator.py`: Tests edge inputs: empty, negatives, zeroes, commas, spaces, characters.
  - `test_cache.py`: Tests cache write, read, recovery from corrupted JSON.
  - `test_network_fallback.py`: Tests weekend empty response fallback.
