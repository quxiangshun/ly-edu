# -*- coding: utf-8 -*-
"""用户证书记录服务，与 Java UserCertificateService 对应"""
import uuid
from datetime import datetime
from typing import Any, List, Optional

import db
from services import certificate_service
from services import certificate_template_service

SELECT_COLS = "id, user_id, certificate_id, template_id, certificate_no, title, issued_at, create_time"


def _row_to_user_certificate(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "userId": row.get("user_id"),
        "certificateId": row.get("certificate_id"),
        "templateId": row.get("template_id"),
        "certificateNo": row.get("certificate_no"),
        "title": row.get("title"),
        "issuedAt": row.get("issued_at"),
        "createTime": row.get("create_time"),
    }


def list_by_user_id(user_id: int) -> List[dict]:
    if not user_id:
        return []
    sql = f"SELECT {SELECT_COLS} FROM ly_user_certificate WHERE user_id = %s ORDER BY issued_at DESC"
    rows = db.query_all(sql, (user_id,))
    return [_row_to_user_certificate(r) for r in (rows or [])]


def get_by_id(uc_id: int) -> Optional[dict]:
    if not uc_id:
        return None
    sql = f"SELECT {SELECT_COLS} FROM ly_user_certificate WHERE id = %s"
    row = db.query_one(sql, (uc_id,))
    return _row_to_user_certificate(row) if row else None


def has_certificate(certificate_id: int, user_id: int) -> bool:
    if not certificate_id or not user_id:
        return False
    sql = "SELECT 1 FROM ly_user_certificate WHERE certificate_id = %s AND user_id = %s LIMIT 1"
    row = db.query_one(sql, (certificate_id, user_id))
    return bool(row)


def issue_if_eligible(source_type: str, source_id: int, user_id: int) -> Optional[dict]:
    if not source_type or not source_id or not user_id:
        return None
    rule = certificate_service.get_by_source(source_type, source_id)
    if not rule:
        return None
    if has_certificate(rule.get("id"), user_id):
        return None
    template = certificate_template_service.get_by_id(rule.get("templateId"))
    if not template or (template.get("status") or 1) != 1:
        return None

    certificate_no = "CERT-" + str(int(datetime.now().timestamp() * 1000)) + "-" + uuid.uuid4().hex[:8].upper()
    title = rule.get("name", "")
    issued_at = datetime.now()

    sql = "INSERT INTO ly_user_certificate (user_id, certificate_id, template_id, certificate_no, title, issued_at) VALUES (%s, %s, %s, %s, %s, %s)"
    rid = db.execute_insert(
        sql,
        (user_id, rule.get("id"), rule.get("templateId"), certificate_no, title, issued_at),
    )
    if not rid:
        return None
    return {
        "id": rid,
        "userId": user_id,
        "certificateId": rule.get("id"),
        "templateId": rule.get("templateId"),
        "certificateNo": certificate_no,
        "title": title,
        "issuedAt": issued_at,
        "createTime": issued_at,
    }


def page(
    page_num: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    user_id: Optional[int] = None,
    certificate_id: Optional[int] = None,
) -> dict:
    """分页查询用户证书（管理员）"""
    from typing import Any
    from common.result import page_result
    
    page_num = max(1, page_num)
    size = max(1, min(100, size))
    offset = (page_num - 1) * size
    
    where_clauses = []
    params: List[Any] = []
    
    if keyword:
        where_clauses.append("(u.real_name LIKE %s OR u.username LIKE %s OR uc.title LIKE %s OR uc.certificate_no LIKE %s)")
        keyword_pattern = f"%{keyword}%"
        params.extend([keyword_pattern, keyword_pattern, keyword_pattern, keyword_pattern])
    
    if user_id:
        where_clauses.append("uc.user_id = %s")
        params.append(user_id)
    
    if certificate_id:
        where_clauses.append("uc.certificate_id = %s")
        params.append(certificate_id)
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # 查询总数
    count_sql = (
        f"SELECT COUNT(*) AS total FROM ly_user_certificate uc "
        f"LEFT JOIN ly_user u ON uc.user_id = u.id AND u.deleted = 0 "
        f"WHERE {where_sql}"
    )
    total_row = db.query_one(count_sql, tuple(params))
    total = total_row.get("total") or 0 if total_row else 0
    
    # 查询数据
    data_sql = (
        f"SELECT uc.id, uc.user_id AS userId, uc.certificate_id AS certificateId, "
        f"uc.template_id AS templateId, uc.certificate_no AS certificateNo, uc.title, "
        f"uc.issued_at AS issuedAt, uc.create_time AS createTime, "
        f"u.real_name AS realName, u.username "
        f"FROM ly_user_certificate uc "
        f"LEFT JOIN ly_user u ON uc.user_id = u.id AND u.deleted = 0 "
        f"WHERE {where_sql} "
        f"ORDER BY uc.issued_at DESC LIMIT %s OFFSET %s"
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
            "certificateId": r.get("certificateId"),
            "templateId": r.get("templateId"),
            "certificateNo": r.get("certificateNo"),
            "title": r.get("title"),
            "issuedAt": r.get("issuedAt"),
            "createTime": r.get("createTime"),
        }
        records.append(record)
    
    return page_result(records, total, page_num, size)
