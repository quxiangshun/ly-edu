# -*- coding: utf-8 -*-
"""视频路由，与 Java VideoController 对应"""
from typing import Optional
from fastapi import APIRouter
from common.result import error, success
from models.schemas import VideoRequest
from services import video_service

router = APIRouter(prefix="/video", tags=["video"])

@router.get("/page")
def page(page: int = 1, size: int = 10, courseId: Optional[int] = None, keyword: Optional[str] = None):
    return success(video_service.page(page_num=page, size=size, course_id=courseId, keyword=keyword))

@router.get("/course/{courseId}")
def list_by_course(courseId: int):
    return success(video_service.list_by_course_id(courseId))

@router.get("/chapter/{chapterId}")
def list_by_chapter(chapterId: int):
    return success(video_service.list_by_chapter_id(chapterId))

@router.get("/{id}")
def get_by_id(id: int):
    video = video_service.get_by_id(id)
    if not video:
        return error(404, "视频不存在")
    return success(video)

def _course_chapter_from_body(body: VideoRequest, fallback_course_id=None, fallback_chapter_id=None):
    """前端可能传 courseId/chapterId (camelCase)，统一取出 course_id、chapter_id"""
    course_id = body.course_id if body.course_id is not None else body.courseId
    chapter_id = body.chapter_id if body.chapter_id is not None else body.chapterId
    if course_id is None:
        course_id = fallback_course_id
    if chapter_id is None:
        chapter_id = fallback_chapter_id
    return course_id, chapter_id


@router.post("")
def create(body: VideoRequest):
    course_id, chapter_id = _course_chapter_from_body(body)
    if course_id is None:
        course_id = 0
    video_service.save(
        course_id=course_id,
        chapter_id=chapter_id,
        title=body.title or "",
        url=body.url or "",
        cover=body.cover,
        duration=body.duration or 0,
        sort=body.sort or 0,
    )
    return success()

@router.put("/{id}")
def update(id: int, body: VideoRequest):
    video = video_service.get_by_id(id)
    if not video:
        return error(404, "视频不存在")
    course_id, chapter_id = _course_chapter_from_body(
        body,
        fallback_course_id=video.get("course_id"),
        fallback_chapter_id=video.get("chapter_id"),
    )
    if course_id is None:
        course_id = video.get("course_id") or 0
    video_service.update(
        id,
        course_id=course_id,
        chapter_id=chapter_id,
        title=body.title or "",
        url=body.url or "",
        cover=body.cover,
        duration=body.duration or 0,
        sort=body.sort or 0,
    )
    return success()

@router.delete("/{id}")
def delete(id: int):
    video_service.delete(id)
    return success()
