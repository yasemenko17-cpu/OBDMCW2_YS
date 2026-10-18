"""Відкриті тести завдання 04: два індекси для вибірок за клієнтом і за датою.

Скрипт студента виконується на таблиці sale_log (24 000 рядків), потім виконуються VACUUM ANALYZE і зафіксовані параметри
планувальника; перевіряється тип вузла плану EXPLAIN (FORMAT JSON), а не час виконання.

Повний набір перевірок (інші значення й граничні випадки) є лише у викладача.
"""

import pytest
from conftest import load
from harness import IndexCase, call, index_names, node_types, plan_fail


M = load(4)


Q_CUSTOMER = "SELECT * FROM sale_log WHERE customer_id = {}"


Q_DATE = "SELECT * FROM sale_log WHERE sold_on = DATE '{}'"


@pytest.fixture
def case(db):
    return IndexCase(db, M)


def non_seq_with_new_index(case, sql):
    plan = case.plan(sql)
    types = node_types(plan)
    if "Seq Scan" in types:
        plan_fail(plan, "Запит читає всю таблицю (Seq Scan): потрібен індекс, який планувальник зможе використати")
    names = [n for n in index_names(plan) if n != "sale_log_pkey"]
    if not names:
        plan_fail(plan, "У плані немає вашого індексу")
    return plan


def test_function_exists():
    assert callable(getattr(M, "indexes", None)), "немає функції indexes()"


def test_script_runs_and_indexes_valid(case):
    new = case.new_indexes()
    assert new, "скрипт не створив жодного індексу"
    assert all(i["valid"] for i in new), "усі індекси мають бути коректними (indisvalid)"


def test_customer_query_uses_index(case):
    non_seq_with_new_index(case, Q_CUSTOMER.format(777))
