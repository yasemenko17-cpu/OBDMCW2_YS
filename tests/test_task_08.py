"""Відкриті тести завдання 08: частковий і функціональний індекси.

Скрипт студента виконується на таблиці sale_log (24 000 рядків), потім VACUUM ANALYZE і зафіксовані параметри планувальника;
перевіряється каталог (indpred, indexprs) і тип вузла плану EXPLAIN (FORMAT JSON).

Повний набір перевірок (інші значення й граничні випадки) є лише у викладача.
"""

import pytest
from conftest import load
from harness import IndexCase, call, index_names, node_types, plan_fail


M = load(8)


Q_NEW = "SELECT * FROM sale_log WHERE status = 'new' AND sold_on < DATE '{}'"


Q_EMAIL = "SELECT * FROM sale_log WHERE lower(email) = '{}'"


@pytest.fixture
def case(db):
    return IndexCase(db, M)


def partial_names(case):
    return {i["name"] for i in case.new_indexes() if i["partial"]}


def expr_names(case):
    return {i["name"] for i in case.new_indexes() if i["expr"]}


def uses(case, sql, names, what):
    plan = case.plan(sql)
    if "Seq Scan" in node_types(plan):
        plan_fail(plan, "Запит читає всю таблицю (Seq Scan)")
    if not names & set(index_names(plan)):
        plan_fail(plan, f"План не використовує {what}")
    return plan


def test_function_exists():
    assert callable(getattr(M, "indexes", None)), "немає функції indexes()"


def test_one_partial_index_on_new_status(case):
    parts = [i for i in case.new_indexes() if i["partial"]]
    assert len(parts) == 1, "потрібен рівно один частковий індекс (з WHERE)"
    assert parts[0]["pred"].replace("(", "").replace(")", "") == "status = 'new'::text", f"умова індексу має бути status = 'new', а є {parts[0]['pred']}"


def test_email_query_uses_expression_index(case):
    uses(case, Q_EMAIL.format("client777@example.com"), expr_names(case), "функціональний індекс")
