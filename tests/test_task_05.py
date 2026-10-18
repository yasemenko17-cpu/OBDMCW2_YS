"""Відкриті тести завдання 05: звіт за клієнтами без розмноження рядків.

Кожен випадок завантажує магазин, змінює дані за потреби й порівнює результат запиту з очікуваним.
Повний набір перевірок (інші дані й граничні випадки) є лише у викладача.
"""
import datetime  # noqa: F401
from decimal import Decimal  # noqa: F401

import pytest
from conftest import load
from harness import call, clean_query, has_keyword, run_query_case

M = load(5)

COLUMNS = 5
COLUMN_LIST = 'id, full_name, referrals, purchases, items'

CASES = [
    {
        'id': 'база',
        'setup': [],
        'note': '',
        'expect': [(1, 'Тарас Олійник', 3, 3, 6), (2, 'Ганна Мазур', 2, 4, 10), (3, 'Роман Клименко', 2, 3, 5), (4, 'Лілія Остапчук', 1, 5, 8), (5, 'Максим Береза', 0, 4, 8), (6, 'Катерина Шульга', 1, 3, 6), (7, 'Євген Логвин', 0, 5, 7), (8, 'Аліна Рибак', 1, 3, 3), (9, 'Віктор Гнатюк', 0, 1, 1), (10, 'Зоя Приходько', 0, 0, 0), (11, 'Назар Коломієць', 0, 2, 4), (12, 'Людмила Данилюк', 0, 1, 1), (13, 'Степан Мартин', 0, 0, 0), (14, 'Дарина Яковенко', 0, 0, 0)],
    },
    {
        'id': 'порожні покупки',
        'setup': ['DELETE FROM purchase'],
        'note': 'усі покупки видалено.',
        'expect': [(1, 'Тарас Олійник', 3, 0, 0), (2, 'Ганна Мазур', 2, 0, 0), (3, 'Роман Клименко', 2, 0, 0), (4, 'Лілія Остапчук', 1, 0, 0), (5, 'Максим Береза', 0, 0, 0), (6, 'Катерина Шульга', 1, 0, 0), (7, 'Євген Логвин', 0, 0, 0), (8, 'Аліна Рибак', 1, 0, 0), (9, 'Віктор Гнатюк', 0, 0, 0), (10, 'Зоя Приходько', 0, 0, 0), (11, 'Назар Коломієць', 0, 0, 0), (12, 'Людмила Данилюк', 0, 0, 0), (13, 'Степан Мартин', 0, 0, 0), (14, 'Дарина Яковенко', 0, 0, 0)],
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
