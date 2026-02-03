# -*- coding: utf-8 -*-
"""课程路由，与 Java CourseController 对应"""
from typing import Optional

from fastapi import APIRouter, Header
from pydantic import BaseModel

from common.result import error, error_result, success
from models.schemas import CourseRequest
from services import course_service
from services import chapter_service
from services import video_service
from services import user_video_progress_service
from services import user_course_service
from services import course_attachment_service
from services import course_comment_service
from util.jwt_util import parse_authorization

router = APIRouter(prefix="/course", tags=["course"])


class CommentRequest(BaseModel):
    chapterId: Optional[int] = None
    parentId: Optional[int] = None
    content: str = ""


def _user_id(authorization: Optional[str]) -> Optional[int]:
    return parse_authorization(authorization)


@router.get("/page")
def page(
    page: int = 1,
    size: int = 10,
    keyword: Optional[str] = None,
    categoryId: Optional[int] = None,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    return success(
        course_service.page(page_num=page, size=size, keyword=keyword, category_id=categoryId, user_id=user_id)
    )


@router.get("/recommended")
def recommended(
    limit: int = 6,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    return success(course_service.list_recommended(limit=limit, user_id=user_id))


@router.get("/{course_id}/comment")
def comment_list(course_id: int, chapterId: Optional[int] = None):
    return success(course_comment_service.list_by_course(course_id, chapterId))


@router.post("/{course_id}/comment")
def comment_add(
    course_id: int,
    body: CommentRequest,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    if not user_id:
        return error(401, "请先登录")
    content = (body.content or "").strip()
    if not content:
        return error(400, "评论内容不能为空")
    comment = course_comment_service.add(
        course_id, user_id, content,
        chapter_id=body.chapterId,
        parent_id=body.parentId,
    )
    if not comment:
        return error(500, "发表失败")
    return success(comment)


@router.delete("/comment/{comment_id}")
def comment_delete(
    comment_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    if not _user_id(authorization):
        return error(401, "请先登录")
    course_comment_service.delete(comment_id)
    return success(None)


@router.get("/{id}")
def get_by_id(id: int, authorization: Optional[str] = Header(None, alias="Authorization")):
    user_id = _user_id(authorization)
    course = course_service.get_detail_by_id(id, user_id=user_id)
    if not course:
        return error(404, "课程不存在")
    chapters = chapter_service.list_by_course_id(id)
    videos = video_service.list_by_course_id(id)
    chapter_items = []
    for ch in chapters:
        hours = [v for v in videos if v.get("chapter_id") == ch["id"]]
        chapter_items.append(
            {"id": ch["id"], "title": ch["title"], "sort": ch["sort"], "hours": hours}
        )
    uncategorized = [v for v in videos if v.get("chapter_id") is None]
    if uncategorized:
        chapter_items.append(
            {"id": None, "title": "未分类", "sort": 999999, "hours": uncategorized}
        )
    attachments = course_attachment_service.list_by_course_id(id)
    detail = {
        "course": course,
        "videos": videos,
        "chapters": chapter_items,
        "attachments": attachments,
    }
    user_id = _user_id(authorization)
    if user_id and videos:
        video_ids = [v["id"] for v in videos]
        progress_map = user_video_progress_service.get_progress_map(user_id, video_ids)
        learn_record = {
            vid: {"progress": p["progress"], "duration": p["duration"]}
            for vid, p in progress_map.items()
        }
        detail["learnRecord"] = learn_record
        total_duration = 0
        finished_duration = 0
        for v in videos:
            d = v.get("duration") or 0
            if d <= 0:
                continue
            total_duration += d
            p = progress_map.get(v["id"])
            if p and p.get("progress") is not None:
                finished_duration += min(p["progress"], d)
        course_progress = (
            int(finished_duration * 100 / total_duration) if total_duration > 0 else 0
        )
        course_progress = min(100, course_progress)
        uc = user_course_service.get_by_user_and_course(user_id, id)
        if uc and (uc.get("progress") or 0) > course_progress:
            course_progress = uc["progress"]
        detail["courseProgress"] = course_progress
    return success(detail)


@router.post("")
def create(body: CourseRequest):
    course_service.save(
        title=body.title,
        cover=body.cover,
        description=body.description,
        category_id=body.category_id,
        status=body.status or 1,
        sort=body.sort or 0,
        is_required=body.is_required or 0,
        visibility=body.visibility if body.visibility is not None else 1,
        department_ids=body.department_ids,
    )
    return success()


@router.put("/{id}")
def update(id: int, body: CourseRequest):
    course = course_service.get_by_id_ignore_visibility(id)
    if not course:
        return error(404, "课程不存在")
    course_service.update(
        id,
        title=body.title,
        cover=body.cover,
        description=body.description,
        category_id=body.category_id,
        status=body.status,
        sort=body.sort,
        is_required=body.is_required,
        visibility=body.visibility if body.visibility is not None else 1,
        department_ids=body.department_ids,
    )
    return success()


@router.delete("/{id}")
def delete(id: int):
    course_service.delete(id)
    return success()
