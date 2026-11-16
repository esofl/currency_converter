"""HTTP layer (SRP: request/response mapping only). Service is injected (DIP)."""

from pathlib import Path

from flask import Flask, jsonify, render_template, request

from src.exceptions import RatesUnavailableError, ValidationError
from src.rate_service import RateService, RatesResult
from src.validator import InputValidator

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"


def _rates_meta(r: RatesResult) -> dict:
    return {"date": r.rate_set.date, "source": r.rate_set.source_name, "offline": r.offline, "notice": r.notice}


def create_app(service: RateService) -> Flask:
    app = Flask(__name__, template_folder=str(TEMPLATES))

    @app.errorhandler(ValidationError)
    def invalid(e):
        return jsonify(error=str(e)), 400

    @app.errorhandler(KeyError)
    def unknown_currency(e):
        return jsonify(error=f"Неизвестная валюта: {e.args[0] if e.args else ''}"), 400

    @app.errorhandler(RatesUnavailableError)
    def unavailable(e):
        return jsonify(error=str(e)), 503

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/rates")
    def rates():
        r = service.get_rates(InputValidator.validate_date(request.args.get("date", "")))
        currencies = sorted(({"code": v.char_code, "name": v.name} for v in r.rate_set.valutes.values()),
                            key=lambda c: c["code"])
        return jsonify(currencies=currencies, **_rates_meta(r))

    @app.post("/api/convert")
    def convert():
        d = request.get_json(silent=True) or {}
        c = service.convert(str(d.get("amount", "")), str(d.get("from", "")), str(d.get("to", "")), str(d.get("date", "")))
        return jsonify(amount=c.amount, from_code=c.from_code, to_code=c.to_code,
                       result=c.result, rate=c.rate, **_rates_meta(c.rates))

    return app
