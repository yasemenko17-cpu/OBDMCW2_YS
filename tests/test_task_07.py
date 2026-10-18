"""Відкриті тести завдання 07: конкурентне зменшення залишку на READ COMMITTED і REPEATABLE READ.
Повний набір перевірок (інші значення й граничні випадки) є лише у викладача.
"""

import pytest
from conftest import load
from harness import call, run_scenario_once, trace_check, trace_of, stock_of


M = load(7)


def blocked_b_update(t):
    return next((s for s in t.of("B") if s.blocked and s.sql.lower().startswith("update")), None)


def commit_ok(t, sess):
    return [s for s in t.of(sess) if s.status == "COMMIT" and s.err is None]


RC = "scenario_read_committed"


def test_functions_exist():
    assert callable(getattr(M, RC, None)), "немає функції scenario_read_committed()"
    assert callable(getattr(M, "scenario_repeatable_read", None)), "немає функції scenario_repeatable_read()"


def test_rc_second_update_waits():
    t = trace_of(M, RC)
    trace_check(t, blocked_b_update(t) is not None, "UPDATE сеансу B має чекати блокування, поки A не зафіксував свою зміну (A: UPDATE, B: UPDATE, лише потім COMMIT A)")


def test_rc_final_stock_and_no_errors():
    t = trace_of(M, RC)
    trace_check(t, not t.errors(), "У цьому сценарії не повинно бути помилок")
    trace_check(t, stock_of(t, 3) == 3, f"Залишок товару 3 після сценарію має бути 3, а є {stock_of(t, 3)}")


RR = "scenario_repeatable_read"


def test_rr_conflict_error_40001():
    t = trace_of(M, RR)
    s = blocked_b_update(t)
    trace_check(t, s is not None, "UPDATE сеансу B має чекати блокування")
    trace_check(t, s.err == "40001", f"Після COMMIT сеансу A оператор B має завершитися помилкою 40001, а є {s.err or s.status}")
    trace_check(t, s.txn == "INERROR", "Після помилки транзакція B має бути у стані INERROR")
