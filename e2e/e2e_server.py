"""
Playwright test server: real RateService/CacheManager/web, fake RateSource (LSP — same
protocol as BNMClient). Modes are switched by the test via /__e2e__/mode/<mode>:
  online   — fixed rates for the requested date
  holiday  — rates published three days earlier than requested
  offline  — NetworkError
POST /__e2e__/reset clears the cache.
"""

import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import jsonify  # noqa: E402

from src.cache_manager import CacheManager  # noqa: E402
from src.exceptions import NetworkError  # noqa: E402
from src.models import ExchangeRateSet, Valute  # noqa: E402
from src.rate_service import RateService  # noqa: E402
from src.web import create_app  # noqa: E402


class FakeRateSource:
    def __init__(self):
        self.mode = "online"

    def fetch_rates(self, target_date=None):
        if self.mode == "offline":
            raise NetworkError("e2e: network down")
        d = datetime.strptime(target_date, "%d.%m.%Y")
        if self.mode == "holiday":
            d -= timedelta(days=3)
        return ExchangeRateSet(d.strftime("%d.%m.%Y"), "Национальный Банк Молдовы (BNM)", {
            "MDL": Valute("0", "498", "MDL", 1, "Молдавский лей", 1.0),
            "EUR": Valute("47", "978", "EUR", 1, "Евро", 20.0),
            "USD": Valute("44", "840", "USD", 1, "Доллар США", 16.0),
            "JPY": Valute("1", "392", "JPY", 100, "Японская иена", 12.0),
        })


if __name__ == "__main__":
    port = int(sys.argv[1])
    tmp = tempfile.mkdtemp(prefix="lab3_e2e_")
    cache_path = os.path.join(tmp, "rates.json")
    source = FakeRateSource()
    app = create_app(RateService(source, CacheManager(cache_path)))

    @app.post("/__e2e__/mode/<mode>")
    def set_mode(mode):
        source.mode = mode
        return jsonify(ok=True)

    @app.post("/__e2e__/reset")
    def reset():
        source.mode = "online"
        if os.path.exists(cache_path):
            os.remove(cache_path)
        return jsonify(ok=True)

    try:
        app.run(host="127.0.0.1", port=port)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
