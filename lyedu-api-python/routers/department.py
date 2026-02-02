# -*- coding: utf-8 -*-
"""部门路由，与 Java DepartmentController 对应"""
from fastapi import APIRouter

from common.result import error, success
from models.schemas import DepartmentRequest
from services import department_service

router = APIRouter(prefix="/department", tags=["department"])


@router.get("/tree")
def tree():
    """获取部门树/列表（全部部门扁平列表）"""
    return success(department_service.list_tree())


@router.get("/{id}")
def get_by_id(id: int):
    dept = department_service.get_by_id(id)
    if not dept:
        return error(404, "部门不存在")
    return success(dept)


@router.post("")
def create(body: DepartmentRequest):
    parent_id = body.parentId if body.parentId is not None else body.parent_id
    department_service.save(
        name=body.name or "",
        parent_id=parent_id,
        sort=body.sort if body.sort is not None else 0,
        status=body.status if body.status is not None else 1,
    )
    return success()


@router.put("/{id}")
def update(id: int, body: DepartmentRequest):
    dept = department_service.get_by_id(id)
    if not dept:
        return error(404, "部门不存在")
    parent_id = body.parentId if body.parentId is not None else body.parent_id
    department_service.update(
        id,
        name=body.name,
        parent_id=parent_id,
        sort=body.sort,
        status=body.status,
    )
    return success()


@router.delete("/{id}")
def delete(id: int):
    department_service.delete(id)
    return success()
