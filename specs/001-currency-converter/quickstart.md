# Quickstart Guide: Desktop Currency Converter

## Requirements
- Python 3.11+
- Internet access for initial live rate fetching (offline cache supported for subsequent launches)

## Launching Application
```powershell
python main.py
```

## Running Automated Unit Tests
Single command test suite execution:
```powershell
python -m unittest discover tests
```

## Usage Workflow
1. Launch `main.py`. The app will automatically connect to BNM and fetch the latest rates.
2. Enter a monetary amount (e.g. `100.50` or `100,50`).
3. Select Source Currency (e.g., `EUR`).
4. Select Target Currency (e.g., `USD` or `MDL`).
5. Notice the **Конвертировать** button enables automatically once input is valid.
6. Click **Конвертировать** (or press Enter) to receive the converted sum.
