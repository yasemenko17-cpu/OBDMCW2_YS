"""Відкриті тести завдання 03: часткове скасування в транзакції (SAVEPOINT) і перервана транзакція.

Сценарій виконується на PostgreSQL у двох сеансах; перевіряється те, що сталося: помилки, стани транзакцій, значення, які бачить сеанс B.

Повний набір перевірок (інші значення й граничні випадки) є лише у викладача.
"""

import pytest
from conftest import load
from harness import call, run_scenario_once, trace_check, trace_of, stock_of


M = load(3)


NAME = "scenario"


def trace():
    return trace_of(M, NAME)


def a_commit(t):
    return next((s for s in t.of("A") if s.status == "COMMIT"), None)


def test_function_exists():
    assert callable(getattr(M, NAME, None)), "немає функції scenario()"


def test_check_violation_in_a():
    t = trace()
    errs = [s for s in t.of("A") if s.err == "23514"]
    trace_check(t, errs, "У сеансі A має статися помилка 23514 (порушення CHECK: залишок не може стати від'ємним)")


def test_final_stock():
    t = trace()
    got = (stock_of(t, 1), stock_of(t, 2), stock_of(t, 3))
    trace_check(t, got == (20, 12, 8), f"Після сценарію залишки товарів 1, 2, 3 мають бути (20, 12, 8), а є {got}")
