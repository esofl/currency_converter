# Feature Specification: Desktop Currency Converter

**Feature Branch**: `specs/001-currency-converter`  
**Created**: 2026-09-23  
**Status**: Approved  
**Author**: esofl  
**System Target**: Desktop GUI (Python Tkinter/ttk)  

---

## Executive Summary
A graphical desktop application that converts monetary amounts between international currencies and the Moldovan Leu (MDL), utilizing live XML exchange rate data provided by the National Bank of Moldova (BNM). The application guarantees high operational reliability through local caching, offline fallback, weekend/holiday fallback, and strict input validation.

---

## User Scenarios & Acceptance Testing

### User Story 1 - Direct and Cross-Currency Conversion (Priority: P1)
As a user, I want to select a source currency, enter an amount, select a target currency, and receive the calculated converted amount.

**Why this priority**: Core value proposition of the application.

**Acceptance Scenarios**:
1. **Given** valid loaded exchange rates, **When** user enters `100` EUR and selects USD as target currency, **Then** clicking "Convert" calculates and displays the USD amount according to official BNM rates with 2-4 decimal places.
2. **Given** any currency X, **When** user selects X as both source and target currency and enters `50`, **Then** the result displays `50.00 X` without network roundtrips.
3. **Given** the base currency MDL, **When** user converts between MDL and foreign currencies in either direction, **Then** rates scale appropriately with nominal calculations.

---

### User Story 2 - Input Validation and Dynamic Controls (Priority: P2)
As a user, I want the application to guide my input and prevent invalid calculations so I don't get erroneous financial data.

**Why this priority**: Prevents bad mathematical operations and user confusion.

**Acceptance Scenarios**:
1. **Given** an empty amount field or non-numeric text (`abc`, `-25`, `0`), **When** the field is evaluated, **Then** the "Convert" button remains disabled (or displays a clear validation error) and no calculation occurs.
2. **Given** a valid amount entered (`150.50` or `150,50`), **When** source and target currencies are selected, **Then** the "Convert" button becomes active.

---

### User Story 3 - Offline Resilience & Local Cache (Priority: P3)
As a user in an offline environment or experiencing network interruptions, I want to use previously cached exchange rates so I can continue working.

**Why this priority**: Meets critical reliability requirements of the specification.

**Acceptance Scenarios**:
1. **Given** no active internet connection and existing cached rates, **When** the application starts, **Then** it loads cached rates, displays an informational notice ("Offline mode: using cached rates"), and indicates the date of the cached rates.
2. **Given** a successful online fetch, **When** the app closes and reopens without network access, **Then** previous rates and date remain intact and functional.

---

### User Story 4 - Weekend & Holiday Rate Fallback (Priority: P4)
As a user checking rates on a weekend or public holiday when BNM does not publish new rates, I want the application to retrieve the most recent working-day rates automatically.

**Why this priority**: BNM publishes rates only on business days; weekends/holidays return empty or unchanged tables.

**Acceptance Scenarios**:
1. **Given** a requested date on a Sunday or official holiday, **When** BNM returns an empty rate list, **Then** the client steps back to the latest working day, retrieves valid rates, and informs the user of the effective date.

---

## Functional Requirements

- **FR-001 [GUI Form]**: The GUI must provide an amount input field, two dropdown selectors (source currency, target currency), a convert button, and an output display area.
- **FR-002 [Attribution & Date]**: The UI must display the data source ("Национальный Банк Молдовы / BNM") and the effective date of the exchange rates (`DD.MM.YYYY`).
- **FR-003 [Button State]**: The Convert button must remain disabled until a valid positive numeric amount is supplied and both currencies are selected.
- **FR-004 [Data Source Integration]**: The application must parse XML data from `https://www.bnm.md/ru/official_exchange_rates?get_xml=1&date=DD.MM.YYYY`.
- **FR-005 [Nominal Handling]**: The calculation engine must parse and respect the `<Nominal>` XML tag for currencies where nominal > 1 (e.g., JPY, RUB, HUF).
- **FR-006 [Input Sanitization]**: The system must accept both dot (`.`) and comma (`,`) as decimal separators, while rejecting zeroes, negative numbers, and alphanumeric strings.
- **FR-007 [Persistent Storage]**: Successful rate responses must be stored locally in JSON format (`cache/exchange_rates.json`) with date, timestamp, and rate map.
- **FR-008 [Crash Prevention]**: Network timeouts, HTTP errors, and malformed XML responses must be trapped without process termination, triggering UI error/warning dialogues.

---

## Edge Cases & Error Matrix

| Condition | System Reaction |
|-----------|-----------------|
| Amount is `0` or negative | Validation message shown; conversion blocked |
| Amount contains letters (`12a`) | Validation error: "Введите корректное положительное число" |
| Amount is empty | Convert button disabled; prompt displayed |
| Source == Target currency | Immediate identity output ($Amount \times 1$) |
| Network unavailable on launch | Prompt user, load from `cache/exchange_rates.json` |
| Network unavailable & no cache | Show critical error dialog asking user to connect to internet |
| Weekend / Empty XML response | Step back date by 1-3 days until working day rate found |
| Non-standard Nominal (e.g. 100 JPY) | Correctly calculate unit rate: $Rate = Value / Nominal$ |
