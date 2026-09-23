<div align="center">

# 💱 Desktop Currency Converter
### Лабораторная работа №3: Spec-Driven Development и Google Antigravity

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Spec Kit](https://img.shields.io/badge/spec--driven-GitHub_Spec_Kit-black.svg?style=for-the-badge&logo=github)](https://github.com/github/spec-kit)
[![Google Antigravity](https://img.shields.io/badge/built_with-Google_Antigravity_2.0-4285F4.svg?style=for-the-badge&logo=google)](https://antigravity.google)
[![Tests Status](https://img.shields.io/badge/tests-26%20passed-success.svg?style=for-the-badge&logo=pytest)](file:///E:/currency_converter/tests)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

*Десктопное приложение для конвертации валют с графическим интерфейсом на базе официальных курсов Национального Банка Молдовы (НБМ / BNM), разработанное по методологии Spec-Driven Development.*

</div>

---

## 📌 О проекте

Приложение разработано в рамках Лабораторной работы №3 по методологии **Spec-Driven Development (SDD)**:
1. **Спецификация**: Формирование конституции, спецификации, архитектурного плана и задач с помощью **GitHub Spec Kit**.
2. **Сборка агентом**: Реализация кода автономным агентом в **Google Antigravity 2.0** на базе подготовленных спецификаций.
3. **Строгая культура Git**: Отдельная ветка на каждый этап (`feat/specifications`, `feat/currency-converter-app`, `test/unit-tests-and-report`) со слиянием в `main` исключительно через **Pull Request**.

---

## ✨ Ключевые возможности

- 🏛️ **Официальные курсы BNM**: Прямая интеграция с XML-шлюзом [Национального Банка Молдовы](https://www.bnm.md/ru/official_exchange_rates) (`ValCurs`).
- ⚡ **Двунаправленная и кросс-конвертация**: Поддержка конвертации между любыми мировыми валютами (EUR, USD, GBP, RON, UAH, RUB, JPY и др.) и молдавским леем (MDL).
- 🔄 **Корректный учет номиналов**: Автоматическая обработка тега `<Nominal>` для валют, котируемых сотнями/десятками (например, 100 JPY, 100 HUF).
- 🛡️ **Отказоустойчивость и оффлайн-режим**: При сбое сети или отсутствии соединения приложение переходит на локально кэшированные курсы (`cache/exchange_rates.json`) с индикацией даты.
- 📅 **Обработка выходных и праздников**: Автоматический откат на предыдущие рабочие банковские дни при получении пустой котировки.
- 🛑 **Реактивная валидация ввода**: Кнопка конвертации заблокирована до ввода корректного положительного числа; поддержка запятой и точки как десятичных разделителей.
- 🎯 **Тождественная конвертация**: Мгновенный расчет $X \to X$ без лишних сетевых вызовов.

---

## 📐 Архитектура проекта

```
currency_converter/
├── .github/                   # Spec Kit интеграции и навыки агента
├── .specify/                  # Конфигурация Spec Kit и Конституция проекта
│   └── memory/constitution.md # Принципы и ограничения разработки
├── specs/
│   └── 001-currency-converter/
│       ├── spec.md            # Функциональная спецификация и User Stories
│       ├── plan.md            # Технический архитектурный план
│       ├── data-model.md      # Модели данных и ER-схема
│       ├── tasks.md           # Декомпозиция задач реализации
│       ├── research.md        # Исследование BNM XML и UI-стека
│       └── verification.md    # Матрица согласованности требований
├── src/
│   ├── __init__.py
│   ├── models.py              # Valute, ExchangeRateSet dataclasses
│   ├── exceptions.py          # Доменные исключения (NetworkError, ValidationError и т.д.)
│   ├── bnm_client.py          # Клиент BNM XML с обработкой выходных дней
│   ├── cache_manager.py       # Менеджер локального JSON-кэша
│   ├── validator.py           # Валидатор сумм и разделителей
│   ├── converter.py           # Математическое ядро конвертации и кросс-курсов
│   └── gui.py                 # Desktop GUI (Tkinter / ttk, потокобезопасный)
├── tests/
│   ├── __init__.py
│   ├── test_parser.py         # Тесты разбора XML, номиналов и инъекции MDL
│   ├── test_converter.py      # Тесты прямого, обратного и кросс-расчета
│   ├── test_validator.py      # Тесты валидации (нули, отрицательные, строки)
│   ├── test_cache.py          # Тесты сохранения и восстановления кэша
│   └── test_network_fallback.py # Тесты сбоев сети и отката в выходные дни
├── cache/
│   └── exchange_rates.json    # Локальный кэш последних курсов
├── main.py                    # Точка входа в приложение
├── REPORT.md                  # Итоговый аналитический отчёт по лабораторной
└── README.md                  # Документация проекта
```

---

## 🚀 Быстрый старт

### Требования
- Python 3.11 или новее.
- Стандартная библиотека Python (`tkinter`, `urllib`, `xml.etree`, `unittest`). Дополнительные внешние pip-зависимости не требуются.

### Запуск приложения
Запустите графическое приложение одной командой:
```powershell
python main.py
```

---

## 🧪 Запуск Unit-тестов

В соответствии с требованиями ТЗ (Часть 6), все тесты запускаются локально **одной командой**:

```powershell
python -m unittest discover tests
```

### Результат выполнения тестов:
```text
..........................
----------------------------------------------------------------------
Ran 26 tests in 0.147s

OK
```

Покрытие включает:
1. Разбор XML-ответа источника (`test_parser.py`).
2. Расчет конвертации, включая обратное направление и номиналы (`test_converter.py`).
3. Поведение при пустом ответе и сбоях сети (`test_network_fallback.py`).
4. Валидацию пользовательского ввода (`test_validator.py`).
5. Надежность локального кэша (`test_cache.py`).

---

## 📄 Отчёт о работе
Подробный отчёт, содержащий ответы на все 5 обязательных пунктов ТЗ (выбор источника, модели Antigravity, анализ ошибок агента и ручных исправлений), доступен в файле [REPORT.md](./REPORT.md).

---

## 📜 Лицензия
Проект распространяется под лицензией MIT.
