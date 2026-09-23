"""Cache manager for storing and loading exchange rates locally."""

import json
import os
from pathlib import Path
from typing import Optional

from src.models import ExchangeRateSet
from src.exceptions import CacheError


class CacheManager:
    """Manages persistent disk caching of exchange rate data."""

    def __init__(self, cache_file_path: Optional[str] = None):
        if cache_file_path:
            self.cache_file = Path(cache_file_path)
        else:
            base_dir = Path(__file__).resolve().parent.parent
            self.cache_file = base_dir / "cache" / "exchange_rates.json"

    def has_cache(self) -> bool:
        """Checks if a readable cache file currently exists."""
        return self.cache_file.exists() and self.cache_file.stat().st_size > 0

    def save_rates(self, rate_set: ExchangeRateSet) -> None:
        """Persists the exchange rate set into local JSON storage."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(rate_set.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise CacheError(f"Failed to write cache to '{self.cache_file}': {e}") from e

    def load_rates(self) -> Optional[ExchangeRateSet]:
        """Loads and reconstructs ExchangeRateSet from local JSON storage."""
        if not self.has_cache():
            return None

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ExchangeRateSet.from_dict(data)
        except Exception as e:
            # Corrupted or unreadable cache file
            raise CacheError(f"Failed to parse cache from '{self.cache_file}': {e}") from e
