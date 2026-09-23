"""Unit tests for BNM XML parsing and nominal handling."""

import unittest
from src.bnm_client import BNMClient
from src.exceptions import RateParsingError

SAMPLE_BNM_XML = """<?xml version="1.0" encoding="UTF-8"?>
<ValCurs Date="23.09.2026" name="Официальный курс">
  <Valute ID="47">
    <NumCode>978</NumCode>
    <CharCode>EUR</CharCode>
    <Nominal>1</Nominal>
    <Name>Евро</Name>
    <Value>20.1352</Value>
  </Valute>
  <Valute ID="44">
    <NumCode>840</NumCode>
    <CharCode>USD</CharCode>
    <Nominal>1</Nominal>
    <Name>Доллар США</Name>
    <Value>17.5585</Value>
  </Valute>
  <Valute ID="50">
    <NumCode>392</NumCode>
    <CharCode>JPY</CharCode>
    <Nominal>100</Nominal>
    <Name>Японская иена</Name>
    <Value>12.1500</Value>
  </Valute>
</ValCurs>"""


class TestBNMParser(unittest.TestCase):
    """Verifies parsing of BNM XML payloads."""

    def setUp(self):
        self.client = BNMClient()

    def test_parse_valid_xml_structure(self):
        rate_set = self.client.parse_xml(SAMPLE_BNM_XML)
        self.assertEqual(rate_set.date, "23.09.2026")
        self.assertIn("EUR", rate_set.valutes)
        self.assertIn("USD", rate_set.valutes)
        self.assertIn("JPY", rate_set.valutes)
        self.assertIn("MDL", rate_set.valutes)

    def test_base_currency_mdl_injected(self):
        rate_set = self.client.parse_xml(SAMPLE_BNM_XML)
        mdl = rate_set.get_valute("MDL")
        self.assertEqual(mdl.char_code, "MDL")
        self.assertEqual(mdl.nominal, 1)
        self.assertEqual(mdl.value, 1.0)
        self.assertEqual(mdl.unit_rate(), 1.0)

    def test_nominal_multiplier_calculation(self):
        rate_set = self.client.parse_xml(SAMPLE_BNM_XML)
        # JPY nominal is 100, value is 12.1500 MDL
        jpy = rate_set.get_valute("JPY")
        self.assertEqual(jpy.nominal, 100)
        self.assertAlmostEqual(jpy.unit_rate(), 0.1215, places=5)

    def test_parse_empty_xml_raises_error(self):
        with self.assertRaises(RateParsingError):
            self.client.parse_xml("")

    def test_parse_empty_valcurs_raises_error(self):
        empty_valcurs = '<ValCurs Date="23.09.2026" name="Курс"></ValCurs>'
        with self.assertRaises(RateParsingError):
            self.client.parse_xml(empty_valcurs)

    def test_parse_malformed_xml_raises_error(self):
        malformed = "<ValCurs><Valute><CharCode>EUR</Valute>"
        with self.assertRaises(RateParsingError):
            self.client.parse_xml(malformed)


if __name__ == "__main__":
    unittest.main()
