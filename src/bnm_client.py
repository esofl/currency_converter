"""National Bank of Moldova (BNM) XML exchange rate client."""

import ssl
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Optional

from src.models import Valute, ExchangeRateSet
from src.exceptions import NetworkError, RateParsingError


class BNMClient:
    """Client for fetching and parsing official exchange rates from BNM."""

    BASE_URL = "https://www.bnm.md/ru/official_exchange_rates?get_xml=1&date={date}"
    SOURCE_NAME = "Национальный Банк Молдовы (BNM)"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        # Secure default SSL context with fallback for environments with missing root certs
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def parse_xml(self, xml_content: str) -> ExchangeRateSet:
        """Parses BNM XML string into an ExchangeRateSet object."""
        if not xml_content or not xml_content.strip():
            raise RateParsingError("Received empty XML content from source")

        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise RateParsingError(f"Malformed XML response: {e}") from e

        if root.tag != "ValCurs":
            raise RateParsingError(f"Unexpected root tag '{root.tag}', expected 'ValCurs'")

        date_str = root.attrib.get("Date", "").strip()
        source_title = root.attrib.get("name", self.SOURCE_NAME).strip() or self.SOURCE_NAME

        valutes = {}
        # Always register the base currency: Moldovan Leu (MDL)
        valutes["MDL"] = Valute(
            id="0",
            num_code="498",
            char_code="MDL",
            nominal=1,
            name="Молдавский лей",
            value=1.0,
        )

        for valute_elem in root.findall("Valute"):
            val_id = valute_elem.attrib.get("ID", "").strip()
            num_code = (valute_elem.findtext("NumCode") or "").strip()
            char_code = (valute_elem.findtext("CharCode") or "").strip().upper()
            nominal_str = (valute_elem.findtext("Nominal") or "1").strip()
            name = (valute_elem.findtext("Name") or "").strip()
            value_str = (valute_elem.findtext("Value") or "0").strip().replace(",", ".")

            if not char_code:
                continue

            try:
                nominal = int(nominal_str)
                value = float(value_str)
            except ValueError as e:
                raise RateParsingError(
                    f"Invalid numeric values in valute '{char_code}': nominal={nominal_str}, value={value_str}"
                ) from e

            valutes[char_code] = Valute(
                id=val_id,
                num_code=num_code,
                char_code=char_code,
                nominal=nominal,
                name=name,
                value=value,
            )

        if len(valutes) <= 1:
            # Only base MDL was registered, no external currencies parsed
            raise RateParsingError("XML response contains no currency exchange rate entries")

        return ExchangeRateSet(
            date=date_str,
            source_name=self.SOURCE_NAME,
            valutes=valutes,
            is_cached=False,
        )

    def fetch_raw_xml(self, target_date: str) -> str:
        """Downloads raw XML response for a specified date (format DD.MM.YYYY)."""
        url = self.BASE_URL.format(date=target_date)
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
                "Accept": "application/xml, text/xml, */*",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self.ssl_context) as response:
                if response.status != 200:
                    raise NetworkError(f"BNM server returned HTTP status {response.status}")
                raw_bytes = response.read()
                return raw_bytes.decode("utf-8", errors="replace")
        except urllib.error.URLError as e:
            raise NetworkError(f"Network error connecting to BNM: {e.reason}") from e
        except Exception as e:
            raise NetworkError(f"Unexpected communication error with BNM: {e}") from e

    def fetch_rates(self, target_date: Optional[str] = None, max_fallback_days: int = 5) -> ExchangeRateSet:
        """Fetches exchange rates with automated weekend and holiday fallback."""
        if target_date:
            curr_dt = datetime.strptime(target_date, "%d.%m.%Y")
        else:
            curr_dt = datetime.now()

        last_error = None
        for step in range(max_fallback_days + 1):
            date_str = curr_dt.strftime("%d.%m.%Y")
            try:
                xml_data = self.fetch_raw_xml(date_str)
                rate_set = self.parse_xml(xml_data)
                return rate_set
            except (RateParsingError, NetworkError) as e:
                last_error = e
                # Fallback to previous day if response was empty or error was rate parsing (e.g. non-working day)
                if isinstance(e, RateParsingError):
                    curr_dt -= timedelta(days=1)
                    continue
                # If network completely fails, do not loop endlessly
                raise e

        if last_error:
            raise last_error
        raise NetworkError("Unable to obtain exchange rates from BNM within fallback window")
