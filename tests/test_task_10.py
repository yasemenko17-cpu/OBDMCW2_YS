"""Відкриті тести завдання 10: індекси під робоче навантаження з трьох запитів.

Скрипт студента виконується на таблиці sale_log (24 000 рядків), потім VACUUM ANALYZE і зафіксовані параметри планувальника;
перевіряється тип вузла плану EXPLAIN (FORMAT JSON): наявність Sort, Index Only Scan, зворотного індексного сканування і оцінена вартість.

Повний набір перевірок (інші значення й граничні випадки) є лише у викладача.
"""

import pytest
from conftest import load
from harness import IndexCase, call, has_backward_scan, index_names, node_types, plan_fail


M = load(10)


Q1 = "SELECT id, amount FROM sale_log WHERE customer_id = {} AND sold_on >= DATE '{}' ORDER BY sold_on"


Q2 = "SELECT sold_on, amount FROM sale_log WHERE product_id = {} AND sold_on BETWEEN DATE '{}' AND DATE '{}'"


Q3 = "SELECT * FROM sale_log WHERE status = 'new' ORDER BY sold_on DESC LIMIT {}"


@pytest.fixture
def case(db):
    return IndexCase(db, M)


def no_sort_index_scan(case, sql):
    plan = case.plan(sql)
    types = node_types(plan)
    if "Sort" in types:
        plan_fail(plan, "У плані є вузол Sort: індекс має віддавати рядки вже впорядкованими")
    if "Seq Scan" in types or not any(t in ("Index Scan", "Index Only Scan") for t in types):
        plan_fail(plan, "Очікується Index Scan за вашим індексом")
    return plan


def test_function_exists():
    assert callable(getattr(M, "indexes", None)), "немає функції indexes()"


def test_query1_no_sort(case):
    no_sort_index_scan(case, Q1.format(777, "2025-06-01"))


def test_query2_index_only_scan(case):
    plan = case.plan(Q2.format(17, "2026-05-01", "2026-05-31"))
    if plan["Node Type"] != "Index Only Scan":
        plan_fail(plan, "Очікується Index Only Scan: усі стовпці запиту мають бути в індексі, а VACUUM заповнив карту видимості")
