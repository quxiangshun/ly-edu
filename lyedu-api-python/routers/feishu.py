# -*- coding: utf-8 -*-
"""飞书通讯录同步：与 docs/飞书同步.md 一致，支持可选部门/用户、是否覆盖；支持后台异步避免超时"""
import threading
import time
import uuid
from typing import Dict, Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from common.result import error, success
from models.schemas import FeishuSyncRequest, FeishuSyncStats
from services.sync import feishu_sync_service
import config

router = APIRouter(prefix="/feishu", tags=["feishu"])

# 后台同步任务存储（进程内，重启后清空）；key=task_id, value={status, result, error, created_at}
_sync_tasks: Dict[str, Dict[str, Any]] = {}
_sync_tasks_lock = threading.Lock()
_TASK_EXPIRE_SECONDS = 3600


def _check_feishu_config() -> bool:
    return bool(config.FEISHU_APP_ID and config.FEISHU_APP_SECRET)


def _do_feishu_sync(opts: FeishuSyncRequest):
    """执行同步并返回统一结构（文档 4.5 响应格式）。"""
    result = feishu_sync_service.run_full_sync(
        sync_departments_flag=opts.sync_departments,
        sync_users_flag=opts.sync_users,
        overwrite_existing=opts.overwrite_existing,
    )
    stats = result.get("stats") or {}
    errors = result.get("errors") or []
    return {
        "success": len(errors) == 0,
        "message": "同步完成" if not errors else "同步完成但有部分错误",
        "stats": FeishuSyncStats(**stats),
        "departments": result.get("departments"),
        "users": result.get("users"),
        "errors": errors,
    }


def _run_sync_in_background(task_id: str, opts: FeishuSyncRequest) -> None:
    """在后台线程中执行同步，更新 _sync_tasks[task_id]。"""
    with _sync_tasks_lock:
        if task_id in _sync_tasks:
            _sync_tasks[task_id]["status"] = "running"
    try:
        data = _do_feishu_sync(opts)
        with _sync_tasks_lock:
            if task_id in _sync_tasks:
                _sync_tasks[task_id]["status"] = "completed"
                _sync_tasks[task_id]["result"] = data
    except Exception as e:
        with _sync_tasks_lock:
            if task_id in _sync_tasks:
                _sync_tasks[task_id]["status"] = "failed"
                _sync_tasks[task_id]["error"] = str(e)


@router.post("/sync")
def feishu_sync(
    body: FeishuSyncRequest | None = None,
    background: bool = Query(False, description="为 true 时异步执行，立即返回 task_id，通过 GET /sync/task/{task_id} 查询结果，避免长耗时超时"),
):
    """
    手动触发飞书通讯录同步（文档 四、五）：
    - sync_departments / sync_users / overwrite_existing 同请求体。
    - background=1 时：立即返回 202 与 task_id，同步在后台执行，用 GET /api/feishu/sync/task/{task_id} 轮询结果，避免请求超时。
    - 不传 background 或 background=0：同步执行并返回结果（可能因耗时长而超时）。
    """
    if not _check_feishu_config():
        return error(400, "请先在系统设置中配置飞书应用（App ID、App Secret），并在飞书开放平台申请通讯录权限")
    opts = body if body is not None else FeishuSyncRequest()

    if background:
        task_id = str(uuid.uuid4())
        with _sync_tasks_lock:
            _sync_tasks[task_id] = {
                "status": "pending",
                "result": None,
                "error": None,
                "created_at": time.time(),
            }
        t = threading.Thread(target=_run_sync_in_background, args=(task_id, opts), daemon=True)
        t.start()
        return JSONResponse(
            status_code=202,
            content=success({
                "task_id": task_id,
                "status": "pending",
                "message": "同步已启动，请通过 GET /api/feishu/sync/task/{task_id} 查询结果",
            }),
        )

    try:
        return success(_do_feishu_sync(opts))
    except Exception as e:
        return error(500, f"同步失败: {str(e)}")


@router.get("/sync/task/{task_id}")
def feishu_sync_task_status(task_id: str):
    """
    查询后台同步任务状态与结果。status: pending -> running -> completed 或 failed。
    完成后 result 为完整同步结果；失败时 error 为错误信息。
    """
    with _sync_tasks_lock:
        rec = _sync_tasks.get(task_id)
    if not rec:
        return error(404, "任务不存在或已过期")
    now = time.time()
    if rec.get("created_at") and (now - rec["created_at"]) > _TASK_EXPIRE_SECONDS and rec.get("status") in ("completed", "failed"):
        with _sync_tasks_lock:
            _sync_tasks.pop(task_id, None)
        return error(404, "任务已过期")
    data = {
        "task_id": task_id,
        "status": rec.get("status", "pending"),
        "result": rec.get("result"),
        "error": rec.get("error"),
    }
    return success(data)


@router.post("/sync/contacts")
def feishu_sync_contacts(
    body: FeishuSyncRequest | None = None,
    background: bool = Query(False, description="为 true 时异步执行，立即返回 task_id"),
):
    """
    飞书通讯录同步（文档 4.5 路径 /feishu/sync/contacts）。
    与 POST /sync 行为一致；传 background=1 可避免长耗时导致请求超时。
    """
    if not _check_feishu_config():
        return error(400, "请先配置飞书应用（FEISHU_APP_ID、FEISHU_APP_SECRET）及通讯录权限")
    opts = body if body is not None else FeishuSyncRequest()

    if background:
        task_id = str(uuid.uuid4())
        with _sync_tasks_lock:
            _sync_tasks[task_id] = {
                "status": "pending",
                "result": None,
                "error": None,
                "created_at": time.time(),
            }
        t = threading.Thread(target=_run_sync_in_background, args=(task_id, opts), daemon=True)
        t.start()
        return JSONResponse(
            status_code=202,
            content=success({
                "task_id": task_id,
                "status": "pending",
                "message": "同步已启动，请通过 GET /api/feishu/sync/task/{task_id} 查询结果",
            }),
        )

    try:
        return success(_do_feishu_sync(opts))
    except Exception as e:
        return error(500, f"同步失败: {str(e)}")


def _test_feishu_token():
    """测试飞书访问令牌，返回 (ok, data_or_message)。"""
    if not _check_feishu_config():
        return False, "未配置飞书应用"
    try:
        from util import feishu_api
        token = feishu_api._get_tenant_access_token()
        if token:
            return True, {"code": 0, "message": "飞书连接正常"}
        return False, "无法获取飞书访问令牌"
    except Exception as e:
        return False, f"测试失败: {str(e)}"


@router.get("/test")
def feishu_test_connection():
    """测试飞书访问令牌是否可用。"""
    ok, data = _test_feishu_token()
    return success(data) if ok else error(500, data if isinstance(data, str) else "无法获取飞书访问令牌")


@router.get("/sync/test")
def feishu_sync_test_connection():
    """测试飞书访问令牌（文档 4.5 GET /feishu/sync/test）。"""
    ok, data = _test_feishu_token()
    if ok:
        return success(data)
    return error(500, data if isinstance(data, str) else "无法获取飞书访问令牌")
