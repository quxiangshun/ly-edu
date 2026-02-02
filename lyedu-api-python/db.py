# -*- coding: utf-8 -*-
"""MySQL 连接，与 Java JdbcTemplate 对应（使用 PyMySQL）"""
from contextlib import contextmanager
from typing import Any, Generator, List, Optional, Tuple

import pymysql
from pymysql.cursors import DictCursor

import config


def get_connection():
    return pymysql.connect(
        host=config.MYSQL_HOST,
        port=config.MYSQL_PORT,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE,
        charset=config.MYSQL_CHARSET,
        cursorclass=DictCursor,
    )


@contextmanager
def cursor() -> Generator:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def query_one(sql: str, args: Tuple = ()) -> Optional[dict]:
    with cursor() as cur:
        cur.execute(sql, args or ())
        return cur.fetchone()


def query_all(sql: str, args: Tuple = ()) -> List[dict]:
    with cursor() as cur:
        cur.execute(sql, args or ())
        return cur.fetchall()


def execute(sql: str, args: Tuple = ()) -> int:
    with cursor() as cur:
        cur.execute(sql, args or ())
        return cur.rowcount


def execute_many(sql: str, args_list: List[Tuple]) -> int:
    with cursor() as cur:
        cur.executemany(sql, args_list)
        return cur.rowcount


def execute_insert(sql: str, args: Tuple = ()) -> int:
    """Execute INSERT and return last row id."""
    with cursor() as cur:
        cur.execute(sql, args or ())
        return cur.lastrowid or 0
