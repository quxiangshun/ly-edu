# -*- coding: utf-8 -*-
"""证书模板服务，与 Java CertificateTemplateService 对应"""
from typing import List, Optional

import db

SELECT_COLS = "id, name, description, config, sort, status, create_time, update_time, deleted"


def _row_to_template(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "name": row.get("name"),
        "description": row.get("description"),
        "config": row.get("config"),
        "sort": row.get("sort", 0),
        "status": row.get("status", 1),
        "createTime": row.get("create_time"),
        "updateTime": row.get("update_time"),
        "deleted": row.get("deleted"),
    }


def list_all() -> List[dict]:
    sql = f"SELECT {SELECT_COLS} FROM ly_certificate_template WHERE deleted = 0 ORDER BY sort ASC, id DESC"
    rows = db.query_all(sql, ())
    return [_row_to_template(r) for r in (rows or [])]


def get_by_id(template_id: int) -> Optional[dict]:
    if not template_id:
        return None
    sql = f"SELECT {SELECT_COLS} FROM ly_certificate_template WHERE id = %s AND deleted = 0"
    row = db.query_one(sql, (template_id,))
    return _row_to_template(row) if row else None


def save(entity: dict) -> int:
    sql = "INSERT INTO ly_certificate_template (name, description, config, sort, status) VALUES (%s, %s, %s, %s, %s)"
    args = (
        entity.get("name"),
        entity.get("description"),
        entity.get("config"),
        entity.get("sort", 0),
        entity.get("status", 1),
    )
    return db.execute_insert(sql, args)


def update(entity: dict) -> None:
    if not entity.get("id"):
        return
    sql = "UPDATE ly_certificate_template SET name = %s, description = %s, config = %s, sort = %s, status = %s WHERE id = %s AND deleted = 0"
    db.execute(
        sql,
        (
            entity.get("name"),
            entity.get("description"),
            entity.get("config"),
            entity.get("sort", 0),
            entity.get("status", 1),
            entity.get("id"),
        ),
    )


def delete(template_id: int) -> None:
    if not template_id:
        return
    db.execute("UPDATE ly_certificate_template SET deleted = 1 WHERE id = %s", (template_id,))
