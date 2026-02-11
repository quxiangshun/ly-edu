# -*- coding: utf-8 -*-
"""企业微信通讯录同步：空实现，预留扩展"""
from typing import Dict, Any


def run_full_sync(
    sync_departments_flag: bool = True,
    sync_users_flag: bool = True,
    overwrite_existing: bool = False,
) -> Dict[str, Any]:
    """企业微信同步入口：空实现"""
    return {
        "departments": {"created": 0, "updated": 0, "skipped": 0, "failed": 0, "errors": []},
        "users": {"created": 0, "updated": 0, "skipped": 0, "failed": 0, "errors": []},
        "stats": {
            "departments_created": 0,
            "departments_updated": 0,
            "departments_skipped": 0,
            "departments_failed": 0,
            "users_created": 0,
            "users_updated": 0,
            "users_skipped": 0,
            "users_failed": 0,
        },
        "errors": ["企业微信同步功能尚未实现"],
    }
