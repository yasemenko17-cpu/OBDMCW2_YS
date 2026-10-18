"""Відкриті тести завдання 06: архівація доставлених покупок одним оператором.

Кожен випадок завантажує магазин, змінює дані за потреби, виконує команду студента й порівнює стан таблиць.
Повний набір перевірок (інші дані й граничні випадки) є лише у викладача.
"""
import datetime  # noqa: F401
from decimal import Decimal  # noqa: F401

import pytest
from conftest import load
from harness import call, has_keyword, need_text, run_statement_case, split_statements

M = load(6)

CASES = [
    {
        'id': 'база',
        'setup': [],
        'note': '',
        'error': '',
        'expect': {'purchase': [(1, 4, 3, 2, datetime.date(2023, 10, 3), None), (3, 9, 12, 1, datetime.date(2023, 10, 12), None), (4, 11, 9, 2, datetime.date(2023, 10, 22), None), (5, 4, 1, 1, datetime.date(2023, 11, 5), None), (7, 7, 16, 1, datetime.date(2023, 11, 19), None), (8, 7, 9, 1, datetime.date(2023, 12, 2), None), (9, 4, 2, 1, datetime.date(2023, 12, 13), None), (10, 1, 6, 2, datetime.date(2023, 12, 20), None), (13, 5, 2, 2, datetime.date(2024, 2, 25), None), (16, 1, 13, 3, datetime.date(2024, 5, 10), None), (17, 2, 1, 2, datetime.date(2024, 7, 23), None), (18, 3, 16, 2, datetime.date(2024, 7, 26), datetime.date(2024, 7, 29)), (19, 8, 9, 1, datetime.date(2024, 8, 26), datetime.date(2024, 10, 5)), (20, 8, 6, 1, datetime.date(2024, 9, 7), datetime.date(2024, 9, 29)), (21, 7, 5, 1, datetime.date(2024, 9, 23), datetime.date(2024, 10, 6)), (22, 1, 9, 1, datetime.date(2024, 11, 10), datetime.date(2024, 11, 22)), (23, 6, 10, 1, datetime.date(2024, 11, 28), datetime.date(2025, 1, 7)), (24, 3, 15, 2, datetime.date(2025, 1, 30), None), (25, 4, 2, 2, datetime.date(2025, 1, 31), datetime.date(2025, 2, 13)), (26, 5, 13, 3, datetime.date(2025, 2, 18), datetime.date(2025, 3, 7)), (27, 5, 10, 1, datetime.date(2025, 3, 5), datetime.date(2025, 4, 4)), (28, 4, 16, 2, datetime.date(2025, 4, 9), datetime.date(2025, 4, 18)), (29, 6, 2, 2, datetime.date(2025, 4, 28), datetime.date(2025, 5, 14)), (30, 5, 3, 2, datetime.date(2025, 5, 20), datetime.date(2025, 6, 21)), (31, 7, 16, 1, datetime.date(2025, 6, 7), None), (32, 2, 2, 3, datetime.date(2025, 6, 8), datetime.date(2025, 6, 26)), (33, 11, 9, 2, datetime.date(2025, 6, 21), datetime.date(2025, 6, 25)), (34, 2, 10, 2, datetime.date(2025, 6, 22), datetime.date(2025, 6, 25))], 'purchase_archive': [(2, 3, 1, 1, datetime.date(2023, 10, 9), datetime.date(2023, 10, 29)), (6, 2, 3, 3, datetime.date(2023, 11, 11), datetime.date(2023, 11, 16)), (11, 12, 10, 1, datetime.date(2024, 2, 20), datetime.date(2024, 2, 24)), (12, 6, 6, 3, datetime.date(2024, 2, 21), datetime.date(2024, 3, 5)), (14, 8, 16, 1, datetime.date(2024, 3, 20), datetime.date(2024, 4, 23)), (15, 7, 8, 3, datetime.date(2024, 4, 27), datetime.date(2024, 5, 1))], 'archive_log': [(1, 6)]},
    },
    {
        'id': 'нічого переносити',
        'setup': ["DELETE FROM purchase WHERE shipped_on IS NOT NULL AND ordered_on < DATE '2024-07-01'"],
        'note': 'видалено всі покупки, які підпадали під архівацію: журнал усе одно отримує рядок із нулем.',
        'error': '',
        'expect': {'purchase': [(1, 4, 3, 2, datetime.date(2023, 10, 3), None), (3, 9, 12, 1, datetime.date(2023, 10, 12), None), (4, 11, 9, 2, datetime.date(2023, 10, 22), None), (5, 4, 1, 1, datetime.date(2023, 11, 5), None), (7, 7, 16, 1, datetime.date(2023, 11, 19), None), (8, 7, 9, 1, datetime.date(2023, 12, 2), None), (9, 4, 2, 1, datetime.date(2023, 12, 13), None), (10, 1, 6, 2, datetime.date(2023, 12, 20), None), (13, 5, 2, 2, datetime.date(2024, 2, 25), None), (16, 1, 13, 3, datetime.date(2024, 5, 10), None), (17, 2, 1, 2, datetime.date(2024, 7, 23), None), (18, 3, 16, 2, datetime.date(2024, 7, 26), datetime.date(2024, 7, 29)), (19, 8, 9, 1, datetime.date(2024, 8, 26), datetime.date(2024, 10, 5)), (20, 8, 6, 1, datetime.date(2024, 9, 7), datetime.date(2024, 9, 29)), (21, 7, 5, 1, datetime.date(2024, 9, 23), datetime.date(2024, 10, 6)), (22, 1, 9, 1, datetime.date(2024, 11, 10), datetime.date(2024, 11, 22)), (23, 6, 10, 1, datetime.date(2024, 11, 28), datetime.date(2025, 1, 7)), (24, 3, 15, 2, datetime.date(2025, 1, 30), None), (25, 4, 2, 2, datetime.date(2025, 1, 31), datetime.date(2025, 2, 13)), (26, 5, 13, 3, datetime.date(2025, 2, 18), datetime.date(2025, 3, 7)), (27, 5, 10, 1, datetime.date(2025, 3, 5), datetime.date(2025, 4, 4)), (28, 4, 16, 2, datetime.date(2025, 4, 9), datetime.date(2025, 4, 18)), (29, 6, 2, 2, datetime.date(2025, 4, 28), datetime.date(2025, 5, 14)), (30, 5, 3, 2, datetime.date(2025, 5, 20), datetime.date(2025, 6, 21)), (31, 7, 16, 1, datetime.date(2025, 6, 7), None), (32, 2, 2, 3, datetime.date(2025, 6, 8), datetime.date(2025, 6, 26)), (33, 11, 9, 2, datetime.date(2025, 6, 21), datetime.date(2025, 6, 25)), (34, 2, 10, 2, datetime.date(2025, 6, 22), datetime.date(2025, 6, 25))], 'purchase_archive': [], 'archive_log': [(1, 0)]},
    },
]


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_cases(db, case):
    run_statement_case(db, M, case)


def test_function_exists():
    assert callable(getattr(M, "statement", None)), "немає функції statement()"


def test_single_command():
    sql = need_text(call(M, "statement"), "statement()")
    assert len(split_statements(sql)) == 1, "потрібна рівно одна команда: оператор має бути атомарним"


def test_uses_data_modifying_cte():
    sql = call(M, "statement")
    assert has_keyword(sql, r"^\s*WITH\b") and has_keyword(sql, r"\bDELETE\b") and has_keyword(sql, r"\bRETURNING\b"), (
        "потрібен оператор WITH з DELETE ... RETURNING")
