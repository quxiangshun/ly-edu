# -*- coding: utf-8 -*-
"""部门路由，与 Java DepartmentController 对应"""
from typing import Optional

from fastapi import APIRouter

from common.result import error, success
from models.schemas import DepartmentRequest
from services.org import department_service
from services.learning import tag_service

router = APIRouter(prefix="/department", tags=["department"])


def _collect_dept_ids(nodes: list) -> list:
    """从树中收集所有部门 id（用于批量查标签，避免 N+1）"""
    ids = []
    for node in nodes or []:
        nid = node.get("id")
        if nid is not None:
            ids.append(nid)
        if node.get("children"):
            ids.extend(_collect_dept_ids(node["children"]))
    return ids


def _apply_tag_ids_to_tree(nodes: list, dept_tag_map: dict) -> None:
    """根据批量查询结果给树节点挂上 tagIds（内存操作，无额外查询）"""
    for node in nodes or []:
        nid = node.get("id")
        node["tagIds"] = dept_tag_map.get(nid, []) if nid is not None else []
        if node.get("children"):
            _apply_tag_ids_to_tree(node["children"], dept_tag_map)


@router.get("/tree")
def tree():
    """获取部门树（含标签）；批量查部门-标签关联，避免 N+1"""
    data = department_service.list_tree()
    dept_ids = _collect_dept_ids(data)
    dept_tag_map = tag_service.list_tag_ids_by_department_batch(dept_ids)
    _apply_tag_ids_to_tree(data, dept_tag_map)
    return success(data)


@router.get("/{id}")
def get_by_id(id: int):
    dept = department_service.get_by_id(id)
    if not dept:
        return error(404, "部门不存在")
    dept["tagIds"] = tag_service.list_tag_ids_by_department(id)
    return success(dept)


@router.post("")
def create(body: DepartmentRequest):
    parent_id = body.parentId if body.parentId is not None else body.parent_id
    new_id = department_service.save(
        name=body.name or "",
        parent_id=parent_id,
        sort=body.sort if body.sort is not None else 0,
        status=body.status if body.status is not None else 1,
    )
    if new_id:
        tag_service.set_tags_for_department(new_id, body.tagIds or body.tag_ids or [])
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
    tag_service.set_tags_for_department(id, body.tagIds or body.tag_ids or [])
    return success()


@router.delete("/{id}")
def delete(id: int):
    department_service.delete(id)
    return success()


