# -*- coding: utf-8 -*-
"""部门路由，与 Java DepartmentController 对应（部门可关联多个课程）"""
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from common.result import error, success
from models.schemas import DepartmentRequest
from services import course_department_service
from services import course_service
from services import department_service

router = APIRouter(prefix="/department", tags=["department"])


class DepartmentCoursesRequest(BaseModel):
    courseIds: Optional[List[int]] = None


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


@router.get("/{id}/courses")
def list_courses_by_department_id(id: int):
    dept = department_service.get_by_id(id)
    if not dept:
        return error(404, "部门不存在")
    course_ids = course_department_service.list_course_ids_by_department_id(id)
    if not course_ids:
        return success([])
    list_courses = []
    for cid in course_ids:
        c = course_service.get_by_id_ignore_visibility(cid)
        if c:
            list_courses.append(c)
    return success(list_courses)


@router.post("/{id}/courses")
def add_courses_to_department(id: int, body: DepartmentCoursesRequest):
    dept = department_service.get_by_id(id)
    if not dept:
        return error(404, "部门不存在")
    course_ids = body.courseIds or []
    if course_ids:
        course_department_service.add_courses_to_department(id, course_ids)
    return success()


@router.delete("/{id}/courses/{course_id}")
def remove_course_from_department(id: int, course_id: int):
    dept = department_service.get_by_id(id)
    if not dept:
        return error(404, "部门不存在")
    course_department_service.remove_course_from_department(id, course_id)
    return success()
