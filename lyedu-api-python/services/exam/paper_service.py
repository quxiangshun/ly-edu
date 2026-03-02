# -*- coding: utf-8 -*-
"""试卷服务，与 Java PaperService 对应"""
from typing import Any, Dict, List, Optional

import pymysql

import db
from models.schemas import page_result
from services.exam import question_service
from util import redis_cache

PAPER_COLS = "id, title, total_score, pass_score, duration_minutes, status, create_time, update_time, deleted"

# 试卷名称缓存 TTL（秒），便于列表/下拉等读多写少场景
PAPER_TITLE_CACHE_TTL = 300


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
    try:
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
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:
            return page_result([], 0, page_num, size)
        raise


def get_by_id(paper_id: int) -> Optional[dict]:
    try:
        sql = "SELECT " + PAPER_COLS + " FROM ly_paper WHERE id = %s AND deleted = 0"
        row = db.query_one(sql, (paper_id,))
        return _row_to_paper(row) if row else None
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:
            return None
        raise


def get_titles_by_ids(paper_ids: List[int]) -> Dict[int, Optional[str]]:
    """批量查询试卷 id -> title，用于列表展示；先读 Redis 缓存，未命中再查库并回填缓存"""
    if not paper_ids:
        return {}
    ids = list(dict.fromkeys(paper_ids))
    result: Dict[int, Optional[str]] = {}
    miss_ids: List[int] = []
    for pid in ids:
        cached = redis_cache.get("paper:title:%s" % pid)
        if cached is not None:
            result[pid] = cached if cached else None
        else:
            miss_ids.append(pid)
    if not miss_ids:
        return result
    try:
        placeholders = ", ".join(["%s"] * len(miss_ids))
        sql = "SELECT id, title FROM ly_paper WHERE id IN (" + placeholders + ") AND deleted = 0"
        rows = db.query_all(sql, tuple(miss_ids))
        for r in (rows or []):
            pid = r["id"]
            title = r.get("title")
            result[pid] = title
            redis_cache.set("paper:title:%s" % pid, title or "", PAPER_TITLE_CACHE_TTL)
        for pid in miss_ids:
            if pid not in result:
                result[pid] = None
                redis_cache.set("paper:title:%s" % pid, "", PAPER_TITLE_CACHE_TTL)
        return result
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:
            for pid in miss_ids:
                result[pid] = None
            return result
        raise


def list_questions_by_paper_id(paper_id: int) -> List[dict]:
    if not paper_id:
        return []
    try:
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
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:
            return []
        raise


def _resolve_question_id_and_score_sort(cur, item: dict, sort_index: int) -> Optional[tuple]:
    """
    解析题目项：若为已有题目（含 questionId）返回 (question_id, score, sort)；
    若为新建题目（含 type, title）则先插入试题再返回 (new_id, score, sort)。
    返回 None 表示该项无效跳过。
    """
    qid = item.get("questionId")
    if qid is not None:
        return (int(qid), item.get("score", 10), item.get("sort", sort_index))
    # 新建试题：需含 type、title
    type_ = (item.get("type") or "").strip()
    title = (item.get("title") or "").strip()
    if not type_ or not title:
        return None
    new_id = question_service.save_with_cursor(
        cur,
        type_=type_,
        title=title,
        options=item.get("options"),
        answer=item.get("answer"),
        score=item.get("score", 10),
        analysis=item.get("analysis"),
        sort=item.get("sort", 0),
    )
    if not new_id:
        return None
    return (new_id, item.get("score", 10), item.get("sort", sort_index))


def save(
    title: str,
    total_score: int = 100,
    pass_score: int = 60,
    duration_minutes: int = 60,
    status: int = 1,
    questions: Optional[List[dict]] = None,
) -> int:
    """创建试卷并关联题目，支持已有题目（questionId）与新建题目（type+title）。同一事务，任一步失败则全部回滚。"""
    try:
        with db.transaction() as cur:
            cur.execute(
                "INSERT INTO ly_paper (title, total_score, pass_score, duration_minutes, status) VALUES (%s, %s, %s, %s, %s)",
                (title, total_score, pass_score, duration_minutes, status),
            )
            pid = cur.lastrowid or 0
            if not pid:
                raise RuntimeError("insert paper failed")
            if questions:
                for sort_index, item in enumerate(questions):
                    resolved = _resolve_question_id_and_score_sort(cur, item, sort_index)
                    if resolved:
                        qid, score, sort_val = resolved
                        cur.execute(
                            "INSERT INTO ly_paper_question (paper_id, question_id, score, sort) VALUES (%s, %s, %s, %s)",
                            (pid, qid, score, sort_val),
                        )
            return pid
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:
            return 0
        raise


def update(
    paper_id: int,
    title: str,
    total_score: int = 100,
    pass_score: int = 60,
    duration_minutes: int = 60,
    status: int = 1,
    questions: Optional[List[dict]] = None,
) -> bool:
    """更新试卷及题目关联，支持已有题目与新建题目。同一事务，任一步失败则全部回滚（关联关系不会部分生效）。"""
    try:
        with db.transaction() as cur:
            cur.execute(
                "UPDATE ly_paper SET title = %s, total_score = %s, pass_score = %s, duration_minutes = %s, status = %s WHERE id = %s AND deleted = 0",
                (title, total_score, pass_score, duration_minutes, status, paper_id),
            )
            n = cur.rowcount
            if n <= 0:
                raise RuntimeError("paper not found or update failed")
            cur.execute("DELETE FROM ly_paper_question WHERE paper_id = %s", (paper_id,))
            if questions:
                for sort_index, item in enumerate(questions):
                    resolved = _resolve_question_id_and_score_sort(cur, item, sort_index)
                    if resolved:
                        qid, score, sort_val = resolved
                        cur.execute(
                            "INSERT INTO ly_paper_question (paper_id, question_id, score, sort) VALUES (%s, %s, %s, %s)",
                            (paper_id, qid, score, sort_val),
                        )
        redis_cache.delete("paper:title:%s" % paper_id)
        return True
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:
            return False
        raise


def delete(paper_id: int) -> bool:
    try:
        db.execute("DELETE FROM ly_paper_question WHERE paper_id = %s", (paper_id,))
        n = db.execute("UPDATE ly_paper SET deleted = 1 WHERE id = %s", (paper_id,))
        if n > 0:
            redis_cache.delete("paper:title:%s" % paper_id)
        return n > 0
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:
            return False
        raise
