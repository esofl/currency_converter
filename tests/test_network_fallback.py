"""Unit tests for network error handling and holiday fallback."""

import unittest
from unittest.mock import patch, MagicMock
import urllib.error

from src.bnm_client import BNMClient
from src.exceptions import NetworkError, RateParsingError

EMPTY_XML = '<ValCurs Date="20.09.2026" name="Курс"></ValCurs>'
VALID_XML = """<?xml version="1.0" encoding="UTF-8"?>
<ValCurs Date="18.09.2026" name="Официальный курс">
  <Valute ID="47">
    <NumCode>978</NumCode>
    <CharCode>EUR</CharCode>
    <Nominal>1</Nominal>
    <Name>Евро</Name>
    <Value>20.1200</Value>
  </Valute>
</ValCurs>"""


class TestNetworkAndFallback(unittest.TestCase):
    """Verifies that network degradation and non-working days are handled cleanly."""

    def setUp(self):
        self.client = BNMClient()

    @patch("urllib.request.urlopen")
    def test_network_connection_error_raises_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
        with self.assertRaises(NetworkError):
            self.client.fetch_raw_xml("23.09.2026")

    @patch("urllib.request.urlopen")
    def test_http_500_status_raises_network_error(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_urlopen.return_value.__enter__.return_value = mock_resp
        with self.assertRaises(NetworkError):
            self.client.fetch_raw_xml("23.09.2026")

    @patch.object(BNMClient, "fetch_raw_xml")
    def test_weekend_fallback_to_previous_working_day(self, mock_fetch):
        """Simulates requesting Sunday (empty) which falls back to Friday (valid)."""
        # First call (Sunday 20.09): returns empty XML
        # Second call (Saturday 19.09): returns empty XML
        # Third call (Friday 18.09): returns valid XML
        mock_fetch.side_effect = [EMPTY_XML, EMPTY_XML, VALID_XML]

        result = self.client.fetch_rates(target_date="20.09.2026", max_fallback_days=3)
        self.assertEqual(result.date, "18.09.2026")
        self.assertIn("EUR", result.valutes)
        self.assertEqual(mock_fetch.call_count, 3)


if __name__ == "__main__":
    unittest.main()
