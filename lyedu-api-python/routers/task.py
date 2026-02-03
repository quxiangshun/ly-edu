# -*- coding: utf-8 -*-
"""周期任务路由，与 Java TaskController 对应"""
from typing import List, Optional

from fastapi import APIRouter, Header
from pydantic import BaseModel

from common.result import error_result, success
from services import task_service
from util.jwt_util import parse_authorization

router = APIRouter(prefix="/task", tags=["task"])


def _user_id(authorization: Optional[str]) -> Optional[int]:
    return parse_authorization(authorization)


def _parse_datetime(s: Optional[str]):
    if not s:
        return None
    try:
        from datetime import datetime
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


class TaskRequest(BaseModel):
    title: str = ""
    description: Optional[str] = None
    cycleType: Optional[str] = "once"
    cycleConfig: Optional[str] = None
    items: Optional[str] = "[]"
    certificateId: Optional[int] = None
    sort: Optional[int] = 0
    status: Optional[int] = 1
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    departmentIds: Optional[List[int]] = None


@router.get("/admin/{task_id}")
def get_by_id_admin(task_id: int):
    t = task_service.get_by_id_ignore_visibility(task_id)
    if not t:
        return error_result((404, "资源不存在"))
    return success(t)


@router.get("/page")
def page(
    page: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    return success(task_service.page(page_num=page, size=size, keyword=keyword, user_id=user_id))


@router.get("/{task_id}")
def get_by_id(
    task_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    t = task_service.get_by_id(task_id, user_id)
    if not t:
        return error_result((404, "资源不存在"))
    return success(t)


@router.post("")
def create(body: TaskRequest):
    title = (body.title or "").strip()
    if not title:
        return error_result((400, "任务名称不能为空"))
    tid = task_service.save(
        title=title,
        description=body.description,
        cycle_type=body.cycleType or "once",
        cycle_config=body.cycleConfig,
        items=body.items or "[]",
        certificate_id=body.certificateId,
        sort=body.sort or 0,
        status=body.status or 1,
        start_time=_parse_datetime(body.startTime),
        end_time=_parse_datetime(body.endTime),
        department_ids=body.departmentIds,
    )
    return success(tid)


@router.put("/{task_id}")
def update(task_id: int, body: TaskRequest):
    existing = task_service.get_by_id_ignore_visibility(task_id)
    if not existing:
        return error_result((404, "资源不存在"))
    title = (body.title or "").strip()
    if not title:
        return error_result((400, "任务名称不能为空"))
    ok = task_service.update(
        task_id=task_id,
        title=title,
        description=body.description,
        cycle_type=body.cycleType or "once",
        cycle_config=body.cycleConfig,
        items=body.items or "[]",
        certificate_id=body.certificateId,
        sort=body.sort or 0,
        status=body.status or 1,
        start_time=_parse_datetime(body.startTime),
        end_time=_parse_datetime(body.endTime),
        department_ids=body.departmentIds,
    )
    if not ok:
        return error_result((500, "更新失败"))
    return success(None)


@router.delete("/{task_id}")
def delete(task_id: int):
    existing = task_service.get_by_id_ignore_visibility(task_id)
    if not existing:
        return error_result((404, "资源不存在"))
    task_service.delete(task_id)
    return success(None)
