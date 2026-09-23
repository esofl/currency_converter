"""Data models for currency exchange rates."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any


@dataclass
class Valute:
    """Represents a single currency exchange rate entry."""
    id: str
    num_code: str
    char_code: str
    nominal: int
    name: str
    value: float

    def unit_rate(self) -> float:
        """Returns the cost of 1 unit of this currency in Moldovan Lei (MDL)."""
        if self.nominal <= 0:
            raise ValueError(f"Nominal must be greater than zero for {self.char_code}")
        return self.value / float(self.nominal)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes Valute to dictionary for JSON caching."""
        return {
            "id": self.id,
            "num_code": self.num_code,
            "char_code": self.char_code,
            "nominal": self.nominal,
            "name": self.name,
            "value": self.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Valute":
        """Instantiates Valute from dictionary."""
        return cls(
            id=str(data.get("id", "")),
            num_code=str(data.get("num_code", "")),
            char_code=str(data.get("char_code", "")).upper(),
            nominal=int(data.get("nominal", 1)),
            name=str(data.get("name", "")),
            value=float(data.get("value", 0.0)),
        )


@dataclass
class ExchangeRateSet:
    """Collection of exchange rates for a specific date and data source."""
    date: str
    source_name: str
    valutes: Dict[str, Valute] = field(default_factory=dict)
    is_cached: bool = False
    fetched_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def get_valute(self, char_code: str) -> Valute:
        """Retrieves a valute by uppercase 3-letter currency code."""
        code = char_code.strip().upper()
        if code not in self.valutes:
            raise KeyError(f"Currency code '{code}' not found in exchange rate set")
        return self.valutes[code]

    def to_dict(self) -> Dict[str, Any]:
        """Serializes rate set to dictionary for JSON persistence."""
        return {
            "date": self.date,
            "source_name": self.source_name,
            "is_cached": True,
            "fetched_at": self.fetched_at,
            "valutes": {k: v.to_dict() for k, v in self.valutes.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExchangeRateSet":
        """Instantiates ExchangeRateSet from dictionary."""
        valutes_dict = {}
        for code, v_data in data.get("valutes", {}).items():
            valutes_dict[code.upper()] = Valute.from_dict(v_data)

        return cls(
            date=str(data.get("date", "")),
            source_name=str(data.get("source_name", "Национальный Банк Молдовы (BNM)")),
            valutes=valutes_dict,
            is_cached=True,
            fetched_at=str(data.get("fetched_at", "")),
        )
