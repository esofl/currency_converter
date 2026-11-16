"""Composition root: wires BNM client + JSON cache into RateService and serves the web UI."""

import logging
import threading
import webbrowser

from src.bnm_client import BNMClient
from src.cache_manager import CacheManager
from src.rate_service import RateService
from src.web import create_app

HOST, PORT = "127.0.0.1", 5000


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    app = create_app(RateService(BNMClient(), CacheManager()))
    threading.Timer(1.0, lambda: webbrowser.open(f"http://{HOST}:{PORT}")).start()
    app.run(host=HOST, port=PORT)


if __name__ == "__main__":
    main()
