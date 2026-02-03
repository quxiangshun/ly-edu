# -*- coding: utf-8 -*-
"""系统配置服务，与 Java ConfigService 对应"""
from typing import List, Optional

import db


def get_by_key(config_key: str) -> Optional[str]:
    if not config_key or not config_key.strip():
        return None
    row = db.query_one("SELECT config_value FROM ly_config WHERE config_key = %s", (config_key.strip(),))
    return row.get("config_value") if row else None


def list_by_category(category: Optional[str]) -> List[dict]:
    if category and category.strip():
        rows = db.query_all(
            "SELECT id, config_key, config_value, category, remark, create_time, update_time FROM ly_config WHERE category = %s ORDER BY config_key",
            (category.strip(),),
        )
    else:
        rows = db.query_all(
            "SELECT id, config_key, config_value, category, remark, create_time, update_time FROM ly_config ORDER BY category, config_key"
        )
    return [
        {
            "id": r["id"],
            "configKey": r["config_key"],
            "configValue": r["config_value"],
            "category": r["category"],
            "remark": r["remark"],
            "createTime": r["create_time"],
            "updateTime": r["update_time"],
        }
        for r in (rows or [])
    ]


def list_all() -> List[dict]:
    return list_by_category(None)


def set_key(config_key: str, config_value: Optional[str], category: Optional[str] = "site", remark: Optional[str] = None) -> None:
    if not config_key or not config_key.strip():
        return
    row = db.query_one("SELECT id FROM ly_config WHERE config_key = %s", (config_key.strip(),))
    if row:
        db.execute(
            "UPDATE ly_config SET config_value = %s, category = %s, remark = %s WHERE config_key = %s",
            (config_value, category or "site", remark, config_key.strip()),
        )
    else:
        db.execute(
            "INSERT INTO ly_config (config_key, config_value, category, remark) VALUES (%s, %s, %s, %s)",
            (config_key.strip(), config_value, category or "site", remark),
        )
