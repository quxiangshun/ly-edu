# -*- coding: utf-8 -*-
"""证书颁发规则服务，与 Java CertificateService 对应"""
from typing import List, Optional

import db

SELECT_COLS = "id, template_id, name, source_type, source_id, sort, status, create_time, update_time, deleted"


def _row_to_certificate(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "templateId": row.get("template_id"),
        "name": row.get("name"),
        "sourceType": row.get("source_type"),
        "sourceId": row.get("source_id"),
        "sort": row.get("sort", 0),
        "status": row.get("status", 1),
        "createTime": row.get("create_time"),
        "updateTime": row.get("update_time"),
        "deleted": row.get("deleted"),
    }


def list_all() -> List[dict]:
    sql = f"SELECT {SELECT_COLS} FROM ly_certificate WHERE deleted = 0 ORDER BY sort ASC, id DESC"
    rows = db.query_all(sql, ())
    return [_row_to_certificate(r) for r in (rows or [])]


def get_by_id(cert_id: int) -> Optional[dict]:
    if not cert_id:
        return None
    sql = f"SELECT {SELECT_COLS} FROM ly_certificate WHERE id = %s AND deleted = 0"
    row = db.query_one(sql, (cert_id,))
    return _row_to_certificate(row) if row else None


def get_by_source(source_type: str, source_id: int) -> Optional[dict]:
    if not source_type or not source_id:
        return None
    sql = f"SELECT {SELECT_COLS} FROM ly_certificate WHERE source_type = %s AND source_id = %s AND status = 1 AND deleted = 0 LIMIT 1"
    row = db.query_one(sql, (source_type, source_id))
    return _row_to_certificate(row) if row else None


def save(entity: dict) -> int:
    sql = "INSERT INTO ly_certificate (template_id, name, source_type, source_id, sort, status) VALUES (%s, %s, %s, %s, %s, %s)"
    args = (
        entity.get("templateId"),
        entity.get("name"),
        entity.get("sourceType"),
        entity.get("sourceId"),
        entity.get("sort", 0),
        entity.get("status", 1),
    )
    return db.execute_insert(sql, args)


def update(entity: dict) -> None:
    if not entity.get("id"):
        return
    sql = "UPDATE ly_certificate SET template_id = %s, name = %s, source_type = %s, source_id = %s, sort = %s, status = %s WHERE id = %s AND deleted = 0"
    db.execute(
        sql,
        (
            entity.get("templateId"),
            entity.get("name"),
            entity.get("sourceType"),
            entity.get("sourceId"),
            entity.get("sort", 0),
            entity.get("status", 1),
            entity.get("id"),
        ),
    )


def delete(cert_id: int) -> None:
    if not cert_id:
        return
    db.execute("UPDATE ly_certificate SET deleted = 1 WHERE id = %s", (cert_id,))
