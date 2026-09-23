"""Main entry point for Desktop Currency Converter."""

import sys
import tkinter as tk
from src.gui import CurrencyConverterApp


def main():
    """Initializes and runs the Tkinter currency converter desktop application."""
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
