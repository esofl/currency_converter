# Currency Converter Constitution

## Core Principles

### I. Spec-Driven Integrity
Every feature and architectural behavior originates from an unambiguous markdown specification. No implementation code may be produced without prior specification, technical planning, and task breakdown.

### II. Offline-First & Resilient Operation
The application must maintain full operational capability during network disconnection, official holidays, weekends, or API degradation. 
- Network exceptions must be caught cleanly and presented gracefully to the user.
- The latest successful exchange rates must be persistently cached and restored upon restart.
- If data is unavailable for a given non-working date, the system falls back to the most recent available rates with explicit UI indication.

### III. Strict Validation & User Feedback
User input must be strictly validated before any financial calculation:
- Amounts must be positive decimal numbers greater than zero.
- Empty strings, alphabetic characters, negative numbers, and zeroes must trigger friendly UI validation messages.
- The primary action button (Convert) must remain inactive until valid inputs are provided.

### IV. Mathematical Precision & Nominal Awareness
Financial calculations must strictly account for currency nominals (e.g., 100 JPY or 10 RUB) and base currency relationships (MDL as base currency):
- $\text{Amount}_{\text{MDL}} = \text{Amount}_{\text{From}} \times \left(\frac{\text{Value}_{\text{From}}}{\text{Nominal}_{\text{From}}}\right)$
- $\text{Amount}_{\text{To}} = \frac{\text{Amount}_{\text{MDL}}}{\left(\frac{\text{Value}_{\text{To}}}{\text{Nominal}_{\text{To}}}\right)}$
- Conversion between identical currencies must yield the identical amount without precision loss or network calls.

### V. Test-First & Automated Verification
All core domain models, XML parsing logic, edge cases (empty responses, holidays, missing nodes), conversion calculations, and validators must be thoroughly covered by unit tests executable via a single standard CLI command.

## Architecture & Technology Constraints
- **Platform**: Desktop Application (GUI). Console-only applications are strictly prohibited by specification.
- **Language & Runtime**: Python 3.11+.
- **GUI Toolkit**: `tkinter` / `ttk` (standard library, zero heavy external binary dependencies).
- **Data Source**: Official National Bank of Moldova (BNM) XML feed (`https://www.bnm.md/ru/official_exchange_rates?get_xml=1&date=DD.MM.YYYY`).
- **Cache Format**: Local JSON storage (`cache/exchange_rates.json`) with timestamp and source metadata.

## Governance
- This constitution governs all implementation artifacts and pull requests.
- All development must proceed through dedicated Git branches with Pull Request merging into `main`.

**Version**: 1.0.0 | **Ratified**: 2026-09-23 | **Author**: esofl
