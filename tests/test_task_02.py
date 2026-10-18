"""Відкриті тести завдання 02: покупки, що перевищують середню суму покупки свого товару.

Кожен випадок завантажує магазин, змінює дані за потреби й порівнює результат запиту з очікуваним.
Повний набір перевірок (інші дані й граничні випадки) є лише у викладача.
"""
import datetime  # noqa: F401
from decimal import Decimal  # noqa: F401

import pytest
from conftest import load
from harness import call, clean_query, has_keyword, run_query_case

M = load(2)

COLUMNS = 4
COLUMN_LIST = 'id, title, amount, avg_amount'

CASES = [
    {
        'id': 'база',
        'setup': [],
        'note': '',
        'expect': [(4, 'Порошок пральний 3 кг', Decimal('458.00'), Decimal('320.60')), (6, 'Молоко 2.5% 900 мл', Decimal('114.00'), Decimal('88.67')), (12, 'Батон нарізний', Decimal('87.00'), Decimal('58.00')), (17, 'Чай чорний 100 г', Decimal('129.00'), Decimal('86.00')), (18, 'Хліб житній', Decimal('64.00'), Decimal('44.80')), (28, 'Хліб житній', Decimal('64.00'), Decimal('44.80')), (32, 'Кава мелена 250 г', Decimal('569.70'), Decimal('379.80')), (33, 'Порошок пральний 3 кг', Decimal('458.00'), Decimal('320.60')), (34, 'Губки кухонні 5 шт', Decimal('64.00'), Decimal('40.00'))],
    },
    {
        'id': 'порожні покупки',
        'setup': ['DELETE FROM purchase'],
        'note': 'усі покупки видалено.',
        'expect': [],
    },
]


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_cases(db, case):
    run_query_case(db, M, case, COLUMNS, COLUMN_LIST)


def test_function_exists():
    assert callable(getattr(M, "query", None)), "немає функції query()"


def test_one_select_statement(db):
    sql = clean_query(call(M, "query"))
    assert sql.lstrip().lower().startswith(("select", "with")), "очікується один запит SELECT або WITH ... SELECT"


def test_uses_window_function():
    sql = call(M, "query")
    assert has_keyword(sql, r"\bOVER\s*\("), "завдання про віконні функції: використайте агрегатну функцію з OVER (...)"
