"""Input validation service for currency conversion operations."""

import math
from typing import Tuple
from src.exceptions import ValidationError


class InputValidator:
    """Validates user-supplied values before passing to conversion engine."""

    @staticmethod
    def clean_number_string(raw_str: str) -> str:
        """Sanitizes user input by stripping spaces and normalizing decimal commas."""
        if raw_str is None:
            return ""
        # Remove non-breaking spaces and standard whitespace
        cleaned = raw_str.strip().replace("\xa0", "").replace(" ", "")
        # Normalize European decimal comma to dot
        return cleaned.replace(",", ".")

    @classmethod
    def validate_amount(cls, raw_str: str) -> float:
        """
        Parses and validates that the raw amount string is a strictly positive finite number.
        Raises ValidationError if invalid.
        """
        cleaned = cls.clean_number_string(raw_str)
        if not cleaned:
            raise ValidationError("Поле суммы не может быть пустым.")

        try:
            val = float(cleaned)
        except ValueError as e:
            raise ValidationError("Сумма должна содержать только цифры и десятичный разделитель.") from e

        if math.isnan(val) or math.isinf(val):
            raise ValidationError("Введено недопустимое числовое значение.")

        if val <= 0.0:
            raise ValidationError("Сумма должна быть строго больше нуля.")

        return val

    @classmethod
    def is_valid_amount(cls, raw_str: str) -> Tuple[bool, str]:
        """
        Non-raising helper for UI bindings.
        Returns (is_valid, error_message).
        """
        try:
            cls.validate_amount(raw_str)
            return True, ""
        except ValidationError as e:
            return False, str(e)
