# -*- coding: utf-8 -*-
"""数据统计与导出，与 Java StatsController 对应"""
import csv
import io
from typing import Any, List, Optional

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

import db
from common.result import success

router = APIRouter(prefix="/stats", tags=["stats"])


def _overview() -> dict:
    user_count = db.query_one("SELECT COUNT(*) AS c FROM ly_user WHERE deleted = 0", ()) or {}
    course_count = db.query_one("SELECT COUNT(*) AS c FROM ly_course WHERE deleted = 0", ()) or {}
    dept_count = db.query_one("SELECT COUNT(*) AS c FROM ly_department WHERE deleted = 0", ()) or {}
    video_count = db.query_one("SELECT COUNT(*) AS c FROM ly_video WHERE deleted = 0", ()) or {}
    return {
        "userCount": user_count.get("c") or 0,
        "courseCount": course_count.get("c") or 0,
        "departmentCount": dept_count.get("c") or 0,
        "videoCount": video_count.get("c") or 0,
    }


@router.get("/overview")
def overview():
    return success(_overview())


@router.get("/learning-rank")
def learning_rank(limit: int = 20):
    limit = max(1, min(100, limit))
    rows = db.query_all(
        "SELECT u.id AS userId, u.real_name AS realName, u.username, d.name AS departmentName, "
        "COUNT(uc.course_id) AS courseCount, COALESCE(SUM(uc.progress), 0) / GREATEST(COUNT(uc.course_id), 1) AS avgProgress "
        "FROM ly_user u "
        "LEFT JOIN ly_department d ON u.department_id = d.id AND d.deleted = 0 "
        "LEFT JOIN ly_user_course uc ON u.id = uc.user_id "
        "WHERE u.deleted = 0 "
        "GROUP BY u.id, u.real_name, u.username, d.name "
        "ORDER BY courseCount DESC, avgProgress DESC "
        "LIMIT %s",
        (limit,),
    )
    return success(rows)


@router.get("/resource")
def resource():
    c1 = db.query_one("SELECT COUNT(*) AS c FROM ly_course WHERE deleted = 0", ()) or {}
    c2 = db.query_one("SELECT COUNT(*) AS c FROM ly_video WHERE deleted = 0", ()) or {}
    c3 = db.query_one("SELECT COUNT(*) AS c FROM ly_course_chapter WHERE deleted = 0", ()) or {}
    c4 = db.query_one("SELECT COUNT(*) AS c FROM ly_course_attachment WHERE deleted = 0", ()) or {}
    return success({
        "courseCount": c1.get("c") or 0,
        "videoCount": c2.get("c") or 0,
        "chapterCount": c3.get("c") or 0,
        "attachmentCount": c4.get("c") or 0,
    })


def _rows_to_csv(headers: List[str], rows: List[dict]) -> bytes:
    buf = io.StringIO()
    buf.write("\uFEFF")
    w = csv.writer(buf)
    w.writerow(headers)
    for r in rows:
        w.writerow([r.get(h) if r.get(h) is not None else "" for h in headers])
    return buf.getvalue().encode("utf-8")


@router.get("/export/learners")
def export_learners_json():
    rows = db.query_all(
        "SELECT u.id, u.username, u.real_name AS realName, u.email, u.mobile, u.role, u.status, "
        "d.name AS departmentName, u.create_time AS createTime "
        "FROM ly_user u LEFT JOIN ly_department d ON u.department_id = d.id AND d.deleted = 0 "
        "WHERE u.deleted = 0 ORDER BY u.id"
    )
    return success(rows)


@router.get("/export/learners.csv")
def export_learners_csv():
    rows = db.query_all(
        "SELECT u.id, u.username, u.real_name AS realName, u.email, u.mobile, u.role, u.status, "
        "d.name AS departmentName, u.create_time AS createTime "
        "FROM ly_user u LEFT JOIN ly_department d ON u.department_id = d.id AND d.deleted = 0 "
        "WHERE u.deleted = 0 ORDER BY u.id"
    )
    headers = ["id", "username", "realName", "email", "mobile", "role", "status", "departmentName", "createTime"]
    csv_bytes = _rows_to_csv(headers, rows)
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=learners.csv"},
    )


@router.get("/learning/page")
def learning_page(page: int = 1, size: int = 20, keyword: Optional[str] = None, userId: Optional[int] = None, courseId: Optional[int] = None):
    """分页查询学习记录"""
    page = max(1, page)
    size = max(1, min(100, size))
    offset = (page - 1) * size
    
    where_clauses = ["uc.user_id = u.id AND u.deleted = 0", "uc.course_id = c.id AND c.deleted = 0"]
    params = []
    
    if keyword:
        where_clauses.append("(u.real_name LIKE %s OR u.username LIKE %s OR c.title LIKE %s)")
        keyword_pattern = f"%{keyword}%"
        params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
    
    if userId:
        where_clauses.append("uc.user_id = %s")
        params.append(userId)
    
    if courseId:
        where_clauses.append("uc.course_id = %s")
        params.append(courseId)
    
    where_sql = " AND ".join(where_clauses)
    
    # 查询总数
    count_sql = f"SELECT COUNT(*) AS total FROM ly_user_course uc JOIN ly_user u ON uc.user_id = u.id JOIN ly_course c ON uc.course_id = c.id WHERE {where_sql}"
    total_row = db.query_one(count_sql, tuple(params))
    total = total_row.get("total") or 0 if total_row else 0
    
    # 查询数据
    data_sql = (
        f"SELECT uc.user_id AS userId, u.real_name AS realName, u.username, uc.course_id AS courseId, "
        f"c.title AS courseTitle, uc.progress, uc.status AS completeStatus, uc.create_time AS joinTime, uc.update_time AS updateTime "
        f"FROM ly_user_course uc "
        f"JOIN ly_user u ON uc.user_id = u.id "
        f"JOIN ly_course c ON uc.course_id = c.id "
        f"WHERE {where_sql} "
        f"ORDER BY uc.update_time DESC LIMIT %s OFFSET %s"
    )
    params.extend([size, offset])
    rows = db.query_all(data_sql, tuple(params))
    
    return success({
        "records": rows,
        "total": total
    })


@router.get("/export/learning")
def export_learning_json():
    rows = db.query_all(
        "SELECT uc.user_id AS userId, u.real_name AS realName, u.username, uc.course_id AS courseId, "
        "c.title AS courseTitle, uc.progress, uc.status AS completeStatus, uc.create_time AS joinTime, uc.update_time AS updateTime "
        "FROM ly_user_course uc "
        "JOIN ly_user u ON uc.user_id = u.id AND u.deleted = 0 "
        "JOIN ly_course c ON uc.course_id = c.id AND c.deleted = 0 ORDER BY uc.user_id, uc.course_id"
    )
    return success(rows)


@router.get("/export/learning.csv")
def export_learning_csv():
    rows = db.query_all(
        "SELECT uc.user_id AS userId, u.real_name AS realName, u.username, uc.course_id AS courseId, "
        "c.title AS courseTitle, uc.progress, uc.status AS completeStatus, uc.create_time AS joinTime, uc.update_time AS updateTime "
        "FROM ly_user_course uc "
        "JOIN ly_user u ON uc.user_id = u.id AND u.deleted = 0 "
        "JOIN ly_course c ON uc.course_id = c.id AND c.deleted = 0 ORDER BY uc.user_id, uc.course_id"
    )
    headers = ["userId", "realName", "username", "courseId", "courseTitle", "progress", "completeStatus", "joinTime", "updateTime"]
    csv_bytes = _rows_to_csv(headers, rows)
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=learning.csv"},
    )


@router.get("/export/department-learning")
def export_department_learning_json():
    rows = db.query_all(
        "SELECT d.id AS departmentId, d.name AS departmentName, "
        "COUNT(DISTINCT u.id) AS userCount, "
        "COUNT(DISTINCT CASE WHEN uc.progress >= 100 THEN uc.user_id ELSE NULL END) AS completedUserCount, "
        "COUNT(uc.id) AS learningRecordCount "
        "FROM ly_department d "
        "LEFT JOIN ly_user u ON u.department_id = d.id AND u.deleted = 0 "
        "LEFT JOIN ly_user_course uc ON uc.user_id = u.id "
        "WHERE d.deleted = 0 GROUP BY d.id, d.name ORDER BY d.sort, d.id"
    )
    return success(rows)


@router.get("/export/department-learning.csv")
def export_department_learning_csv():
    rows = db.query_all(
        "SELECT d.id AS departmentId, d.name AS departmentName, "
        "COUNT(DISTINCT u.id) AS userCount, "
        "COUNT(DISTINCT CASE WHEN uc.progress >= 100 THEN uc.user_id ELSE NULL END) AS completedUserCount, "
        "COUNT(uc.id) AS learningRecordCount "
        "FROM ly_department d "
        "LEFT JOIN ly_user u ON u.department_id = d.id AND u.deleted = 0 "
        "LEFT JOIN ly_user_course uc ON uc.user_id = u.id "
        "WHERE d.deleted = 0 GROUP BY d.id, d.name ORDER BY d.sort, d.id"
    )
    headers = ["departmentId", "departmentName", "userCount", "completedUserCount", "learningRecordCount"]
    csv_bytes = _rows_to_csv(headers, rows)
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=department-learning.csv"},
    )
