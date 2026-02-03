# -*- coding: utf-8 -*-
"""用户证书记录服务，与 Java UserCertificateService 对应"""
import uuid
from datetime import datetime
from typing import List, Optional

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
