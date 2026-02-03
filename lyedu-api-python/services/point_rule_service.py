# -*- coding: utf-8 -*-
"""积分规则服务，与 Java PointRuleService 对应"""
from typing import List, Optional

import db


def list_all() -> List[dict]:
    rows = db.query_all(
        "SELECT id, rule_key, rule_name, points, enabled, remark, create_time, update_time FROM ly_point_rule ORDER BY id"
    )
    return [_row_to_rule(r) for r in (rows or [])]


def get_by_key(rule_key: str) -> Optional[dict]:
    if not (rule_key and rule_key.strip()):
        return None
    row = db.query_one(
        "SELECT id, rule_key, rule_name, points, enabled, remark, create_time, update_time FROM ly_point_rule WHERE rule_key = %s",
        (rule_key.strip(),),
    )
    return _row_to_rule(row) if row else None


def update(rule_key: str, rule_name: Optional[str], points: Optional[int], enabled: Optional[int], remark: Optional[str]) -> None:
    if not (rule_key and rule_key.strip()):
        return
    db.execute(
        "UPDATE ly_point_rule SET rule_name = %s, points = %s, enabled = %s, remark = %s WHERE rule_key = %s",
        (rule_name, points, enabled, remark, rule_key.strip()),
    )


def _row_to_rule(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "ruleKey": row.get("rule_key"),
        "ruleName": row.get("rule_name"),
        "points": row.get("points"),
        "enabled": row.get("enabled"),
        "remark": row.get("remark"),
        "createTime": row.get("create_time"),
        "updateTime": row.get("update_time"),
    }
