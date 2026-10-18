"""Допоміжні засоби тестів: підключення до PostgreSQL, тимчасова схема, спроба виконання команд, читання каталогу.

Параметри підключення беруться зі змінних PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE
(у Codespaces їх задає devcontainer; локально за замовчуванням localhost:5432, користувач postgres).
"""
import os
import re
import uuid

import psycopg


def connect():
    return psycopg.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=int(os.environ.get("PGPORT", "5432")),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", "postgres"),
        dbname=os.environ.get("PGDATABASE", "postgres"),
        autocommit=True,
        connect_timeout=5,
    )


class ScriptError(Exception):
    """SQL-скрипт завершився помилкою."""

    def __init__(self, error):
        self.state = error.sqlstate
        super().__init__(f"{error.sqlstate}: {str(error).strip().splitlines()[0]}")


class Db:
    """З'єднання з окремою тимчасовою схемою: усі таблиці тесту створюються лише в ній."""

    def __init__(self):
        self.conn = connect()
        self.schema = "t_" + uuid.uuid4().hex[:10]
        self.conn.execute(f"CREATE SCHEMA {self.schema}")
        self.conn.execute(f"SET search_path = {self.schema}")

    def close(self):
        try:
            self.conn.execute("ROLLBACK")
            self.conn.execute("SET search_path = public")
            self.conn.execute(f"DROP SCHEMA IF EXISTS {self.schema} CASCADE")
        finally:
            self.conn.close()

    def run(self, sql):
        """Виконує скрипт (кілька команд). Помилку перетворює на ScriptError."""
        try:
            self.conn.execute(sql)
        except psycopg.Error as error:
            raise ScriptError(error) from None

    def try_run(self, sql):
        """Виконує скрипт; повертає SQLSTATE помилки або порожній рядок. Незавершену транзакцію скасовує."""
        state = ""
        try:
            self.conn.execute(sql)
        except psycopg.Error as error:
            state = error.sqlstate or "?"
        self.conn.execute("ROLLBACK")
        return state

    def rows(self, sql, params=None):
        return self.conn.execute(sql, params).fetchall()

    def value(self, sql, params=None):
        row = self.conn.execute(sql, params).fetchone()
        return row[0] if row else None


def canon(type_name):
    """Приводить запис типу до вигляду, який повертає format_type()."""
    t = re.sub(r"\s+", " ", type_name.strip().lower())
    t = re.sub(r"^varchar\b", "character varying", t)
    t = re.sub(r"^char\b", "character", t)
    t = {"int": "integer", "int4": "integer", "int8": "bigint", "int2": "smallint", "bool": "boolean"}.get(t, t)
    return t


def columns(db, table):
    """{ім'я: {type, notnull, identity, default}} у порядку створення; порожній словник, якщо таблиці немає."""
    rows = db.rows(
        """SELECT a.attname, format_type(a.atttypid, a.atttypmod), a.attnotnull, a.attidentity,
                  pg_get_expr(d.adbin, d.adrelid)
           FROM pg_attribute a LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
           WHERE a.attrelid = to_regclass(%s) AND a.attnum > 0 AND NOT a.attisdropped ORDER BY a.attnum""",
        (table,))
    return {r[0]: {"type": r[1], "notnull": r[2], "identity": r[3], "default": r[4]} for r in rows}


def constraints(db, table):
    """Обмеження таблиці (p, f, u, c): список словників {name, type, cols, ref, refcols, on_delete, def}."""
    rows = db.rows(
        """SELECT c.conname, c.contype,
                  ARRAY(SELECT a.attname FROM unnest(c.conkey) WITH ORDINALITY k(n, o)
                        JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = k.n ORDER BY k.o),
                  (SELECT relname FROM pg_class WHERE oid = c.confrelid),
                  ARRAY(SELECT a.attname FROM unnest(c.confkey) WITH ORDINALITY k(n, o)
                        JOIN pg_attribute a ON a.attrelid = c.confrelid AND a.attnum = k.n ORDER BY k.o),
                  c.confdeltype, pg_get_constraintdef(c.oid)
           FROM pg_constraint c
           WHERE c.conrelid = to_regclass(%s) AND c.contype IN ('p', 'f', 'u', 'c') ORDER BY c.conname""",
        (table,))
    keys = ("name", "type", "cols", "ref", "refcols", "on_delete", "def")
    return [dict(zip(keys, r)) for r in rows]


def attempt(db, statements):
    """Виконує команди в транзакції, яку завжди скасовують. Повертає SQLSTATE помилки або порожній рядок."""
    if isinstance(statements, str):
        statements = [statements]
    state = ""
    db.conn.execute("BEGIN")
    try:
        for sql in statements:
            db.conn.execute(sql)
    except psycopg.Error as error:
        state = error.sqlstate or "?"
    finally:
        db.conn.execute("ROLLBACK")
    return state
