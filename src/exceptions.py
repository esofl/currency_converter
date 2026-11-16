"""Domain-specific exceptions for Currency Converter."""


class ConverterBaseException(Exception):
    """Base class for converter domain exceptions."""
    pass


class ValidationError(ConverterBaseException):
    """Raised when user input fails numerical or business constraints."""
    pass


class NetworkError(ConverterBaseException):
    """Raised when remote communication with BNM fails."""
    pass


class RateParsingError(ConverterBaseException):
    """Raised when XML parsing fails or required fields are missing."""
    pass


class CacheError(ConverterBaseException):
    """Raised when local cache read or write operations fail."""
    pass


class NoDataError(RateParsingError):
    """Source has no publication for the requested date (empty list or HTTP 404)."""
    pass


class RatesUnavailableError(ConverterBaseException):
    """Neither the live source nor the local cache can provide rates."""
    pass
