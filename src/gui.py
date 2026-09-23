"""Graphical User Interface for Currency Converter using Tkinter/ttk."""

import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List

from src.models import ExchangeRateSet
from src.bnm_client import BNMClient
from src.cache_manager import CacheManager
from src.validator import InputValidator
from src.converter import ConverterService
from src.exceptions import NetworkError, RateParsingError, ValidationError, CacheError


class CurrencyConverterApp:
    """Desktop GUI application for currency conversion."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Конвертер валют | НБМ (BNM)")
        self.root.geometry("540x600")
        self.root.minsize(480, 520)

        # Domain services
        self.client = BNMClient()
        self.cache_manager = CacheManager()
        self.rate_set: Optional[ExchangeRateSet] = None

        # State tracking
        self.amount_var = tk.StringVar()
        self.from_curr_var = tk.StringVar(value="EUR")
        self.to_curr_var = tk.StringVar(value="MDL")
        self.result_var = tk.StringVar(value="Введите сумму и нажмите «Конвертировать»")
        self.rate_info_var = tk.StringVar(value="")
        self.validation_msg_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Инициализация...")

        self._configure_styles()
        self._build_ui()
        self._bind_events()

        # Load rates (cache first, then live fetch in background)
        self._initialize_rates()

    def _configure_styles(self):
        """Sets up ttk styles for clean visual appearance."""
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#1e293b")
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 9), foreground="#64748b")
        self.style.configure("Card.TFrame", background="#f8fafc", relief="solid", borderwidth=1)
        self.style.configure("ResultCard.TFrame", background="#f1f5f9", relief="solid", borderwidth=1)
        self.style.configure("ResultTitle.TLabel", font=("Segoe UI", 11), background="#f1f5f9", foreground="#475569")
        self.style.configure("ResultValue.TLabel", font=("Segoe UI", 18, "bold"), background="#f1f5f9", foreground="#0f172a")
        self.style.configure("ResultRate.TLabel", font=("Segoe UI", 9, "italic"), background="#f1f5f9", foreground="#64748b")
        self.style.configure("Error.TLabel", font=("Segoe UI", 9), foreground="#dc2626")
        self.style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), padding=6)
        self.style.configure("Status.TLabel", font=("Segoe UI", 8), foreground="#475569", background="#e2e8f0")

    def _build_ui(self):
        """Constructs all visual components inside the root window."""
        container = ttk.Frame(self.root, padding="16 16 16 8")
        container.pack(fill=tk.BOTH, expand=True)

        # 1. Header
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(header_frame, text="Конвертер Валют", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header_frame,
            text="Официальные курсы Национального Банка Молдовы (BNM)",
            style="SubHeader.TLabel",
        ).pack(anchor="w")

        # 2. Input & Controls Card
        card = ttk.Frame(container, padding="14 14 14 14", style="Card.TFrame")
        card.pack(fill=tk.X, pady=6)

        # Amount Input
        ttk.Label(card, text="Сумма для конвертации:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
        self.amount_entry = ttk.Entry(card, textvariable=self.amount_var, font=("Segoe UI", 12))
        self.amount_entry.pack(fill=tk.X, pady=(0, 2))

        self.error_label = ttk.Label(card, textvariable=self.validation_msg_var, style="Error.TLabel")
        self.error_label.pack(anchor="w", pady=(0, 10))

        # Currency selection row
        curr_frame = ttk.Frame(card)
        curr_frame.pack(fill=tk.X, pady=4)

        # From currency
        from_frame = ttk.Frame(curr_frame)
        from_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(from_frame, text="Из валюты:").pack(anchor="w", pady=(0, 2))
        self.from_combobox = ttk.Combobox(
            from_frame,
            textvariable=self.from_curr_var,
            state="readonly",
            font=("Segoe UI", 10),
        )
        self.from_combobox.pack(fill=tk.X)

        # Swap button
        swap_btn = ttk.Button(curr_frame, text="⇄", width=3, command=self._swap_currencies)
        swap_btn.pack(side=tk.LEFT, padx=8, pady=(16, 0))

        # To currency
        to_frame = ttk.Frame(curr_frame)
        to_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(to_frame, text="В валюту:").pack(anchor="w", pady=(0, 2))
        self.to_combobox = ttk.Combobox(
            to_frame,
            textvariable=self.to_curr_var,
            state="readonly",
            font=("Segoe UI", 10),
        )
        self.to_combobox.pack(fill=tk.X)

        # Convert Action Button (starts disabled until valid amount entered)
        self.convert_button = ttk.Button(
            card,
            text="Конвертировать",
            style="Action.TButton",
            command=self.perform_conversion,
            state="disabled",
        )
        self.convert_button.pack(fill=tk.X, pady=(16, 4))

        # 3. Result Presentation Card
        self.result_card = ttk.Frame(container, padding="14 14 14 14", style="ResultCard.TFrame")
        self.result_card.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(self.result_card, text="Результат расчета:", style="ResultTitle.TLabel").pack(anchor="w")
        self.result_label = ttk.Label(
            self.result_card,
            textvariable=self.result_var,
            style="ResultValue.TLabel",
            wraplength=460,
        )
        self.result_label.pack(anchor="w", pady=(6, 4))

        self.rate_info_label = ttk.Label(
            self.result_card,
            textvariable=self.rate_info_var,
            style="ResultRate.TLabel",
        )
        self.rate_info_label.pack(anchor="w")

        # 4. Refresh & Controls Row
        refresh_frame = ttk.Frame(container)
        refresh_frame.pack(fill=tk.X, pady=(0, 4))

        self.refresh_btn = ttk.Button(
            refresh_frame,
            text="🔄 Обновить курсы",
            command=self._reload_rates_threaded,
        )
        self.refresh_btn.pack(side=tk.RIGHT)

        # 5. Status & Attribution Bar
        status_bar = ttk.Frame(self.root, padding="6 4 6 4", style="Status.TLabel")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = ttk.Label(
            status_bar,
            textvariable=self.status_var,
            style="Status.TLabel",
        )
        self.status_label.pack(side=tk.LEFT)

    def _bind_events(self):
        """Binds reactive listeners to inputs and shortcuts."""
        self.amount_var.trace_add("write", self._on_amount_change)
        self.from_curr_var.trace_add("write", self._on_currency_change)
        self.to_curr_var.trace_add("write", self._on_currency_change)
        self.amount_entry.bind("<Return>", lambda e: self._on_enter_pressed())

    def _on_enter_pressed(self):
        """Handles Enter key press in the amount entry field."""
        if str(self.convert_button["state"]) != "disabled":
            self.perform_conversion()

    def _swap_currencies(self):
        """Swaps source and target currency selections."""
        cur_from = self.from_curr_var.get()
        cur_to = self.to_curr_var.get()
        self.from_curr_var.set(cur_to)
        self.to_curr_var.set(cur_from)
        if str(self.convert_button["state"]) != "disabled":
            self.perform_conversion()

    def _on_amount_change(self, *args):
        """Validates input dynamically on every keystroke and toggles the Convert button."""
        val = self.amount_var.get()
        if not val.strip():
            self.validation_msg_var.set("")
            self.convert_button.config(state="disabled")
            return

        is_valid, err_msg = InputValidator.is_valid_amount(val)
        if is_valid and self.rate_set is not None:
            self.validation_msg_var.set("")
            self.convert_button.config(state="normal")
        else:
            self.validation_msg_var.set(err_msg)
            self.convert_button.config(state="disabled")

    def _on_currency_change(self, *args):
        """Triggers conversion recalculation when user changes dropdown selection if valid."""
        is_valid, _ = InputValidator.is_valid_amount(self.amount_var.get())
        if is_valid and self.rate_set is not None:
            self.perform_conversion()

    def _populate_currency_dropdowns(self):
        """Populates the comboboxes with available currency codes."""
        if not self.rate_set:
            return

        # Sort codes: popular currencies first, then alphabetically
        priority_codes = ["EUR", "USD", "MDL", "RON", "RUB", "UAH", "GBP"]
        all_codes = sorted(list(self.rate_set.valutes.keys()))
        ordered = [c for c in priority_codes if c in all_codes] + [c for c in all_codes if c not in priority_codes]

        self.from_combobox["values"] = ordered
        self.to_combobox["values"] = ordered

        if self.from_curr_var.get() not in ordered:
            self.from_curr_var.set("EUR")
        if self.to_curr_var.get() not in ordered:
            self.to_curr_var.set("MDL")

    def _initialize_rates(self):
        """Tries to restore cached rates immediately, then fetches live data asynchronously."""
        try:
            cached = self.cache_manager.load_rates()
            if cached:
                self.rate_set = cached
                self._populate_currency_dropdowns()
                self._update_status(
                    f"Загружен локальный кэш от {cached.date} | Источник: {cached.source_name}"
                )
        except Exception as e:
            # Non-blocking cache read error
            pass

        # Always trigger background fetch
        self._reload_rates_threaded()

    def _reload_rates_threaded(self):
        """Launches background rate fetch to keep the UI smooth and responsive."""
        self.refresh_btn.config(state="disabled")
        self._update_status("Подключение к Национальному Банку Молдовы (BNM)...")

        worker = threading.Thread(target=self._fetch_rates_worker, daemon=True)
        worker.start()

    def _fetch_rates_worker(self):
        """Worker thread logic for obtaining rates from BNM."""
        error_msg = None
        new_rates = None
        try:
            new_rates = self.client.fetch_rates("23.09.2026")
            self.cache_manager.save_rates(new_rates)
        except NetworkError as e:
            error_msg = f"Сеть недоступна: {e}"
        except RateParsingError as e:
            error_msg = f"Ошибка данных BNM: {e}"
        except Exception as e:
            error_msg = f"Непредвиденная ошибка: {e}"

        # Schedule UI update in the main thread
        self.root.after(0, self._on_rates_fetched, new_rates, error_msg)

    def _on_rates_fetched(self, new_rates: Optional[ExchangeRateSet], error_msg: Optional[str]):
        """Runs in main thread after background fetch finishes."""
        self.refresh_btn.config(state="normal")

        if new_rates:
            self.rate_set = new_rates
            self._populate_currency_dropdowns()
            self._update_status(
                f"Курсы актуальны на {new_rates.date} | Источник: {new_rates.source_name}"
            )
            # Re-check amount field to activate button if user typed while loading
            self._on_amount_change()
        else:
            # Network or parsing failure
            if self.rate_set:
                # We have cache fallback
                self._update_status(
                    f"⚠️ Оффлайн-режим (кэш от {self.rate_set.date}) | Источник: {self.rate_set.source_name}"
                )
                messagebox.showwarning(
                    "Внимание: Оффлайн-режим",
                    f"Не удалось обновить курсы валют ({error_msg}).\n\n"
                    f"Приложение продолжает работу с последними сохраненными курсами от {self.rate_set.date}.",
                )
            else:
                # No cache available at all
                self._update_status("❌ Ошибка: курсы валют недоступны")
                messagebox.showerror(
                    "Ошибка соединения",
                    f"Не удалось загрузить курсы валют и сохраненный кэш отсутствует.\n\n"
                    f"Детали ошибки: {error_msg}\n"
                    "Проверьте интернет-соединение и нажмите «Обновить курсы».",
                )

    def _update_status(self, text: str):
        """Updates the status bar text safely."""
        self.status_var.set(text)

    def perform_conversion(self):
        """Executes currency conversion calculation and updates the result card."""
        if not self.rate_set:
            messagebox.showwarning("Внимание", "Курсы валют еще не загружены.")
            return

        raw_amount = self.amount_var.get()
        try:
            amount = InputValidator.validate_amount(raw_amount)
        except ValidationError as e:
            self.validation_msg_var.set(str(e))
            self.convert_button.config(state="disabled")
            return

        from_code = self.from_curr_var.get()
        to_code = self.to_curr_var.get()

        if not from_code or not to_code:
            messagebox.showwarning("Внимание", "Выберите исходную и целевую валюты.")
            return

        try:
            converted = ConverterService.convert(amount, from_code, to_code, self.rate_set)
            cross_rate = ConverterService.get_cross_rate(from_code, to_code, self.rate_set)

            # Format primary display
            if from_code == to_code:
                result_text = f"{amount:,.2f} {from_code} = {converted:,.2f} {to_code}"
                rate_info = f"1 {from_code} = 1.0000 {to_code} (идентичные валюты)"
            else:
                result_text = f"{amount:,.2f} {from_code} = {converted:,.2f} {to_code}"
                rate_info = (
                    f"Курс конвертации: 1 {from_code} = {cross_rate:.4f} {to_code} "
                    f"(на {self.rate_set.date})"
                )

            self.result_var.set(result_text)
            self.rate_info_var.set(rate_info)

        except Exception as e:
            messagebox.showerror("Ошибка расчета", f"Не удалось выполнить конвертацию: {e}")
