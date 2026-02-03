# -*- coding: utf-8 -*-
"""试题服务，与 Java QuestionService 对应"""
from typing import Any, List, Optional

import db
from models.schemas import page_result

SELECT_COLS = "id, type, title, options, answer, score, analysis, sort, create_time, update_time, deleted"


def _row_to_question(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "type": row.get("type"),
        "title": row.get("title"),
        "options": row.get("options"),
        "answer": row.get("answer"),
        "score": row.get("score", 10),
        "analysis": row.get("analysis"),
        "sort": row.get("sort", 0),
        "createTime": row.get("create_time"),
        "updateTime": row.get("update_time"),
        "deleted": row.get("deleted"),
    }


def page(
    page_num: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    type_: Optional[str] = None,
) -> dict:
    offset = (page_num - 1) * size
    where = ["deleted = 0"]
    params: List[Any] = []
    if keyword and keyword.strip():
        where.append("title LIKE %s")
        params.append("%" + keyword.strip() + "%")
    if type_ and type_.strip():
        where.append("type = %s")
        params.append(type_.strip())
    where_sql = " AND ".join(where)
    count_sql = "SELECT COUNT(*) AS total FROM ly_question WHERE " + where_sql
    total_row = db.query_one(count_sql, tuple(params))
    total = total_row.get("total", 0) or 0
    query_sql = "SELECT " + SELECT_COLS + " FROM ly_question WHERE " + where_sql + " ORDER BY sort ASC, id DESC LIMIT %s OFFSET %s"
    query_params = list(params) + [size, offset]
    rows = db.query_all(query_sql, tuple(query_params))
    records = [_row_to_question(r) for r in (rows or [])]
    return page_result(records, total, page_num, size)


def get_by_id(question_id: int) -> Optional[dict]:
    sql = "SELECT " + SELECT_COLS + " FROM ly_question WHERE id = %s AND deleted = 0"
    row = db.query_one(sql, (question_id,))
    return _row_to_question(row) if row else None


def save(
    type_: str,
    title: str,
    options: Optional[str] = None,
    answer: Optional[str] = None,
    score: int = 10,
    analysis: Optional[str] = None,
    sort: int = 0,
) -> int:
    sql = "INSERT INTO ly_question (type, title, options, answer, score, analysis, sort) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    return db.execute_insert(sql, (type_, title, options, answer, score, analysis, sort))


def update(
    question_id: int,
    type_: str,
    title: str,
    options: Optional[str] = None,
    answer: Optional[str] = None,
    score: int = 10,
    analysis: Optional[str] = None,
    sort: int = 0,
) -> bool:
    sql = "UPDATE ly_question SET type = %s, title = %s, options = %s, answer = %s, score = %s, analysis = %s, sort = %s WHERE id = %s AND deleted = 0"
    n = db.execute(sql, (type_, title, options, answer, score, analysis, sort, question_id))
    return n > 0


def delete(question_id: int) -> bool:
    n = db.execute("UPDATE ly_question SET deleted = 1 WHERE id = %s", (question_id,))
    return n > 0
