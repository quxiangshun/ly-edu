# -*- coding: utf-8 -*-
"""用户任务进度路由，与 Java UserTaskController 对应"""
from typing import Optional

from fastapi import APIRouter, Header
from pydantic import BaseModel

from common.result import error_result, success
from services import user_task_service
from util.jwt_util import parse_authorization

router = APIRouter(prefix="/user-task", tags=["user-task"])


def _user_id(authorization: Optional[str]) -> Optional[int]:
    return parse_authorization(authorization)


class ProgressRequest(BaseModel):
    progress: Optional[str] = None


@router.get("/my")
def my_tasks(authorization: Optional[str] = Header(None, alias="Authorization")):
    user_id = _user_id(authorization)
    if not user_id:
        return error_result((401, "未登录"))
    return success(user_task_service.list_my_tasks(user_id))


@router.get("/task/{task_id}")
def task_detail(
    task_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    if not user_id:
        return error_result((401, "未登录"))
    t = user_task_service.get_task_detail(task_id, user_id)
    if not t:
        return error_result((404, "资源不存在"))
    return success(t)


@router.get("/task/{task_id}/progress")
def get_or_create_progress(
    task_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    if not user_id:
        return error_result((401, "未登录"))
    ut = user_task_service.get_or_create_user_task(task_id, user_id)
    if not ut:
        return error_result((404, "资源不存在"))
    return success(ut)


@router.post("/task/{task_id}/progress")
def update_progress(
    task_id: int,
    body: ProgressRequest,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    if not user_id:
        return error_result((401, "未登录"))
    ut = user_task_service.update_progress(task_id, user_id, body.progress if body else None)
    if not ut:
        return error_result((404, "资源不存在"))
    return success(ut)


@router.get("/page")
def page(
    page: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    userId: Optional[int] = None,
    taskId: Optional[int] = None,
):
    """分页查询用户任务（管理员）"""
    return success(user_task_service.page(page_num=page, size=size, keyword=keyword, user_id=userId, task_id=taskId))
