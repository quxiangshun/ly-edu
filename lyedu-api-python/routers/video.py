# -*- coding: utf-8 -*-
"""视频路由：管理 + 播放次数/点赞（H5 用）"""
from typing import Optional, List
from fastapi import APIRouter, Header
from pydantic import BaseModel
from common.result import error, success, error_result
from common.result import ResultCode
from models.schemas import VideoRequest
from services import video_service
from util.jwt_util import parse_authorization

router = APIRouter(prefix="/video", tags=["video"])


def _uid(authorization: Optional[str]) -> Optional[int]:
    return parse_authorization(authorization)


@router.get("/page")
def page(page: int = 1, size: int = 10, courseId: Optional[int] = None, keyword: Optional[str] = None):
    return success(video_service.page(page_num=page, size=size, course_id=courseId, keyword=keyword))


@router.get("/course/{courseId}")
def list_by_course(courseId: int, authorization: Optional[str] = Header(None, alias="Authorization")):
    uid = _uid(authorization)
    return success(video_service.list_by_course_id(courseId, user_id=uid))


@router.get("/chapter/{chapterId}")
def list_by_chapter(chapterId: int, authorization: Optional[str] = Header(None, alias="Authorization")):
    uid = _uid(authorization)
    return success(video_service.list_by_chapter_id(chapterId, user_id=uid))


@router.get("/liked")
def list_liked(
    page: int = 1,
    size: int = 10,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """我点赞的视频，分页（H5 滚动加载）"""
    uid = _uid(authorization)
    if uid is None:
        return error_result(ResultCode.UNAUTHORIZED)
    return success(video_service.list_liked_by_user(uid, page_num=page, size=size))


@router.get("/{id}")
def get_by_id(id: int, authorization: Optional[str] = Header(None, alias="Authorization")):
    uid = _uid(authorization)
    video = video_service.get_by_id(id, user_id=uid)
    if not video:
        return error(404, "视频不存在")
    video["playCount"] = video.get("play_count", 0)
    video["likeCount"] = video.get("like_count", 0)
    video["courseId"] = video.get("course_id")
    return success(video)


@router.post("/{id}/play")
def record_play(id: int):
    """记录播放次数（只要播放就+1，H5 在开始播放时调用一次）"""
    video_service.record_play(id)
    return success()


@router.post("/{id}/like")
def like(id: int, authorization: Optional[str] = Header(None, alias="Authorization")):
    """点赞，一人只能点一次"""
    uid = _uid(authorization)
    if uid is None:
        return error_result(ResultCode.UNAUTHORIZED)
    if video_service.like(id, uid):
        return success()
    return success({"message": "已点赞"})


@router.delete("/{id}/like")
def unlike(id: int, authorization: Optional[str] = Header(None, alias="Authorization")):
    """取消点赞"""
    uid = _uid(authorization)
    if uid is None:
        return error_result(ResultCode.UNAUTHORIZED)
    video_service.unlike(id, uid)
    return success()

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


class VideoCoursesRequest(BaseModel):
    courseIds: Optional[List[int]] = None
