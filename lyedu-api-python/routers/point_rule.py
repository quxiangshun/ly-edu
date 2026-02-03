# -*- coding: utf-8 -*-
"""积分规则管理路由，与 Java PointRuleController 对应"""
from fastapi import APIRouter

from common.result import error_result, success
from services import point_rule_service

router = APIRouter(prefix="/point-rule", tags=["point-rule"])


@router.get("/list")
def list_rules():
    return success(point_rule_service.list_all())


@router.put("/update")
def update_rule(body: dict):
    rule_key = body.get("ruleKey") or body.get("rule_key")
    if not (rule_key and str(rule_key).strip()):
        return error_result((400, "参数错误"))
    point_rule_service.update(
        rule_key=str(rule_key).strip(),
        rule_name=body.get("ruleName") or body.get("rule_name"),
        points=body.get("points"),
        enabled=body.get("enabled"),
        remark=body.get("remark"),
    )
    return success()
