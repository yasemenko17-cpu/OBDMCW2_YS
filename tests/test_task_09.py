"""Відкриті тести завдання 09: клієнти, що дають перші 80 % виручки кожної категорії.

Кожен випадок завантажує магазин, змінює дані за потреби й порівнює результат запиту з очікуваним.
Повний набір перевірок (інші дані й граничні випадки) є лише у викладача.
"""
import datetime  # noqa: F401
from decimal import Decimal  # noqa: F401

import pytest
from conftest import load
from harness import call, clean_query, has_keyword, run_query_case

M = load(9)

COLUMNS = 4
COLUMN_LIST = 'category, customer, revenue, cum_pct'

CASES = [
    {
        'id': 'база',
        'setup': [],
        'note': '',
        'expect': [('Напої', 'Ганна Мазур', Decimal('698.70'), Decimal('32.1')), ('Напої', 'Лілія Остапчук', Decimal('634.20'), Decimal('61.2')), ('Напої', 'Максим Береза', Decimal('379.80'), Decimal('78.6')), ('Напої', 'Катерина Шульга', Decimal('379.80'), Decimal('96.1')), ('Молочні вироби', 'Роман Клименко', Decimal('196.00'), Decimal('40.1')), ('Молочні вироби', 'Ганна Мазур', Decimal('114.00'), Decimal('63.4')), ('Молочні вироби', 'Лілія Остапчук', Decimal('76.00'), Decimal('78.9')), ('Молочні вироби', 'Максим Береза', Decimal('76.00'), Decimal('94.5')), ('Хлібобулочні', 'Катерина Шульга', Decimal('87.00'), Decimal('21.9')), ('Хлібобулочні', 'Роман Клименко', Decimal('64.00'), Decimal('37.9')), ('Хлібобулочні', 'Лілія Остапчук', Decimal('64.00'), Decimal('54.0')), ('Хлібобулочні', 'Євген Логвин', Decimal('64.00'), Decimal('70.1')), ('Хлібобулочні', 'Аліна Рибак', Decimal('61.00'), Decimal('85.4')), ('Побутова хімія', 'Назар Коломієць', Decimal('916.00'), Decimal('46.1')), ('Побутова хімія', 'Євген Логвин', Decimal('454.00'), Decimal('68.9')), ('Побутова хімія', 'Тарас Олійник', Decimal('229.00'), Decimal('80.4'))],
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
