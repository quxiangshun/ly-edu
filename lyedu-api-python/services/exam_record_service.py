# -*- coding: utf-8 -*-
"""考试记录服务，与 Java ExamRecordService 对应"""
import json
from typing import Any, List, Optional

import db
from services import exam_service
from services import paper_service

SELECT_COLS = "id, exam_id, user_id, paper_id, score, passed, answers, submit_time, create_time"


def _row_to_record(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "examId": row.get("exam_id"),
        "userId": row.get("user_id"),
        "paperId": row.get("paper_id"),
        "score": row.get("score"),
        "passed": row.get("passed"),
        "answers": row.get("answers"),
        "submitTime": row.get("submit_time"),
        "createTime": row.get("create_time"),
    }


def submit(exam_id: int, user_id: int, answers_json: Optional[str]) -> Optional[dict]:
    exam = exam_service.get_by_id_ignore_visibility(exam_id)
    if not exam:
        return None
    paper = paper_service.get_by_id(exam.get("paperId"))
    if not paper:
        return None
    items = paper_service.list_questions_by_paper_id(exam.get("paperId"))
    if not items:
        return None

    try:
        user_answers = json.loads(answers_json or "{}") if answers_json else {}
    except Exception:
        user_answers = {}

    pass_score = exam.get("passScore") if exam.get("passScore") is not None else paper.get("passScore", 60)
    total_score = 0
    for item in items:
        score = item.get("score", 10)
        q = item.get("question")
        if not q:
            continue
        correct = (q.get("answer") or "").strip().upper()
        user = (user_answers.get(str(q.get("id")), "") or "").strip().upper()
        if correct == user:
            total_score += score
    passed = 1 if total_score >= pass_score else 0

    sql = "INSERT INTO ly_exam_record (exam_id, user_id, paper_id, score, passed, answers, submit_time) VALUES (%s, %s, %s, %s, %s, %s, NOW())"
    db.execute(sql, (exam_id, user_id, paper.get("id"), total_score, passed, answers_json))
    if passed == 1:
        user_certificate_service.issue_if_eligible("exam", exam_id, user_id)
    row = db.query_one("SELECT LAST_INSERT_ID() AS id", ())
    rid = row.get("id") if row else None
    if not rid:
        return None
    r = {
        "id": rid,
        "examId": exam_id,
        "userId": user_id,
        "paperId": paper.get("id"),
        "score": total_score,
        "passed": passed,
        "answers": answers_json,
        "submitTime": None,
        "createTime": None,
    }
    return r


def list_by_exam_id(exam_id: int) -> List[dict]:
    if not exam_id:
        return []
    sql = "SELECT " + SELECT_COLS + " FROM ly_exam_record WHERE exam_id = %s ORDER BY submit_time DESC"
    rows = db.query_all(sql, (exam_id,))
    return [_row_to_record(r) for r in (rows or [])]


def list_by_user_id(user_id: int) -> List[dict]:
    if not user_id:
        return []
    sql = "SELECT " + SELECT_COLS + " FROM ly_exam_record WHERE user_id = %s ORDER BY submit_time DESC"
    rows = db.query_all(sql, (user_id,))
    return [_row_to_record(r) for r in (rows or [])]


def get_by_exam_and_user(exam_id: int, user_id: int) -> Optional[dict]:
    if not exam_id or not user_id:
        return None
    sql = "SELECT " + SELECT_COLS + " FROM ly_exam_record WHERE exam_id = %s AND user_id = %s ORDER BY id DESC LIMIT 1"
    row = db.query_one(sql, (exam_id, user_id))
    return _row_to_record(row) if row else None
