"""
Application service (SRP: orchestration only).
Fetch → cache → offline/holiday fallback → conversion. Depends on RateSource/RateCache
protocols (DIP), so the UI and tests can plug any implementation.
"""

import logging
from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.converter import ConverterService
from src.exceptions import CacheError, NetworkError, RateParsingError, RatesUnavailableError
from src.models import ExchangeRateSet
from src.ports import RateCache, RateSource
from src.validator import InputValidator

logger = logging.getLogger(__name__)


@dataclass
class RatesResult:
    rate_set: ExchangeRateSet
    offline: bool = False
    notice: Optional[str] = None


@dataclass
class ConversionResult:
    amount: float
    from_code: str
    to_code: str
    result: float
    rate: float
    rates: RatesResult


class RateService:
    def __init__(self, source: RateSource, cache: RateCache) -> None:
        self._source = source
        self._cache = cache

    def get_rates(self, requested: date) -> RatesResult:
        req = requested.strftime("%d.%m.%Y")
        try:
            rate_set = self._source.fetch_rates(req)
        except (NetworkError, RateParsingError) as e:
            logger.warning("Live rates unavailable: %s", e)
            return self._from_cache(e)

        try:
            self._cache.save_rates(rate_set)
        except CacheError as e:  # cache is best-effort; live data is still valid
            logger.error("Cache write failed: %s", e)

        notice = None
        if rate_set.date and rate_set.date != req:
            notice = f"Курс на {req} не опубликован, показан последний доступный курс от {rate_set.date}."
        return RatesResult(rate_set, offline=False, notice=notice)

    def _from_cache(self, error: Exception) -> RatesResult:
        try:
            cached = self._cache.load_rates()
        except CacheError as e:
            logger.error("Cache read failed: %s", e)
            cached = None
        reason = "Нет связи с BNM" if isinstance(error, NetworkError) else "BNM вернул некорректные данные"
        if cached is None:
            raise RatesUnavailableError(f"{reason}, а сохранённого курса нет. Проверьте подключение и попробуйте ещё раз.")
        return RatesResult(cached, offline=True,
                           notice=f"{reason}. Используется сохранённый курс от {cached.date}.")

    def convert(self, amount_raw: str, from_code: str, to_code: str, date_raw: str) -> ConversionResult:
        amount = InputValidator.validate_amount(amount_raw)
        rates = self.get_rates(InputValidator.validate_date(date_raw))
        rs = rates.rate_set
        result = ConverterService.convert(amount, from_code, to_code, rs)
        rate = ConverterService.get_cross_rate(from_code, to_code, rs)
        return ConversionResult(amount, from_code.upper(), to_code.upper(), result, rate, rates)
