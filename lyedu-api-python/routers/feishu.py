# -*- coding: utf-8 -*-
"""飞书通讯录同步：手动触发、定时任务"""
from fastapi import APIRouter

from common.result import error, success
from services import feishu_sync_service
import config

router = APIRouter(prefix="/feishu", tags=["feishu"])


def _check_feishu_config() -> bool:
    return bool(config.FEISHU_APP_ID and config.FEISHU_APP_SECRET)


@router.post("/sync")
def feishu_sync():
    """
    手动触发飞书通讯录同步：先同步部门（机构），再同步用户。
    部门/用户不存在则创建，存在则更新。
    需在系统设置或环境变量中配置 FEISHU_APP_ID、FEISHU_APP_SECRET，并在飞书开放平台申请通讯录只读权限。
    """
    if not _check_feishu_config():
        return error(400, "请先在系统设置中配置飞书应用（App ID、App Secret），并在飞书开放平台申请通讯录权限")
    try:
        result = feishu_sync_service.run_full_sync()
        return success(result)
    except Exception as e:
        return error(500, f"同步失败: {str(e)}")
