# -*- coding: utf-8 -*-
"""试卷服务，与 Java PaperService 对应"""
from typing import Any, List, Optional

import db
from models.schemas import page_result
from services import question_service

PAPER_COLS = "id, title, total_score, pass_score, duration_minutes, status, create_time, update_time, deleted"


def _row_to_paper(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "title": row.get("title"),
        "totalScore": row.get("total_score", 100),
        "passScore": row.get("pass_score", 60),
        "durationMinutes": row.get("duration_minutes", 60),
        "status": row.get("status", 1),
        "createTime": row.get("create_time"),
        "updateTime": row.get("update_time"),
        "deleted": row.get("deleted"),
    }


def page(page_num: int = 1, size: int = 20, keyword: Optional[str] = None) -> dict:
    offset = (page_num - 1) * size
    where = ["deleted = 0"]
    params: List[Any] = []
    if keyword and keyword.strip():
        where.append("title LIKE %s")
        params.append("%" + keyword.strip() + "%")
    where_sql = " AND ".join(where)
    count_sql = "SELECT COUNT(*) AS total FROM ly_paper WHERE " + where_sql
    total_row = db.query_one(count_sql, tuple(params))
    total = total_row.get("total", 0) or 0
    query_sql = "SELECT " + PAPER_COLS + " FROM ly_paper WHERE " + where_sql + " ORDER BY id DESC LIMIT %s OFFSET %s"
    query_params = list(params) + [size, offset]
    rows = db.query_all(query_sql, tuple(query_params))
    records = [_row_to_paper(r) for r in (rows or [])]
    return page_result(records, total, page_num, size)


def get_by_id(paper_id: int) -> Optional[dict]:
    sql = "SELECT " + PAPER_COLS + " FROM ly_paper WHERE id = %s AND deleted = 0"
    row = db.query_one(sql, (paper_id,))
    return _row_to_paper(row) if row else None


def list_questions_by_paper_id(paper_id: int) -> List[dict]:
    if not paper_id:
        return []
    sql = "SELECT question_id, score, sort FROM ly_paper_question WHERE paper_id = %s ORDER BY sort ASC, question_id ASC"
    rows = db.query_all(sql, (paper_id,))
    result = []
    for r in (rows or []):
        qid = r.get("question_id")
        q = question_service.get_by_id(qid) if qid else None
        result.append({
            "questionId": qid,
            "score": r.get("score", 10),
            "sort": r.get("sort", 0),
            "question": q,
        })
    return result


def save(
    title: str,
    total_score: int = 100,
    pass_score: int = 60,
    duration_minutes: int = 60,
    status: int = 1,
    questions: Optional[List[dict]] = None,
) -> int:
    sql = "INSERT INTO ly_paper (title, total_score, pass_score, duration_minutes, status) VALUES (%s, %s, %s, %s, %s)"
    pid = db.execute_insert(sql, (title, total_score, pass_score, duration_minutes, status))
    if pid and questions:
        for item in questions:
            qid = item.get("questionId")
            if qid is not None:
                db.execute(
                    "INSERT INTO ly_paper_question (paper_id, question_id, score, sort) VALUES (%s, %s, %s, %s)",
                    (pid, qid, item.get("score", 10), item.get("sort", 0)),
                )
    return pid or 0


def update(
    paper_id: int,
    title: str,
    total_score: int = 100,
    pass_score: int = 60,
    duration_minutes: int = 60,
    status: int = 1,
    questions: Optional[List[dict]] = None,
) -> bool:
    sql = "UPDATE ly_paper SET title = %s, total_score = %s, pass_score = %s, duration_minutes = %s, status = %s WHERE id = %s AND deleted = 0"
    n = db.execute(sql, (title, total_score, pass_score, duration_minutes, status, paper_id))
    db.execute("DELETE FROM ly_paper_question WHERE paper_id = %s", (paper_id,))
    if questions:
        for item in questions:
            qid = item.get("questionId")
            if qid is not None:
                db.execute(
                    "INSERT INTO ly_paper_question (paper_id, question_id, score, sort) VALUES (%s, %s, %s, %s)",
                    (paper_id, qid, item.get("score", 10), item.get("sort", 0)),
                )
    return n > 0


def delete(paper_id: int) -> bool:
    db.execute("DELETE FROM ly_paper_question WHERE paper_id = %s", (paper_id,))
    n = db.execute("UPDATE ly_paper SET deleted = 1 WHERE id = %s", (paper_id,))
    return n > 0
