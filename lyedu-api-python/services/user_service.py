# -*- coding: utf-8 -*-
"""用户服务，与 Java UserService 对应"""
from typing import Any, List, Optional

import pymysql

import db
from models.schemas import page_result

# 数据库是否包含 entry_date 列（V8 迁移），首次访问时检测
_has_entry_date: Optional[bool] = None
# 数据库是否包含 feishu_open_id 列（V2 迁移），首次访问时检测
_has_feishu_open_id: Optional[bool] = None
# 数据库是否包含 union_id 列（V18 迁移），首次访问时检测
_has_union_id: Optional[bool] = None


def _check_entry_date() -> bool:
    global _has_entry_date
    if _has_entry_date is not None:
        return _has_entry_date
    try:
        db.query_one("SELECT entry_date FROM ly_user LIMIT 1")
        _has_entry_date = True
    except (pymysql.err.OperationalError, pymysql.err.ProgrammingError) as e:
        if getattr(e, "args", (None,))[0] == 1054:  # Unknown column
            _has_entry_date = False
        else:
            raise
    return _has_entry_date


def _check_feishu_open_id() -> bool:
    global _has_feishu_open_id
    if _has_feishu_open_id is not None:
        return _has_feishu_open_id
    try:
        db.query_one("SELECT feishu_open_id FROM ly_user LIMIT 1")
        _has_feishu_open_id = True
    except (pymysql.err.OperationalError, pymysql.err.ProgrammingError) as e:
        if getattr(e, "args", (None,))[0] == 1054:
            _has_feishu_open_id = False
        else:
            raise
    return _has_feishu_open_id


def _check_union_id() -> bool:
    global _has_union_id
    if _has_union_id is not None:
        return _has_union_id
    try:
        db.query_one("SELECT union_id FROM ly_user LIMIT 1")
        _has_union_id = True
    except (pymysql.err.OperationalError, pymysql.err.ProgrammingError) as e:
        if getattr(e, "args", (None,))[0] == 1054:
            _has_union_id = False
        else:
            raise
    return _has_union_id


def _user_cols(include_create_time: bool = False) -> str:
    """用户表查询列，按库表是否有 feishu_open_id / union_id / entry_date 动态拼接"""
    parts = ["id", "username", "password", "real_name", "email", "mobile", "avatar"]
    if _check_feishu_open_id():
        parts.append("feishu_open_id")
    if _check_union_id():
        parts.append("union_id")
    parts.extend(["department_id"])
    if _check_entry_date():
        parts.append("entry_date")
    parts.extend(["role", "status"])
    if include_create_time:
        parts.append("create_time")
    return ", ".join(parts)


def find_by_username(username: str) -> Optional[dict]:
    cols = _user_cols()
    row = db.query_one(
        f"SELECT {cols} FROM ly_user WHERE username = %s AND deleted = 0 LIMIT 1",
        (username,),
    )
    return row


def find_by_feishu_open_id(feishu_open_id: str) -> Optional[dict]:
    if not (feishu_open_id or feishu_open_id.strip()):
        return None
    if not _check_feishu_open_id():
        return None
    cols = _user_cols()
    row = db.query_one(
        f"SELECT {cols} FROM ly_user WHERE feishu_open_id = %s AND deleted = 0 LIMIT 1",
        (feishu_open_id.strip(),),
    )
    return row


def find_by_union_id(union_id: str) -> Optional[dict]:
    """根据 union_id 查询用户（用于小程序等同一主体多应用）"""
    if not (union_id or union_id.strip()):
        return None
    if not _check_union_id():
        return None
    cols = _user_cols()
    row = db.query_one(
        f"SELECT {cols} FROM ly_user WHERE union_id = %s AND deleted = 0 LIMIT 1",
        (union_id.strip(),),
    )
    return row


def _row_to_user(row: dict) -> dict:
    if not row:
        return {}
    dept_id = row.get("department_id")
    return {
        "id": row["id"],
        "username": row.get("username"),
        "password": row.get("password"),
        "real_name": row.get("real_name"),
        "email": row.get("email"),
        "mobile": row.get("mobile"),
        "avatar": row.get("avatar"),
        "feishu_open_id": row.get("feishu_open_id"),
        "union_id": row.get("union_id"),
        "department_id": dept_id,
        "departmentId": dept_id,  # 前端使用的驼峰命名
        "entry_date": row.get("entry_date"),
        "entryDate": row.get("entry_date"),
        "role": row.get("role"),
        "status": row.get("status"),
        "create_time": row.get("create_time"),
        "createTime": row.get("create_time"),
    }


def get_by_id(user_id: int) -> Optional[dict]:
    cols = _user_cols(include_create_time=True)
    row = db.query_one(
        f"SELECT {cols} FROM ly_user WHERE id = %s AND deleted = 0",
        (user_id,),
    )
    return _row_to_user(row) if row else None


def page(
    page_num: int = 1,
    size: int = 10,
    keyword: Optional[str] = None,
    department_id: Optional[int] = None,
    role: Optional[str] = None,
    status: Optional[int] = None,
) -> dict:
    offset = (page_num - 1) * size
    where = ["deleted = 0"]
    params: List[Any] = []
    if keyword and keyword.strip():
        where.append("(username LIKE %s OR real_name LIKE %s OR email LIKE %s OR mobile LIKE %s)")
        like = "%" + keyword.strip() + "%"
        params.extend([like, like, like, like])
    if department_id is not None:
        where.append("department_id = %s")
        params.append(department_id)
    if role and role.strip():
        where.append("role = %s")
        params.append(role)
    if status is not None:
        where.append("status = %s")
        params.append(status)
    where_sql = " AND ".join(where)
    total_row = db.query_one(
        "SELECT COUNT(*) AS cnt FROM ly_user WHERE " + where_sql, tuple(params)
    )
    total = total_row["cnt"] or 0
    cols = _user_cols(include_create_time=True)
    sql = (
        f"SELECT {cols} FROM ly_user WHERE " + where_sql + " ORDER BY id DESC LIMIT %s OFFSET %s"
    )
    params.extend([size, offset])
    rows = db.query_all(sql, tuple(params))
    records = [_row_to_user(r) for r in rows]
    return page_result(records, total, page_num, size)


def save(
    username: str,
    password: Optional[str] = None,
    real_name: Optional[str] = None,
    email: Optional[str] = None,
    mobile: Optional[str] = None,
    avatar: Optional[str] = None,
    feishu_open_id: Optional[str] = None,
    union_id: Optional[str] = None,
    department_id: Optional[int] = None,
    entry_date: Optional[Any] = None,
    role: str = "student",
    status: int = 1,
) -> None:
    from passlib.hash import bcrypt
    pwd = (password or "123456").strip()
    encoded = bcrypt.hash(pwd)
    has_feishu = _check_feishu_open_id()
    has_union = _check_union_id()
    has_entry = _check_entry_date()
    cols = ["username", "password", "real_name", "email", "mobile", "avatar"]
    vals = [username, encoded, real_name, email, mobile, avatar]
    if has_feishu:
        cols.append("feishu_open_id")
        vals.append(feishu_open_id)
    if has_union:
        cols.append("union_id")
        vals.append(union_id)
    cols.extend(["department_id"])
    vals.append(department_id)
    if has_entry:
        cols.append("entry_date")
        vals.append(entry_date)
    cols.extend(["role", "status"])
    vals.append(role)
    vals.append(status)
    placeholders = ", ".join(["%s"] * len(vals))
    db.execute(
        f"INSERT INTO ly_user ({', '.join(cols)}) VALUES ({placeholders})",
        tuple(vals),
    )


def update(
    user_id: int,
    real_name: Optional[str] = None,
    email: Optional[str] = None,
    mobile: Optional[str] = None,
    avatar: Optional[str] = None,
    union_id: Optional[str] = None,
    department_id: Optional[int] = None,
    entry_date: Optional[Any] = None,
    role: Optional[str] = None,
    status: Optional[int] = None,
    username: Optional[str] = None,
) -> int:
    set_parts: List[str] = []
    params: List[Any] = []
    if entry_date is not None and _check_entry_date():
        set_parts.append("entry_date = %s")
        params.append(entry_date)
    if real_name is not None:
        set_parts.append("real_name = %s")
        params.append(real_name)
    if email is not None:
        set_parts.append("email = %s")
        params.append(email)
    if mobile is not None:
        set_parts.append("mobile = %s")
        params.append(mobile)
    if avatar is not None:
        set_parts.append("avatar = %s")
        params.append(avatar)
    if union_id is not None and _check_union_id():
        set_parts.append("union_id = %s")
        params.append(union_id)
    if department_id is not None:
        set_parts.append("department_id = %s")
        params.append(department_id)
    if role is not None:
        set_parts.append("role = %s")
        params.append(role)
    if status is not None:
        set_parts.append("status = %s")
        params.append(status)
    if username is not None:
        set_parts.append("username = %s")
        params.append(username)
    if not set_parts:
        return 0
    params.append(user_id)
    return db.execute(
        "UPDATE ly_user SET " + ", ".join(set_parts) + " WHERE id = %s AND deleted = 0",
        tuple(params),
    )


def delete(user_id: int) -> int:
    return db.execute("UPDATE ly_user SET deleted = 1 WHERE id = %s", (user_id,))


def update_password(user_id: int, password: str) -> int:
    from passlib.hash import bcrypt
    encoded = bcrypt.hash(password.strip())
    return db.execute("UPDATE ly_user SET password = %s WHERE id = %s AND deleted = 0", (encoded, user_id))
