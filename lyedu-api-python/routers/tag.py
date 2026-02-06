# -*- coding: utf-8 -*-
"""标签管理路由：标签 CRUD 及关联人员/部门/课程"""
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from common.result import error, success
from services import tag_service

router = APIRouter(prefix="/tag", tags=["tag"])


class TagRequest(BaseModel):
    name: Optional[str] = None
    sort: Optional[int] = 0


class TagEntitiesRequest(BaseModel):
    userIds: Optional[List[int]] = None
    departmentIds: Optional[List[int]] = None
    courseIds: Optional[List[int]] = None


@router.get("/list")
def list_tags():
    """获取全部标签（用于下拉选择等）"""
    return success(tag_service.list_all())


@router.get("/{tag_id}")
def get_tag(tag_id: int):
    tag = tag_service.get_by_id(tag_id)
    if not tag:
        return error(404, "标签不存在")
    return success(tag)


@router.post("")
def create(body: TagRequest):
    name = (body.name or "").strip()
    if not name:
        return error(400, "标签名称不能为空")
    try:
        tag_service.save(name=name, sort=body.sort if body.sort is not None else 0)
    except ValueError as e:
        return error(400, str(e))
    except RuntimeError as e:
        return error(500, str(e))
    return success()


@router.put("/{tag_id}")
def update(tag_id: int, body: TagRequest):
    tag = tag_service.get_by_id(tag_id)
    if not tag:
        return error(404, "标签不存在")
    name = (body.name or "").strip() if body.name is not None else None
    tag_service.update(tag_id, name=name, sort=body.sort)
    return success()


@router.delete("/{tag_id}")
def delete(tag_id: int):
    tag = tag_service.get_by_id(tag_id)
    if not tag:
        return error(404, "标签不存在")
    tag_service.delete(tag_id)
    return success()


@router.get("/{tag_id}/users")
def list_users_by_tag(tag_id: int):
    tag = tag_service.get_by_id(tag_id)
    if not tag:
        return error(404, "标签不存在")
    return success(tag_service.get_users_by_tag(tag_id))


@router.get("/{tag_id}/departments")
def list_departments_by_tag(tag_id: int):
    tag = tag_service.get_by_id(tag_id)
    if not tag:
        return error(404, "标签不存在")
    return success(tag_service.get_departments_by_tag(tag_id))


@router.get("/{tag_id}/courses")
def list_courses_by_tag(tag_id: int):
    tag = tag_service.get_by_id(tag_id)
    if not tag:
        return error(404, "标签不存在")
    return success(tag_service.get_courses_by_tag(tag_id))


@router.put("/{tag_id}/entities")
def set_tag_entities(tag_id: int, body: TagEntitiesRequest):
    """为标签绑定人员/部门/课程（传空列表则清空该类型）"""
    tag = tag_service.get_by_id(tag_id)
    if not tag:
        return error(404, "标签不存在")
    tag_service.set_tag_entities(
        tag_id,
        user_ids=body.userIds,
        department_ids=body.departmentIds,
        course_ids=body.courseIds,
    )
    return success()
