# -*- coding: utf-8 -*-
"""知识库路由，与 Java KnowledgeController 对应"""
from typing import List, Optional

from fastapi import APIRouter, Header
from pydantic import BaseModel

from common.result import error, error_result, success
from services import knowledge_service
from util.jwt_util import parse_authorization

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


def _user_id(authorization: Optional[str]) -> Optional[int]:
    return parse_authorization(authorization)


class KnowledgeRequest(BaseModel):
    title: str = ""
    category: Optional[str] = None
    fileName: Optional[str] = None
    fileUrl: str = ""
    fileSize: Optional[int] = None
    fileType: Optional[str] = None
    sort: Optional[int] = 0
    visibility: Optional[int] = 1
    departmentIds: Optional[List[int]] = None


@router.get("/admin/{knowledge_id}")
def get_by_id_admin(knowledge_id: int):
    k = knowledge_service.get_by_id_ignore_visibility(knowledge_id)
    if not k:
        return error_result((404, "资源不存在"))
    return success(k)


@router.get("/page")
def page(
    page: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    return success(
        knowledge_service.page(page_num=page, size=size, keyword=keyword, category=category, user_id=user_id)
    )


@router.get("/{knowledge_id}")
def get_by_id(
    knowledge_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    k = knowledge_service.get_by_id(knowledge_id, user_id)
    if not k:
        return error_result((404, "资源不存在"))
    return success(k)


@router.post("")
def create(body: KnowledgeRequest, authorization: Optional[str] = Header(None, alias="Authorization")):
    title = (body.title or "").strip()
    file_url = (body.fileUrl or "").strip()
    if not title or not file_url:
        return error(400, "标题和文件地址不能为空")
    kid = knowledge_service.save(
        title=title,
        file_url=file_url,
        category=body.category,
        file_name=body.fileName,
        file_size=body.fileSize,
        file_type=body.fileType,
        sort=body.sort or 0,
        visibility=body.visibility or 1,
        department_ids=body.departmentIds,
    )
    return success(kid)


@router.put("/{knowledge_id}")
def update(
    knowledge_id: int,
    body: KnowledgeRequest,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    existing = knowledge_service.get_by_id_ignore_visibility(knowledge_id)
    if not existing:
        return error_result((404, "资源不存在"))
    title = (body.title or "").strip()
    file_url = (body.fileUrl or "").strip()
    if not title or not file_url:
        return error(400, "标题和文件地址不能为空")
    ok = knowledge_service.update(
        knowledge_id=knowledge_id,
        title=title,
        file_url=file_url,
        category=body.category,
        file_name=body.fileName,
        file_size=body.fileSize,
        file_type=body.fileType,
        sort=body.sort or 0,
        visibility=body.visibility or 1,
        department_ids=body.departmentIds,
    )
    if not ok:
        return error(500, "更新失败")
    return success(None)


@router.delete("/{knowledge_id}")
def delete(
    knowledge_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    existing = knowledge_service.get_by_id_ignore_visibility(knowledge_id)
    if not existing:
        return error_result((404, "资源不存在"))
    knowledge_service.delete(knowledge_id)
    return success(None)
