# -*- coding: utf-8 -*-
"""系统配置路由，与 Java ConfigController 对应"""
from typing import Optional

from fastapi import APIRouter

from common.result import success
from services import config_service

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/key/{key}")
def get_by_key(key: str):
    return success(config_service.get_by_key(key))


@router.get("/category/{category}")
def list_by_category(category: str):
    return success(config_service.list_by_category(category))


@router.get("/all")
def list_all():
    return success(config_service.list_all())


@router.post("/set")
def set_config(body: dict):
    config_key = body.get("configKey") or body.get("config_key")
    config_value = body.get("configValue") or body.get("config_value")
    category = body.get("category")
    remark = body.get("remark")
    if config_key:
        config_service.set_key(config_key, config_value, category, remark)
    return success(None)


@router.post("/batch")
def batch_set(body: dict):
    if body:
        for k, v in body.items():
            if k and str(k).strip():
                config_service.set_key(str(k).strip(), str(v) if v is not None else None)
    return success(None)
