"""RateService on fakes (DIP), date validation and BNM 404 handling."""

import os
import tempfile
import unittest
import urllib.error
from datetime import date
from unittest.mock import patch

from src.bnm_client import BNMClient
from src.cache_manager import CacheManager
from src.exceptions import NetworkError, NoDataError, RateParsingError, RatesUnavailableError, ValidationError
from src.models import ExchangeRateSet, Valute
from src.rate_service import RateService
from src.validator import InputValidator


def rates(d="16.11.2026"):
    return ExchangeRateSet(d, "BNM", {
        "MDL": Valute("0", "498", "MDL", 1, "Лей", 1.0),
        "EUR": Valute("47", "978", "EUR", 1, "Евро", 20.0),
        "USD": Valute("44", "840", "USD", 1, "Доллар", 18.0),
        "JPY": Valute("1", "392", "JPY", 100, "Иена", 12.0),
    })


class FakeSource:
    def __init__(self, result=None, error=None):
        self.result, self.error, self.calls = result, error, []

    def fetch_rates(self, target_date=None):
        self.calls.append(target_date)
        if self.error:
            raise self.error
        return self.result


class MemoryCache:
    def __init__(self, stored=None):
        self.stored = stored

    def save_rates(self, rate_set):
        self.stored = rate_set

    def load_rates(self):
        return self.stored


D = date(2026, 11, 16)


class TestRateService(unittest.TestCase):
    def test_live_rates_are_cached(self):
        cache = MemoryCache()
        r = RateService(FakeSource(rates()), cache).get_rates(D)
        self.assertFalse(r.offline)
        self.assertIsNone(r.notice)
        self.assertIs(cache.stored, r.rate_set)

    def test_holiday_notice_when_date_differs(self):
        r = RateService(FakeSource(rates("13.11.2026")), MemoryCache()).get_rates(D)
        self.assertIn("16.11.2026", r.notice)
        self.assertIn("13.11.2026", r.notice)

    def test_offline_uses_cache_with_its_date(self):
        r = RateService(FakeSource(error=NetworkError("down")), MemoryCache(rates("10.11.2026"))).get_rates(D)
        self.assertTrue(r.offline)
        self.assertIn("Нет связи", r.notice)
        self.assertIn("10.11.2026", r.notice)

    def test_offline_without_cache_raises_clear_error(self):
        with self.assertRaises(RatesUnavailableError):
            RateService(FakeSource(error=NetworkError("down")), MemoryCache()).get_rates(D)

    def test_malformed_source_falls_back_to_cache(self):
        r = RateService(FakeSource(error=RateParsingError("bad xml")), MemoryCache(rates())).get_rates(D)
        self.assertTrue(r.offline)

    def test_convert_both_directions_and_nominal(self):
        s = RateService(FakeSource(rates()), MemoryCache())
        there = s.convert("100", "EUR", "USD", "2026-11-16").result
        back = s.convert(str(there), "USD", "EUR", "2026-11-16").result
        self.assertAlmostEqual(there, 111.1111, places=4)
        self.assertAlmostEqual(back, 100.0, places=3)
        self.assertAlmostEqual(s.convert("1000", "JPY", "MDL", "2026-11-16").result, 120.0)

    def test_convert_rejects_bad_amount_before_network(self):
        src = FakeSource(rates())
        for bad in ("", "abc", "-5", "0"):
            with self.assertRaises(ValidationError):
                RateService(src, MemoryCache()).convert(bad, "EUR", "USD", "2026-11-16")
        self.assertEqual(src.calls, [])

    def test_cache_survives_restart(self):
        path = os.path.join(tempfile.mkdtemp(), "rates.json")
        RateService(FakeSource(rates()), CacheManager(path)).get_rates(D)
        # «перезапуск»: новые объекты, сети нет
        r = RateService(FakeSource(error=NetworkError("down")), CacheManager(path)).get_rates(D)
        self.assertTrue(r.offline)
        self.assertEqual(r.rate_set.get_valute("EUR").value, 20.0)


class TestDateValidation(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(InputValidator.validate_date("2026-11-16", today=D), D)

    def test_invalid(self):
        for bad in ("", "16.11.2026", "2026-02-31", "abc"):
            with self.assertRaises(ValidationError):
                InputValidator.validate_date(bad, today=D)

    def test_future_rejected(self):
        with self.assertRaises(ValidationError):
            InputValidator.validate_date("2026-11-17", today=D)


class TestBnm404(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_404_is_no_data(self, urlopen):
        urlopen.side_effect = urllib.error.HTTPError("u", 404, "Not Found", {}, None)
        with self.assertRaises(NoDataError):
            BNMClient().fetch_raw_xml("25.11.2026")

    def test_tls_verification_enabled(self):
        import ssl
        ctx = BNMClient().ssl_context
        self.assertTrue(ctx.check_hostname)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)


if __name__ == "__main__":
    unittest.main()
