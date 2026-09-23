"""Unit tests for currency conversion calculations in both directions."""

import unittest
from src.models import Valute, ExchangeRateSet
from src.converter import ConverterService
from src.exceptions import ValidationError


class TestConverterService(unittest.TestCase):
    """Verifies precision of conversion engine across all currency pairs."""

    def setUp(self):
        valutes = {
            "MDL": Valute("0", "498", "MDL", 1, "Молдавский лей", 1.0),
            "EUR": Valute("47", "978", "EUR", 1, "Евро", 20.0000),
            "USD": Valute("44", "840", "USD", 1, "Доллар США", 10.0000),
            "JPY": Valute("50", "392", "JPY", 100, "Японская иена", 10.0000),  # 1 JPY = 0.10 MDL
        }
        self.rate_set = ExchangeRateSet(date="23.09.2026", source_name="BNM", valutes=valutes)

    def test_identity_conversion(self):
        """Converting a currency to itself returns identical value."""
        res_eur = ConverterService.convert(150.0, "EUR", "EUR", self.rate_set)
        self.assertEqual(res_eur, 150.0)

        res_mdl = ConverterService.convert(250.75, "MDL", "MDL", self.rate_set)
        self.assertEqual(res_mdl, 250.75)

    def test_direct_conversion_to_mdl(self):
        """Converting foreign currency to base MDL."""
        # 10 EUR * 20.0000 = 200.0 MDL
        res = ConverterService.convert(10.0, "EUR", "MDL", self.rate_set)
        self.assertEqual(res, 200.0)

    def test_reverse_conversion_from_mdl(self):
        """Converting base MDL to foreign currency."""
        # 200 MDL / 20.0000 = 10.0 EUR
        res = ConverterService.convert(200.0, "MDL", "EUR", self.rate_set)
        self.assertEqual(res, 10.0)

    def test_cross_currency_conversion(self):
        """Converting between two foreign currencies (EUR -> USD and USD -> EUR)."""
        # 10 EUR = 200 MDL. 200 MDL / 10 (USD rate) = 20 USD.
        res_to_usd = ConverterService.convert(10.0, "EUR", "USD", self.rate_set)
        self.assertEqual(res_to_usd, 20.0)

        # Reverse: 20 USD = 200 MDL. 200 MDL / 20 (EUR rate) = 10 EUR.
        res_to_eur = ConverterService.convert(20.0, "USD", "EUR", self.rate_set)
        self.assertEqual(res_to_eur, 10.0)

    def test_nominal_conversion(self):
        """Converting with currencies having nominal > 1 (e.g. JPY with nominal 100)."""
        # 1000 JPY: unit rate is 10.0 / 100 = 0.10 MDL. 1000 JPY = 100 MDL.
        # In USD (unit rate 10.0): 100 MDL / 10.0 = 10 USD.
        res_usd = ConverterService.convert(1000.0, "JPY", "USD", self.rate_set)
        self.assertEqual(res_usd, 10.0)

    def test_zero_or_negative_amount_raises_error(self):
        with self.assertRaises(ValidationError):
            ConverterService.convert(0.0, "EUR", "MDL", self.rate_set)

        with self.assertRaises(ValidationError):
            ConverterService.convert(-50.0, "EUR", "MDL", self.rate_set)

    def test_cross_rate_calculation(self):
        # 1 EUR (20 MDL) / 1 USD (10 MDL) = 2.0
        rate = ConverterService.get_cross_rate("EUR", "USD", self.rate_set)
        self.assertEqual(rate, 2.0)


if __name__ == "__main__":
    unittest.main()
