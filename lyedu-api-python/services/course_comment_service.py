# -*- coding: utf-8 -*-
"""课程评论服务，与 Java CourseCommentService 对应"""
from typing import Any, List, Optional

import db


def list_by_course(course_id: int, chapter_id: Optional[int] = None) -> List[dict]:
    if chapter_id is not None:
        rows = db.query_all(
            "SELECT c.id, c.course_id, c.chapter_id, c.user_id, c.parent_id, c.content, c.status, c.create_time, "
            "u.real_name AS user_real_name FROM ly_course_comment c "
            "LEFT JOIN ly_user u ON c.user_id = u.id AND u.deleted = 0 "
            "WHERE c.course_id = %s AND c.deleted = 0 AND (c.status IS NULL OR c.status = 1) "
            "AND (c.chapter_id IS NULL OR c.chapter_id = %s) ORDER BY c.id ASC",
            (course_id, chapter_id),
        )
    else:
        rows = db.query_all(
            "SELECT c.id, c.course_id, c.chapter_id, c.user_id, c.parent_id, c.content, c.status, c.create_time, "
            "u.real_name AS user_real_name FROM ly_course_comment c "
            "LEFT JOIN ly_user u ON c.user_id = u.id AND u.deleted = 0 "
            "WHERE c.course_id = %s AND c.deleted = 0 AND (c.status IS NULL OR c.status = 1) "
            "ORDER BY c.id ASC",
            (course_id,),
        )
    return [_row_to_dto(r) for r in rows]


def _row_to_dto(r: dict) -> dict:
    out = {
        "id": r["id"],
        "courseId": r["course_id"],
        "chapterId": r.get("chapter_id"),
        "userId": r["user_id"],
        "userRealName": r.get("user_real_name"),
        "parentId": r.get("parent_id"),
        "content": r.get("content") or "",
        "status": r.get("status") or 1,
        "createTime": r.get("create_time"),
    }
    if hasattr(out["createTime"], "isoformat"):
        out["createTime"] = out["createTime"].isoformat()
    return out


def add(
    course_id: int,
    user_id: int,
    content: str,
    chapter_id: Optional[int] = None,
    parent_id: Optional[int] = None,
) -> Optional[dict]:
    content = (content or "").strip()
    if not content:
        return None
    db.execute(
        "INSERT INTO ly_course_comment (course_id, chapter_id, user_id, parent_id, content, status) "
        "VALUES (%s, %s, %s, %s, %s, 1)",
        (course_id, chapter_id, user_id, parent_id, content),
    )
    row = db.query_one(
        "SELECT id, course_id, chapter_id, user_id, parent_id, content, status, create_time "
        "FROM ly_course_comment WHERE course_id = %s AND user_id = %s ORDER BY id DESC LIMIT 1",
        (course_id, user_id),
    )
    if not row:
        return None
    return {
        "id": row["id"],
        "courseId": row["course_id"],
        "chapterId": row.get("chapter_id"),
        "userId": row["user_id"],
        "parentId": row.get("parent_id"),
        "content": row["content"],
        "status": row.get("status") or 1,
        "createTime": row.get("create_time").isoformat() if row.get("create_time") else None,
    }


def delete(comment_id: int) -> int:
    """删除评论（假删除，管理员使用）"""
    return db.execute("UPDATE ly_course_comment SET deleted = 1 WHERE id = %s", (comment_id,))


def delete_by_user(comment_id: int, user_id: int) -> int:
    """用户删除自己的评论（假删除，只能删除自己的）"""
    return db.execute("UPDATE ly_course_comment SET deleted = 1 WHERE id = %s AND user_id = %s", (comment_id, user_id))


def update_status(comment_id: int, status: int) -> int:
    """更新评论状态（0-隐藏，1-显示）"""
    return db.execute("UPDATE ly_course_comment SET status = %s WHERE id = %s", (status, comment_id))


def get_by_id(comment_id: int) -> Optional[dict]:
    """获取评论详情（包含已删除和隐藏的，管理员使用）"""
    row = db.query_one(
        "SELECT c.id, c.course_id, c.chapter_id, c.user_id, c.parent_id, c.content, c.status, c.deleted, c.create_time, "
        "u.real_name AS user_real_name, u.username FROM ly_course_comment c "
        "LEFT JOIN ly_user u ON c.user_id = u.id "
        "WHERE c.id = %s",
        (comment_id,),
    )
    if not row:
        return None
    return {
        "id": row["id"],
        "courseId": row["course_id"],
        "chapterId": row.get("chapter_id"),
        "userId": row["user_id"],
        "userRealName": row.get("user_real_name"),
        "username": row.get("username"),
        "parentId": row.get("parent_id"),
        "content": row.get("content") or "",
        "status": row.get("status") or 1,
        "deleted": row.get("deleted") or 0,
        "createTime": row.get("create_time").isoformat() if row.get("create_time") else None,
    }


def page(
    page_num: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    course_id: Optional[int] = None,
    status: Optional[int] = None,
) -> dict:
    """分页查询评论（管理员使用，包含已删除和隐藏的）"""
    where_parts = []
    params = []
    if keyword:
        where_parts.append("(c.content LIKE %s OR u.real_name LIKE %s OR u.username LIKE %s)")
        kw = f"%{keyword}%"
        params.extend([kw, kw, kw])
    if course_id:
        where_parts.append("c.course_id = %s")
        params.append(course_id)
    if status is not None:
        where_parts.append("c.status = %s")
        params.append(status)
    where_sql = " AND ".join(where_parts) if where_parts else "1=1"
    offset = (page_num - 1) * size
    rows = db.query_all(
        f"SELECT c.id, c.course_id, c.chapter_id, c.user_id, c.parent_id, c.content, c.status, c.deleted, c.create_time, "
        f"u.real_name AS user_real_name, u.username, co.title AS course_title "
        f"FROM ly_course_comment c "
        f"LEFT JOIN ly_user u ON c.user_id = u.id "
        f"LEFT JOIN ly_course co ON c.course_id = co.id "
        f"WHERE {where_sql} "
        f"ORDER BY c.id DESC LIMIT %s OFFSET %s",
        tuple(params + [size, offset]),
    )
    total = db.query_one(
        f"SELECT COUNT(*) AS cnt FROM ly_course_comment c "
        f"LEFT JOIN ly_user u ON c.user_id = u.id "
        f"WHERE {where_sql}",
        tuple(params),
    )
    return {
        "records": [_row_to_admin_dto(r) for r in rows],
        "total": total.get("cnt") or 0 if total else 0,
    }


def _row_to_admin_dto(r: dict) -> dict:
    """转换为管理员DTO（包含 deleted 和完整信息）"""
    out = {
        "id": r["id"],
        "courseId": r["course_id"],
        "courseTitle": r.get("course_title"),
        "chapterId": r.get("chapter_id"),
        "userId": r["user_id"],
        "userRealName": r.get("user_real_name"),
        "username": r.get("username"),
        "parentId": r.get("parent_id"),
        "content": r.get("content") or "",
        "status": r.get("status") or 1,
        "deleted": r.get("deleted") or 0,
        "createTime": r.get("create_time").isoformat() if r.get("create_time") else None,
    }
    return out
