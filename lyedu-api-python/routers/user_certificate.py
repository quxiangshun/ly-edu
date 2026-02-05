# -*- coding: utf-8 -*-
"""用户证书记录路由，与 Java UserCertificateController 对应"""
from typing import Optional

from fastapi import APIRouter, Header

from common.result import error_result, success
from services import certificate_template_service
from services import user_certificate_service
from util.jwt_util import parse_authorization

router = APIRouter(prefix="/user-certificate", tags=["user-certificate"])


def _user_id(authorization: Optional[str]) -> Optional[int]:
    return parse_authorization(authorization)


@router.get("/my")
def my_list(authorization: Optional[str] = Header(None, alias="Authorization")):
    user_id = _user_id(authorization)
    if not user_id:
        return error_result((401, "未授权"))
    return success(user_certificate_service.list_by_user_id(user_id))


@router.get("/admin/user/{uid}")
def list_by_user_id(uid: int):
    return success(user_certificate_service.list_by_user_id(uid))


@router.get("/page")
def page(
    page: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    userId: Optional[int] = None,
    certificateId: Optional[int] = None,
):
    """分页查询用户证书（管理员）"""
    return success(user_certificate_service.page(page_num=page, size=size, keyword=keyword, user_id=userId, certificate_id=certificateId))


@router.get("/{uc_id}")
def get_by_id(
    uc_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    uc = user_certificate_service.get_by_id(uc_id)
    if not uc:
        return error_result((404, "资源不存在"))
    if not user_id:
        return error_result((401, "未授权"))
    if uc.get("userId") != user_id:
        return error_result((403, "禁止访问"))
    template = certificate_template_service.get_by_id(uc.get("templateId"))
    return success({"userCertificate": uc, "template": template})
