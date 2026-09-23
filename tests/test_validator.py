"""Unit tests for user input validation."""

import unittest
from src.validator import InputValidator
from src.exceptions import ValidationError


class TestInputValidator(unittest.TestCase):
    """Verifies edge cases in user input validation."""

    def test_valid_integer_and_float(self):
        self.assertEqual(InputValidator.validate_amount("100"), 100.0)
        self.assertEqual(InputValidator.validate_amount("12.50"), 12.5)
        self.assertEqual(InputValidator.validate_amount(" 42.99 "), 42.99)

    def test_comma_decimal_separator(self):
        """Accepts European/Russian comma separator."""
        self.assertEqual(InputValidator.validate_amount("100,50"), 100.5)
        self.assertEqual(InputValidator.validate_amount(" 0,05 "), 0.05)

    def test_reject_empty_and_whitespace(self):
        with self.assertRaises(ValidationError):
            InputValidator.validate_amount("")
        with self.assertRaises(ValidationError):
            InputValidator.validate_amount("   ")

    def test_reject_zero(self):
        with self.assertRaises(ValidationError):
            InputValidator.validate_amount("0")
        with self.assertRaises(ValidationError):
            InputValidator.validate_amount("0.0")
        with self.assertRaises(ValidationError):
            InputValidator.validate_amount("0,000")

    def test_reject_negative_numbers(self):
        with self.assertRaises(ValidationError):
            InputValidator.validate_amount("-10")
        with self.assertRaises(ValidationError):
            InputValidator.validate_amount("-0.01")

    def test_reject_alphabetic_and_symbols(self):
        with self.assertRaises(ValidationError):
            InputValidator.validate_amount("abc")
        with self.assertRaises(ValidationError):
            InputValidator.validate_amount("100a")
        with self.assertRaises(ValidationError):
            InputValidator.validate_amount("12$50")
        with self.assertRaises(ValidationError):
            InputValidator.validate_amount("--5")

    def test_is_valid_amount_helper(self):
        ok, msg = InputValidator.is_valid_amount("150.25")
        self.assertTrue(ok)
        self.assertEqual(msg, "")

        bad, msg = InputValidator.is_valid_amount("xyz")
        self.assertFalse(bad)
        self.assertIn("цифры", msg)


if __name__ == "__main__":
    unittest.main()
