# Research: National Bank of Moldova (BNM) XML Feed & GUI Framework

## 1. BNM Data Feed Characteristics
- **URL Endpoint**: `https://www.bnm.md/ru/official_exchange_rates?get_xml=1&date=DD.MM.YYYY`
- **Protocol**: HTTPS GET
- **Format**: XML 1.0 (UTF-8)
- **Top Element**: `<ValCurs Date="23.09.2026" name="Официальный курс">`
- **Child Elements**:
  ```xml
  <Valute ID="47">
    <NumCode>978</NumCode>
    <CharCode>EUR</CharCode>
    <Nominal>1</Nominal>
    <Name>Евро</Name>
    <Value>20.1352</Value>
  </Valute>
  ```
- **Nominal Sensitivity**: Several currencies (e.g., JPY, HUF, RUB, AMD) use nominals such as 10, 100, or 1000. Unit calculation `value / nominal` is essential to prevent factor-of-100 mathematical errors.
- **Holidays & Weekends**: On non-banking days, the endpoint returns either empty XML (`<ValCurs Date="..."></ValCurs>`) or 0 valutes. The client must intelligently decrement the query date until active rates are discovered.

## 2. Desktop Framework Selection: Python Tkinter
- **Decision**: Tkinter (`ttk` modern themed widgets).
- **Rationale**:
  - Bundled natively with Python 3.11 on Windows — zero external compilation or binary wheels required.
  - Native Windows appearance and lightweight memory footprint (< 30 MB RAM).
  - Responsive event loop with simple `after` or thread synchronization.
