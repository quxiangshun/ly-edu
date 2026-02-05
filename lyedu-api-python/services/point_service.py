# -*- coding: utf-8 -*-
"""积分服务，与 Java PointService 对应"""
from typing import List, Optional

import db
from services import point_rule_service


def add_points(user_id: int, rule_key: str, ref_type: Optional[str], ref_id: Optional[int]) -> int:
    if not user_id or not (rule_key and rule_key.strip()):
        return 0
    rule = point_rule_service.get_by_key(rule_key)
    if not rule or (rule.get("enabled") or 0) != 1:
        return 0
    points = rule.get("points") or 0
    if points <= 0:
        return 0
    if ref_type and ref_id is not None:
        row = db.query_one(
            "SELECT 1 FROM ly_point_log WHERE user_id = %s AND ref_type = %s AND ref_id = %s LIMIT 1",
            (user_id, ref_type, ref_id),
        )
        if row:
            return 0
    remark = rule.get("ruleName") or rule_key
    db.execute(
        "INSERT INTO ly_point_log (user_id, points, rule_key, ref_type, ref_id, remark) VALUES (%s, %s, %s, %s, %s, %s)",
        (user_id, points, rule_key, ref_type, ref_id, remark),
    )
    db.execute("UPDATE ly_user SET total_points = COALESCE(total_points, 0) + %s WHERE id = %s", (points, user_id))
    return points


def get_total_points(user_id: int) -> int:
    if not user_id:
        return 0
    row = db.query_one("SELECT COALESCE(total_points, 0) AS total FROM ly_user WHERE id = %s", (user_id,))
    return int(row["total"]) if row else 0


def list_my_log(user_id: int, page: int = 1, size: int = 20) -> List[dict]:
    if not user_id:
        return []
    offset = (page - 1) * size
    rows = db.query_all(
        "SELECT id, user_id, points, rule_key, ref_type, ref_id, remark, create_time FROM ly_point_log WHERE user_id = %s ORDER BY create_time DESC LIMIT %s OFFSET %s",
        (user_id, size, offset),
    )
    return [_row_to_log(r) for r in (rows or [])]


def list_ranking(limit: int = 50, department_id: Optional[int] = None) -> List[dict]:
    if department_id is not None:
        rows = db.query_all(
            "SELECT u.id AS userId, u.real_name AS realName, u.username, COALESCE(u.total_points, 0) AS totalPoints FROM ly_user u WHERE u.deleted = 0 AND u.department_id = %s ORDER BY totalPoints DESC, u.id ASC LIMIT %s",
            (department_id, limit),
        )
    else:
        rows = db.query_all(
            "SELECT u.id AS userId, u.real_name AS realName, u.username, COALESCE(u.total_points, 0) AS totalPoints FROM ly_user u WHERE u.deleted = 0 ORDER BY totalPoints DESC, u.id ASC LIMIT %s",
            (limit,),
        )
    result = []
    for i, r in enumerate(rows or []):
        result.append({
            "userId": r.get("userId"),
            "realName": r.get("real_name") or r.get("realName"),
            "username": r.get("username"),
            "totalPoints": r.get("total_points") if "total_points" in r else r.get("totalPoints"),
            "rank": i + 1,
        })
    return result


def _row_to_log(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "userId": row.get("user_id"),
        "points": row.get("points"),
        "ruleKey": row.get("rule_key"),
        "refType": row.get("ref_type"),
        "refId": row.get("ref_id"),
        "remark": row.get("remark"),
        "createTime": row.get("create_time"),
    }


def page_log(
    page_num: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    user_id: Optional[int] = None,
) -> dict:
    """分页查询积分记录（管理员）"""
    from typing import Any
    from common.result import page_result
    
    page_num = max(1, page_num)
    size = max(1, min(100, size))
    offset = (page_num - 1) * size
    
    where_clauses = []
    params: List[Any] = []
    
    if keyword:
        where_clauses.append("(u.real_name LIKE %s OR u.username LIKE %s OR pl.remark LIKE %s)")
        keyword_pattern = f"%{keyword}%"
        params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
    
    if user_id:
        where_clauses.append("pl.user_id = %s")
        params.append(user_id)
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # 查询总数
    count_sql = (
        f"SELECT COUNT(*) AS total FROM ly_point_log pl "
        f"LEFT JOIN ly_user u ON pl.user_id = u.id AND u.deleted = 0 "
        f"WHERE {where_sql}"
    )
    total_row = db.query_one(count_sql, tuple(params))
    total = total_row.get("total") or 0 if total_row else 0
    
    # 查询数据
    data_sql = (
        f"SELECT pl.id, pl.user_id AS userId, pl.points, pl.rule_key AS ruleKey, "
        f"pl.ref_type AS refType, pl.ref_id AS refId, pl.remark, pl.create_time AS createTime, "
        f"u.real_name AS realName, u.username "
        f"FROM ly_point_log pl "
        f"LEFT JOIN ly_user u ON pl.user_id = u.id AND u.deleted = 0 "
        f"WHERE {where_sql} "
        f"ORDER BY pl.create_time DESC LIMIT %s OFFSET %s"
    )
    params.extend([size, offset])
    rows = db.query_all(data_sql, tuple(params))
    
    records = []
    for r in (rows or []):
        record = {
            "id": r.get("id"),
            "userId": r.get("userId"),
            "realName": r.get("realName"),
            "username": r.get("username"),
            "points": r.get("points"),
            "ruleKey": r.get("ruleKey"),
            "refType": r.get("refType"),
            "refId": r.get("refId"),
            "remark": r.get("remark"),
            "createTime": r.get("createTime"),
        }
        records.append(record)
    
    return page_result(records, total, page_num, size)
