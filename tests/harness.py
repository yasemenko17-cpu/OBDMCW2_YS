"""Спільні засоби перевірок: запуск запитів, команд, сценаріїв двох сеансів і читання планів EXPLAIN."""
import re
from datetime import date, datetime
from decimal import Decimal

import pytest

import pgutil
import txsim
from schemas import SALE_LOG, SHOP, TX


def fail(message):
    pytest.fail(message, pytrace=False)


# ----------------------------------------------------------------------------------------------
# Загальне: виклик функції студента, перевірка тексту SQL
# ----------------------------------------------------------------------------------------------
def call(mod, name):
    """Викликає функцію name з файла завдання; заглушку NotImplementedError перетворює на зрозумілу невдачу."""
    fn = getattr(mod, name, None)
    if fn is None:
        fail(f"У файлі завдання немає функції {name}()")
    try:
        return fn()
    except NotImplementedError:
        fail(f"Функцію {name}() ще не реалізовано (NotImplementedError)")


def strip_sql(text):
    """Текст SQL без коментарів і рядкових літералів: для пошуку ключових слів."""
    text = re.sub(r"--[^\n]*", " ", text)
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"'(?:[^']|'')*'", "''", text)


def split_statements(text):
    """Розбиває скрипт на команди за «;» поза рядковими літералами й коментарями."""
    body = strip_sql(text)
    parts = [p.strip() for p in body.split(";")]
    return [p for p in parts if p]


def need_text(value, what):
    if not isinstance(value, str) or not value.strip():
        fail(f"{what} має повертати непорожній рядок з текстом SQL")
    return value.strip()


def has_keyword(sql, pattern):
    return re.search(pattern, strip_sql(sql), re.I) is not None


# ----------------------------------------------------------------------------------------------
# Запити SELECT і порівняння результату
# ----------------------------------------------------------------------------------------------
def norm(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, Decimal)):
        text = format(Decimal(str(value)).normalize(), "f")
        return "0" if text in ("-0", "") else text
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def norm_rows(rows):
    return [tuple(norm(v) for v in row) for row in rows]


def clean_query(value):
    text = need_text(value, "query()")
    while text.endswith(";"):
        text = text[:-1].rstrip()
    if ";" in strip_sql(text):
        fail("query() має повертати рівно один запит: приберіть зайві «;» і додаткові команди")
    if not re.match(r"(?is)^\s*(select|with|values|table)\b", text):
        fail("Запит має починатися зі SELECT (або WITH); змінювати дані й схему не можна")
    return text


def run_query(db, sql):
    db.conn.execute("SET default_transaction_read_only = on")
    db.conn.execute("SET statement_timeout = 10000")
    try:
        cur = db.conn.execute(sql)
        rows = cur.fetchall()
        return len(cur.description), rows
    except pgutil.psycopg.errors.QueryCanceled:
        fail("Запит виконується понад 10 секунд: схоже на декартів добуток (забута умова з'єднання?)")
    except pgutil.psycopg.Error as error:
        fail("Помилка SQL " + f"{error.sqlstate}: {str(error).strip().splitlines()[0]}")
    finally:
        db.conn.execute("SET default_transaction_read_only = off")


def compare_rows(got, want, label, note=""):
    got, want = norm_rows(got), norm_rows(want)
    if got == want:
        return
    lines = [f"Перевірка «{label}»: очікувалось рядків {len(want)}, отримано {len(got)}."]
    if sorted(got, key=repr) == sorted(want, key=repr):
        lines.append("Набір рядків правильний, але порядок інший: перевірте ORDER BY.")
    else:
        missing = [r for r in want if r not in got]
        extra = [r for r in got if r not in want]
        if missing:
            lines.append("Бракує: " + "; ".join(map(str, missing[:3])) + (" ..." if len(missing) > 3 else ""))
        if extra:
            lines.append("Зайві або інші: " + "; ".join(map(str, extra[:3])) + (" ..." if len(extra) > 3 else ""))
        if not missing and not extra:
            lines.append("Рядки повторюються: перевірте розмноження після JOIN або потрібність DISTINCT.")
    for pos, (a, b) in enumerate(zip(got, want), 1):
        if a != b:
            lines.append(f"Перший розбіг на рядку {pos}: отримано {a}, очікувалось {b}.")
            break
    if note:
        lines.append("Цей тест додатково змінює дані: " + note)
    fail("\n".join(lines))


def run_query_case(db, mod, case, columns, column_list):
    """Один тест запиту: схема магазину, зміни даних випадку, запит студента, порівняння з очікуваним."""
    db.run(SHOP)
    for sql in case["setup"]:
        db.run(sql)
    sql = clean_query(call(mod, "query"))
    ncols, rows = run_query(db, sql)
    if ncols != columns:
        fail(f"Очікувалось стовпців {columns}, запит повернув {ncols}. Потрібні стовпці по порядку: {column_list}")
    compare_rows(rows, case["expect"], case["id"], case["note"])


# ----------------------------------------------------------------------------------------------
# Сценарії двох сеансів
# ----------------------------------------------------------------------------------------------
def run_scenario_once(mod, name):
    steps = call(mod, name)
    try:
        db = pgutil.Db()
    except Exception as error:  # noqa: BLE001
        fail("Немає підключення до PostgreSQL (" + str(error).strip().splitlines()[0] + "). Запустіть сервер і перевірте "
             "змінні PGHOST, PGPORT, PGUSER, PGPASSWORD (див. README.md).")
    try:
        db.run(TX)
        return txsim.run_scenario(db.schema, steps)
    except txsim.ScenarioError as error:
        fail(str(error))
    finally:
        db.close()


_TRACES = {}


def trace_of(mod, name):
    key = (getattr(mod, "__file__", id(mod)), name)
    if key not in _TRACES:
        _TRACES[key] = run_scenario_once(mod, name)
    return _TRACES[key]


def trace_fail(trace, message):
    fail(message + "\nЩо сталося у вашому сценарії:\n" + trace.table(16))


def trace_check(trace, condition, message):
    if not condition:
        trace_fail(trace, message)


def stock_of(trace, product_id):
    for row in trace.final.get("product", []):
        if row[0] == product_id:
            return row[2]
    return None


# ----------------------------------------------------------------------------------------------
# Індекси й плани
# ----------------------------------------------------------------------------------------------
PLAN_SETTINGS = (
    "SET max_parallel_workers_per_gather = 0",
    "SET jit = off",
    "SET seq_page_cost = 1",
    "SET random_page_cost = 1.1",
    "SET effective_cache_size = '1GB'",
    "SET work_mem = '4MB'",
)


class IndexCase:
    """Таблиця sale_log, скрипт студента з індексами, VACUUM ANALYZE і зафіксовані параметри планувальника."""

    def __init__(self, db, mod):
        self.db = db
        db.run(SALE_LOG)
        script = need_text(call(mod, "indexes"), "indexes()")
        bad = [s for s in split_statements(script) if not re.match(r"(?i)^create\s+index\b", s)]
        if bad:
            fail("Скрипт має містити лише команди CREATE INDEX; знайдено: " + bad[0][:60])
        db.run(script)
        db.run("VACUUM ANALYZE sale_log")
        for sql in PLAN_SETTINGS:
            db.run(sql)
        self.script = script

    def new_indexes(self):
        rows = self.db.rows(
            """SELECT c.relname, pg_get_indexdef(i.indexrelid), i.indpred IS NOT NULL, i.indexprs IS NOT NULL,
                      pg_relation_size(i.indexrelid), pg_get_expr(i.indpred, i.indrelid), i.indisvalid
               FROM pg_index i JOIN pg_class c ON c.oid = i.indexrelid
               WHERE i.indrelid = to_regclass('sale_log') AND NOT i.indisprimary ORDER BY c.relname""")
        keys = ("name", "def", "partial", "expr", "size", "pred", "valid")
        return [dict(zip(keys, r)) for r in rows]

    def plan(self, sql):
        row = self.db.conn.execute("EXPLAIN (FORMAT JSON) " + sql).fetchone()[0]
        return row[0]["Plan"]


def walk(plan):
    """Усі вузли плану в порядку обходу (спочатку батьківський)."""
    yield plan
    for child in plan.get("Plans", []):
        yield from walk(child)


def node_types(plan):
    return [n["Node Type"] for n in walk(plan)]


def index_names(plan):
    return [n["Index Name"] for n in walk(plan) if "Index Name" in n]


def has_backward_scan(plan):
    """Чи є в плані індексне сканування в зворотному напрямку (у JSON: Node Type = Index Scan, Scan Direction = Backward)."""
    return any(n["Node Type"] in ("Index Scan", "Index Only Scan") and n.get("Scan Direction") == "Backward" for n in walk(plan))


def plan_text(plan):
    """Короткий опис плану для повідомлень: тип вузла, таблиця, індекс."""
    out = []

    def rec(node, depth):
        line = "  " * depth + node["Node Type"]
        if node.get("Scan Direction") == "Backward":
            line += " Backward"
        if "Relation Name" in node:
            line += " on " + node["Relation Name"]
        if "Index Name" in node:
            line += " using " + node["Index Name"]
        line += f" (cost={node['Total Cost']:.2f})"
        out.append(line)
        for child in node.get("Plans", []):
            rec(child, depth + 1)

    rec(plan, 1)
    return "\n".join(out)


def plan_fail(plan, message):
    fail(message + "\nПлан запиту:\n" + plan_text(plan))


# ----------------------------------------------------------------------------------------------
# Команда зміни даних (завдання 6): стан таблиць після виконання
# ----------------------------------------------------------------------------------------------
def run_statement_case(db, mod, case):
    db.run(SHOP)
    for sql in case["setup"]:
        db.run(sql)
    sql = need_text(call(mod, "statement"), "statement()")
    if len(split_statements(sql)) != 1:
        fail("statement() має повертати рівно одну команду SQL (без «;» посередині): оператор має бути атомарним")
    state = ""
    try:
        db.conn.execute(sql)
    except pgutil.psycopg.Error as error:
        state = error.sqlstate or "?"
        message = str(error).strip().splitlines()[0]
    if case["error"] and state != case["error"]:
        fail(f"Перевірка «{case['id']}»: очікувалась помилка {case['error']} (дублікат ключа в архіві) і повне скасування "
             f"оператора, а отримано " + (f"помилку {state}" if state else "успішне виконання") + ".")
    if state and not case["error"]:
        fail(f"Перевірка «{case['id']}»: помилка SQL {state}: {message}")
    got = {
        "purchase": db.rows("SELECT id, customer_id, product_id, quantity, ordered_on, shipped_on FROM purchase ORDER BY id"),
        "purchase_archive": db.rows("SELECT id, customer_id, product_id, quantity, ordered_on, shipped_on "
                                    "FROM purchase_archive ORDER BY id"),
        "archive_log": db.rows("SELECT id, moved FROM archive_log ORDER BY id"),
    }
    names = {"purchase": "purchase (залишок)", "purchase_archive": "purchase_archive", "archive_log": "archive_log (id, moved)"}
    for table in ("purchase", "purchase_archive", "archive_log"):
        a, b = norm_rows(got[table]), norm_rows(case["expect"][table])
        if a != b:
            lines = [f"Перевірка «{case['id']}»: таблиця {names[table]} має інший вміст: очікувалось рядків {len(b)}, отримано {len(a)}."]
            missing = [r for r in b if r not in a]
            extra = [r for r in a if r not in b]
            if missing:
                lines.append("Бракує: " + "; ".join(map(str, missing[:3])))
            if extra:
                lines.append("Зайві: " + "; ".join(map(str, extra[:3])))
            if case["note"]:
                lines.append("Цей тест додатково змінює дані: " + case["note"])
            fail("\n".join(lines))
