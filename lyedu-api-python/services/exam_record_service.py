# -*- coding: utf-8 -*-
"""考试记录服务，与 Java ExamRecordService 对应"""
import json
from typing import Any, List, Optional

import db
from services import exam_service
from services import paper_service
from services import point_service
from services import user_certificate_service
from datetime import datetime

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
    row = db.query_one("SELECT LAST_INSERT_ID() AS id", ())
    rid = row.get("id") if row else None
    if passed == 1:
        user_certificate_service.issue_if_eligible("exam", exam_id, user_id)
        point_service.add_points(user_id, "exam_pass", "exam", exam_id)
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


def page(
    page_num: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    exam_id: Optional[int] = None,
    user_id: Optional[int] = None,
) -> dict:
    """分页查询考试记录（管理员）"""
    from common.result import page_result
    
    page_num = max(1, page_num)
    size = max(1, min(100, size))
    offset = (page_num - 1) * size
    
    where_clauses = []
    params: List[Any] = []
    
    if keyword:
        where_clauses.append("(u.real_name LIKE %s OR u.username LIKE %s OR e.title LIKE %s)")
        keyword_pattern = f"%{keyword}%"
        params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
    
    if exam_id:
        where_clauses.append("er.exam_id = %s")
        params.append(exam_id)
    
    if user_id:
        where_clauses.append("er.user_id = %s")
        params.append(user_id)
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # 查询总数
    count_sql = (
        f"SELECT COUNT(*) AS total FROM ly_exam_record er "
        f"LEFT JOIN ly_user u ON er.user_id = u.id AND u.deleted = 0 "
        f"LEFT JOIN ly_exam e ON er.exam_id = e.id AND e.deleted = 0 "
        f"WHERE {where_sql}"
    )
    total_row = db.query_one(count_sql, tuple(params))
    total = total_row.get("total") or 0 if total_row else 0
    
    # 查询数据
    data_sql = (
        f"SELECT er.id, er.exam_id AS examId, er.user_id AS userId, er.paper_id AS paperId, "
        f"er.score, er.passed, er.answers, er.submit_time AS submitTime, er.create_time AS createTime, "
        f"u.real_name AS realName, u.username, e.title AS examTitle "
        f"FROM ly_exam_record er "
        f"LEFT JOIN ly_user u ON er.user_id = u.id AND u.deleted = 0 "
        f"LEFT JOIN ly_exam e ON er.exam_id = e.id AND e.deleted = 0 "
        f"WHERE {where_sql} "
        f"ORDER BY er.submit_time DESC LIMIT %s OFFSET %s"
    )
    params.extend([size, offset])
    rows = db.query_all(data_sql, tuple(params))
    
    records = []
    for r in (rows or []):
        record = {
            "id": r.get("id"),
            "examId": r.get("examId"),
            "userId": r.get("userId"),
            "paperId": r.get("paperId"),
            "score": r.get("score"),
            "passed": r.get("passed"),
            "answers": r.get("answers"),
            "submitTime": r.get("submitTime"),
            "createTime": r.get("createTime"),
            "realName": r.get("realName"),
            "username": r.get("username"),
            "examTitle": r.get("examTitle"),
        }
        records.append(record)
    
    return page_result(records, total, page_num, size)
