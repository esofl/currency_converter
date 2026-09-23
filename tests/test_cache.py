"""Unit tests for local cache persistence and recovery."""

import os
import tempfile
import unittest
from pathlib import Path

from src.models import Valute, ExchangeRateSet
from src.cache_manager import CacheManager
from src.exceptions import CacheError


class TestCacheManager(unittest.TestCase):
    """Verifies that cache survives restarts and handles corrupted files."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_file = Path(self.temp_dir.name) / "test_rates.json"
        self.manager = CacheManager(str(self.cache_file))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_load_cache(self):
        valutes = {
            "MDL": Valute("0", "498", "MDL", 1, "Молдавский лей", 1.0),
            "EUR": Valute("47", "978", "EUR", 1, "Евро", 20.1352),
        }
        original_set = ExchangeRateSet(
            date="23.09.2026",
            source_name="Национальный Банк Молдовы (BNM)",
            valutes=valutes,
        )

        self.assertFalse(self.manager.has_cache())
        self.manager.save_rates(original_set)

        self.assertTrue(self.manager.has_cache())
        loaded_set = self.manager.load_rates()

        self.assertIsNotNone(loaded_set)
        self.assertEqual(loaded_set.date, "23.09.2026")
        self.assertTrue(loaded_set.is_cached)
        self.assertIn("EUR", loaded_set.valutes)
        self.assertEqual(loaded_set.get_valute("EUR").value, 20.1352)

    def test_load_non_existent_cache_returns_none(self):
        self.assertIsNone(self.manager.load_rates())

    def test_load_corrupted_cache_raises_error(self):
        # Write corrupted JSON
        with open(self.cache_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json content ...")

        with self.assertRaises(CacheError):
            self.manager.load_rates()


if __name__ == "__main__":
    unittest.main()
