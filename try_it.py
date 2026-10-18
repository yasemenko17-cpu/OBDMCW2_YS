"""Ручний прогін вашого завдання без тестів.

Використання:  python try_it.py <номер_завдання>

* завдання 1, 2, 5, 9: виконує ваш запит на даних магазину й друкує рядки результату;
* завдання 6: виконує вашу команду на даних магазину й друкує вміст таблиць purchase, purchase_archive, archive_log;
* завдання 3, 7: виконує сценарій у двох сеансах A і B та друкує, що відбулося на кроках (результат, помилка, очікування,
  стан транзакції, рівень ізоляції) і стан таблиць;
* завдання 4, 8, 10: створює таблицю sale_log, виконує ваш скрипт, друкує створені індекси й плани EXPLAIN запитів завдання.

Усе відбувається в тимчасовій схемі, яку програма видаляє наприкінці.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tests"))

import pytest  # noqa: E402

import harness  # noqa: E402
import pgutil  # noqa: E402
from conftest import load  # noqa: E402

PLAN_QUERIES = {
    4: ["SELECT * FROM sale_log WHERE customer_id = 777",
        "SELECT * FROM sale_log WHERE sold_on = DATE '2025-03-15'"],
    8: ["SELECT * FROM sale_log WHERE status = 'new' AND sold_on < DATE '2025-03-01'",
        "SELECT * FROM sale_log WHERE lower(email) = 'client777@example.com'"],
    10: ["SELECT id, amount FROM sale_log WHERE customer_id = 777 AND sold_on >= DATE '2025-06-01' ORDER BY sold_on",
         "SELECT sold_on, amount FROM sale_log WHERE product_id = 17 AND sold_on BETWEEN DATE '2026-05-01' AND DATE '2026-05-31'",
         "SELECT * FROM sale_log WHERE status = 'new' ORDER BY sold_on DESC LIMIT 5"],
}
SCENARIOS = {3: ["scenario"], 7: ["scenario_read_committed", "scenario_repeatable_read"]}


def show_rows(rows, limit=40):
    for row in rows[:limit]:
        print("  ", row)
    if len(rows) > limit:
        print(f"   ... ще рядків: {len(rows) - limit}")
    print(f"Усього рядків: {len(rows)}")


def main():
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        print(__doc__)
        return 1
    task = int(sys.argv[1])
    mod = load(task)
    db = pgutil.Db()
    try:
        if task in (1, 2, 5, 9):
            db.run(harness.SHOP)
            sql = harness.clean_query(harness.call(mod, "query"))
            ncols, rows = harness.run_query(db, sql)
            print(f"Стовпців: {ncols}")
            show_rows(rows)
        elif task == 6:
            db.run(harness.SHOP)
            sql = harness.need_text(harness.call(mod, "statement"), "statement()")
            db.run(sql)
            for table, order in (("purchase", "id"), ("purchase_archive", "id"), ("archive_log", "id")):
                print(f"-- {table}")
                show_rows(db.rows(f"SELECT * FROM {table} ORDER BY {order}"))
        elif task in SCENARIOS:
            for name in SCENARIOS[task]:
                print(f"=== {name}()")
                trace = harness.run_scenario_once(mod, name)
                print(trace.table(60))
                print("Стан після сценарію:", trace.final.get("product"), "| транзакції:", trace.end_txn)
        else:
            case = harness.IndexCase(db, mod)
            print("Створені індекси:")
            for idx in case.new_indexes():
                print("  ", idx["def"], f"({idx['size']} байт)")
            for sql in PLAN_QUERIES[task]:
                print("\n" + sql)
                print(harness.plan_text(case.plan(sql)))
    except pytest.fail.Exception as error:
        print("Зупинка:", error)
        return 1
    except pgutil.ScriptError as error:
        print("Помилка SQL:", error)
        return 1
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
