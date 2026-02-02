# -*- coding: utf-8 -*-
"""用户路由，与 Java UserController 对应"""
from typing import Optional

from fastapi import APIRouter, Header

from common.result import ResultCode, error, error_result, success
from models.schemas import UserRequest, ResetPasswordRequest
from services import user_service
from util.jwt_util import parse_authorization

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/info")
def get_current_user(authorization: Optional[str] = Header(None, alias="Authorization")):
    """根据 token 返回当前用户信息，与前端 getUserInfo() 对接"""
    user_id = parse_authorization(authorization)
    if user_id is None:
        return error_result(ResultCode.UNAUTHORIZED)
    user = user_service.get_by_id(user_id)
    if not user:
        return error_result(ResultCode.USER_NOT_FOUND)
    return success({
        "id": user.get("id"),
        "username": user.get("username"),
        "realName": user.get("real_name"),
        "role": user.get("role") or "student",
    })


@router.get("/page")
def page(
    page: int = 1,
    size: int = 10,
    keyword: Optional[str] = None,
    departmentId: Optional[int] = None,
    role: Optional[str] = None,
    status: Optional[int] = None,
):
    return success(
        user_service.page(
            page_num=page,
            size=size,
            keyword=keyword,
            department_id=departmentId,
            role=role,
            status=status,
        )
    )


@router.get("/{id}")
def get_by_id(id: int):
    user = user_service.get_by_id(id)
    if not user:
        return error(404, "用户不存在")
    user.pop("password", None)
    return success(user)


@router.post("")
def create(body: UserRequest):
    if not body.username or not body.username.strip():
        return error(400, "用户名不能为空")
    existing = user_service.find_by_username(body.username.strip())
    if existing:
        return error(400, "用户名已存在")
    user_service.save(
        username=body.username.strip(),
        password=body.password,
        real_name=body.real_name,
        email=body.email,
        mobile=body.mobile,
        avatar=body.avatar,
        department_id=body.department_id,
        role=body.role or "student",
        status=body.status if body.status is not None else 1,
    )
    return success()


@router.put("/{id}")
def update(id: int, body: UserRequest):
    user = user_service.get_by_id(id)
    if not user:
        return error(404, "用户不存在")
    if body.username is not None and body.username.strip() != user.get("username"):
        existing = user_service.find_by_username(body.username.strip())
        if existing:
            return error(400, "用户名已存在")
    user_service.update(
        id,
        username=body.username.strip() if body.username else None,
        real_name=body.real_name,
        email=body.email,
        mobile=body.mobile,
        avatar=body.avatar,
        department_id=body.department_id,
        role=body.role,
        status=body.status,
    )
    return success()


@router.delete("/{id}")
def delete(id: int):
    user = user_service.get_by_id(id)
    if not user:
        return error(404, "用户不存在")
    user_service.delete(id)
    return success()


@router.post("/{id}/reset-password")
def reset_password(id: int, body: ResetPasswordRequest):
    user = user_service.get_by_id(id)
    if not user:
        return error(404, "用户不存在")
    user_service.update_password(id, body.password)
    return success()
