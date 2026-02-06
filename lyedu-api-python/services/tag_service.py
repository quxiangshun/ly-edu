# -*- coding: utf-8 -*-
"""标签服务：标签 CRUD 及与用户/部门/课程的关联"""
from typing import List, Optional

import pymysql

import db
from services import user_service
from services import department_service
from services import course_service


def _table_exists() -> bool:
    try:
        db.query_one("SELECT 1 FROM ly_tag LIMIT 0")
        return True
    except (pymysql.err.OperationalError, pymysql.err.ProgrammingError) as e:
        if getattr(e, "args", (None,))[0] in (1054, 1146):
            return False
        raise


def list_all() -> List[dict]:
    if not _table_exists():
        return []
    rows = db.query_all(
        "SELECT id, name, sort, create_time FROM ly_tag ORDER BY sort ASC, id ASC"
    )
    return [_row_to_tag(r) for r in (rows or [])]


def get_by_id(tag_id: int) -> Optional[dict]:
    if not _table_exists():
        return None
    row = db.query_one(
        "SELECT id, name, sort, create_time FROM ly_tag WHERE id = %s",
        (tag_id,),
    )
    return _row_to_tag(row) if row else None


def _row_to_tag(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "name": row.get("name"),
        "sort": row.get("sort", 0),
        "createTime": row.get("create_time"),
    }


def save(name: str, sort: int = 0) -> None:
    if not _table_exists():
        raise RuntimeError("ly_tag 表不存在，请先执行数据库迁移")
    name = (name or "").strip()
    if not name:
        raise ValueError("标签名称不能为空")
    db.execute(
        "INSERT INTO ly_tag (name, sort) VALUES (%s, %s)",
        (name, sort),
    )


def update(tag_id: int, name: Optional[str] = None, sort: Optional[int] = None) -> int:
    if not _table_exists():
        return 0
    updates = []
    params = []
    if name is not None:
        updates.append("name = %s")
        params.append((name or "").strip())
    if sort is not None:
        updates.append("sort = %s")
        params.append(sort)
    if not updates:
        return 0
    params.append(tag_id)
    return db.execute(
        "UPDATE ly_tag SET " + ", ".join(updates) + " WHERE id = %s",
        tuple(params),
    )


def delete(tag_id: int) -> int:
    if not _table_exists():
        return 0
    db.execute("DELETE FROM ly_user_tag WHERE tag_id = %s", (tag_id,))
    db.execute("DELETE FROM ly_department_tag WHERE tag_id = %s", (tag_id,))
    db.execute("DELETE FROM ly_course_tag WHERE tag_id = %s", (tag_id,))
    return db.execute("DELETE FROM ly_tag WHERE id = %s", (tag_id,))


# ---------- 实体与标签的关联 ----------


def list_tag_ids_by_user(user_id: int) -> List[int]:
    if not _table_exists():
        return []
    try:
        rows = db.query_all("SELECT tag_id FROM ly_user_tag WHERE user_id = %s", (user_id,))
        return [int(r["tag_id"]) for r in (rows or []) if r.get("tag_id") is not None]
    except (pymysql.err.OperationalError, pymysql.err.ProgrammingError) as e:
        if getattr(e, "args", (None,))[0] in (1054, 1146):
            return []
        raise


def list_tag_ids_by_department(department_id: int) -> List[int]:
    if not _table_exists():
        return []
    try:
        rows = db.query_all(
            "SELECT tag_id FROM ly_department_tag WHERE department_id = %s",
            (department_id,),
        )
        return [int(r["tag_id"]) for r in (rows or []) if r.get("tag_id") is not None]
    except (pymysql.err.OperationalError, pymysql.err.ProgrammingError) as e:
        if getattr(e, "args", (None,))[0] in (1054, 1146):
            return []
        raise


def list_tag_ids_by_course(course_id: int) -> List[int]:
    if not _table_exists():
        return []
    try:
        rows = db.query_all(
            "SELECT tag_id FROM ly_course_tag WHERE course_id = %s",
            (course_id,),
        )
        return [int(r["tag_id"]) for r in (rows or []) if r.get("tag_id") is not None]
    except (pymysql.err.OperationalError, pymysql.err.ProgrammingError) as e:
        if getattr(e, "args", (None,))[0] in (1054, 1146):
            return []
        raise


def set_tags_for_user(user_id: int, tag_ids: List[int]) -> None:
    if not _table_exists():
        return
    db.execute("DELETE FROM ly_user_tag WHERE user_id = %s", (user_id,))
    for tid in tag_ids or []:
        if tid:
            try:
                db.execute(
                    "INSERT INTO ly_user_tag (user_id, tag_id) VALUES (%s, %s)",
                    (user_id, tid),
                )
            except pymysql.err.IntegrityError:
                pass


def set_tags_for_department(department_id: int, tag_ids: List[int]) -> None:
    if not _table_exists():
        return
    db.execute("DELETE FROM ly_department_tag WHERE department_id = %s", (department_id,))
    for tid in tag_ids or []:
        if tid:
            try:
                db.execute(
                    "INSERT INTO ly_department_tag (department_id, tag_id) VALUES (%s, %s)",
                    (department_id, tid),
                )
            except pymysql.err.IntegrityError:
                pass


def set_tags_for_course(course_id: int, tag_ids: List[int]) -> None:
    if not _table_exists():
        return
    db.execute("DELETE FROM ly_course_tag WHERE course_id = %s", (course_id,))
    for tid in tag_ids or []:
        if tid:
            try:
                db.execute(
                    "INSERT INTO ly_course_tag (course_id, tag_id) VALUES (%s, %s)",
                    (course_id, tid),
                )
            except pymysql.err.IntegrityError:
                pass


def get_users_by_tag(tag_id: int) -> List[dict]:
    if not _table_exists():
        return []
    try:
        rows = db.query_all(
            "SELECT user_id FROM ly_user_tag WHERE tag_id = %s",
            (tag_id,),
        )
        user_ids = [int(r["user_id"]) for r in (rows or []) if r.get("user_id") is not None]
        result = []
        for uid in user_ids:
            u = user_service.get_by_id(uid)
            if u:
                result.append(u)
        return result
    except (pymysql.err.OperationalError, pymysql.err.ProgrammingError) as e:
        if getattr(e, "args", (None,))[0] in (1054, 1146):
            return []
        raise


def get_departments_by_tag(tag_id: int) -> List[dict]:
    if not _table_exists():
        return []
    try:
        rows = db.query_all(
            "SELECT department_id FROM ly_department_tag WHERE tag_id = %s",
            (tag_id,),
        )
        dept_ids = [int(r["department_id"]) for r in (rows or []) if r.get("department_id") is not None]
        result = []
        for did in dept_ids:
            d = department_service.get_by_id(did)
            if d:
                result.append(d)
        return result
    except (pymysql.err.OperationalError, pymysql.err.ProgrammingError) as e:
        if getattr(e, "args", (None,))[0] in (1054, 1146):
            return []
        raise


def get_courses_by_tag(tag_id: int) -> List[dict]:
    if not _table_exists():
        return []
    try:
        rows = db.query_all(
            "SELECT course_id FROM ly_course_tag WHERE tag_id = %s",
            (tag_id,),
        )
        course_ids = [int(r["course_id"]) for r in (rows or []) if r.get("course_id") is not None]
        result = []
        for cid in course_ids:
            c = course_service.get_by_id_ignore_visibility(cid)
            if c:
                result.append(c)
        return result
    except (pymysql.err.OperationalError, pymysql.err.ProgrammingError) as e:
        if getattr(e, "args", (None,))[0] in (1054, 1146):
            return []
        raise


def set_tag_entities(
    tag_id: int,
    user_ids: Optional[List[int]] = None,
    department_ids: Optional[List[int]] = None,
    course_ids: Optional[List[int]] = None,
) -> None:
    """为标签绑定/解绑人员、部门、课程（传空列表则清空该类型）"""
    if not _table_exists():
        return
    if user_ids is not None:
        db.execute("DELETE FROM ly_user_tag WHERE tag_id = %s", (tag_id,))
        for uid in user_ids:
            if uid:
                try:
                    db.execute("INSERT INTO ly_user_tag (user_id, tag_id) VALUES (%s, %s)", (uid, tag_id))
                except pymysql.err.IntegrityError:
                    pass
    if department_ids is not None:
        db.execute("DELETE FROM ly_department_tag WHERE tag_id = %s", (tag_id,))
        for did in department_ids:
            if did:
                try:
                    db.execute("INSERT INTO ly_department_tag (department_id, tag_id) VALUES (%s, %s)", (did, tag_id))
                except pymysql.err.IntegrityError:
                    pass
    if course_ids is not None:
        db.execute("DELETE FROM ly_course_tag WHERE tag_id = %s", (tag_id,))
        for cid in course_ids:
            if cid:
                try:
                    db.execute("INSERT INTO ly_course_tag (course_id, tag_id) VALUES (%s, %s)", (cid, tag_id))
                except pymysql.err.IntegrityError:
                    pass
