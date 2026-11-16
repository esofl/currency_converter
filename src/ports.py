"""Abstractions the application service depends on (DIP, ISP)."""

from typing import Optional, Protocol

from src.models import ExchangeRateSet


class RateSource(Protocol):
    def fetch_rates(self, target_date: Optional[str] = None) -> ExchangeRateSet:
        """Rates for DD.MM.YYYY (or today). Raises NetworkError / RateParsingError."""


class RateCache(Protocol):
    def save_rates(self, rate_set: ExchangeRateSet) -> None: ...
    def load_rates(self) -> Optional[ExchangeRateSet]: ...
