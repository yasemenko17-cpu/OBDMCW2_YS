"""Відкриті тести завдання 01: клієнти, що купували напої та молочні вироби, але не хімію.

Кожен випадок завантажує магазин, змінює дані за потреби й порівнює результат запиту з очікуваним.
Повний набір перевірок (інші дані й граничні випадки) є лише у викладача.
"""
import datetime  # noqa: F401
from decimal import Decimal  # noqa: F401

import pytest
from conftest import load
from harness import call, clean_query, has_keyword, run_query_case

M = load(1)

COLUMNS = 2
COLUMN_LIST = 'id, full_name'

CASES = [
    {
        'id': 'база',
        'setup': [],
        'note': '',
        'expect': [(3, 'Роман Клименко'), (4, 'Лілія Остапчук')],
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


def test_uses_set_operator():
    sql = call(M, "query")
    assert has_keyword(sql, r"\b(INTERSECT|EXCEPT|UNION)\b"), "завдання про оператори над множинами: використайте INTERSECT, EXCEPT або UNION"
