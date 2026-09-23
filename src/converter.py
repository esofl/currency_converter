"""Currency conversion calculation engine."""

from typing import Tuple
from src.models import ExchangeRateSet
from src.exceptions import ValidationError


class ConverterService:
    """Calculates exchange between currencies based on BNM rates."""

    @staticmethod
    def convert(
        amount: float,
        from_code: str,
        to_code: str,
        rate_set: ExchangeRateSet,
        round_digits: int = 4,
    ) -> float:
        """
        Converts an amount from one currency to another using MDL as the intermediate base.
        """
        if amount <= 0:
            raise ValidationError("Сумма для конвертации должна быть больше нуля.")

        from_clean = from_code.strip().upper()
        to_clean = to_code.strip().upper()

        if from_clean == to_clean:
            return round(amount, round_digits)

        from_valute = rate_set.get_valute(from_clean)
        to_valute = rate_set.get_valute(to_clean)

        from_unit = from_valute.unit_rate()
        to_unit = to_valute.unit_rate()

        if to_unit <= 0:
            raise ValidationError(f"Недопустимый нулевой курс для валюты {to_clean}")

        # Amount in Moldovan Lei (MDL)
        amount_in_mdl = amount * from_unit

        # Amount in Target Currency
        target_amount = amount_in_mdl / to_unit

        return round(target_amount, round_digits)

    @staticmethod
    def get_cross_rate(
        from_code: str,
        to_code: str,
        rate_set: ExchangeRateSet,
        round_digits: int = 6,
    ) -> float:
        """Computes the direct exchange rate between two currencies (1 unit of from_code = ? to_code)."""
        from_clean = from_code.strip().upper()
        to_clean = to_code.strip().upper()

        if from_clean == to_clean:
            return 1.0

        from_valute = rate_set.get_valute(from_clean)
        to_valute = rate_set.get_valute(to_clean)

        return round(from_valute.unit_rate() / to_valute.unit_rate(), round_digits)
