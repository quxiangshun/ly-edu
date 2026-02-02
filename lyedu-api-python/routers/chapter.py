# -*- coding: utf-8 -*-
"""章节路由，与 Java ChapterController 对应"""
from fastapi import APIRouter

from common.result import error_result, success
from models.schemas import ChapterRequest
from services import chapter_service
from common.result import ResultCode

router = APIRouter(prefix="/chapter", tags=["chapter"])


@router.get("")
def list(courseId: int):
    return success(chapter_service.list_by_course_id(courseId))


@router.post("")
def create(body: ChapterRequest):
    if body.course_id is None:
        return error_result(ResultCode.PARAM_ERROR)
    rid = chapter_service.save(
        course_id=body.course_id,
        title=body.title or "",
        sort=body.sort or 0,
    )
    return success(rid)


@router.put("/{id}")
def update(id: int, body: ChapterRequest):
    ch = chapter_service.get_by_id(id)
    if not ch:
        return error_result(ResultCode.NOT_FOUND)
    chapter_service.update(id, title=body.title or "", sort=body.sort or 0)
    return success()


@router.delete("/{id}")
def delete(id: int):
    chapter_service.delete(id)
    return success()
