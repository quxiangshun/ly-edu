# -*- coding: utf-8 -*-
"""积分路由，与 Java PointController 对应"""
from typing import Optional

from fastapi import APIRouter, Header

from common.result import error_result, success
from services import point_service
from util.jwt_util import parse_authorization

router = APIRouter(prefix="/point", tags=["point"])


def _user_id(authorization: Optional[str]) -> Optional[int]:
    return parse_authorization(authorization)


@router.get("/my")
def my_total(authorization: Optional[str] = Header(None, alias="Authorization")):
    user_id = _user_id(authorization)
    if not user_id:
        return error_result((401, "未授权"))
    return success(point_service.get_total_points(user_id))


@router.get("/log")
def my_log(
    page: int = 1,
    size: int = 20,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    if not user_id:
        return error_result((401, "未授权"))
    return success(point_service.list_my_log(user_id, page=page, size=size))


@router.get("/ranking")
def ranking(limit: int = 50, department_id: Optional[int] = None):
    return success(point_service.list_ranking(limit=limit, department_id=department_id))
