# -*- coding: utf-8 -*-
"""Pydantic request/response schemas, mirroring Java DTOs."""
from typing import Any, List, Optional

from pydantic import BaseModel, Field


# ----- Course -----
class CourseRequest(BaseModel):
    title: Optional[str] = None
    cover: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    status: Optional[int] = 1
    sort: Optional[int] = 0
    is_required: Optional[int] = 0
    visibility: Optional[int] = 1  # 1-公开，0-私有
    department_id: Optional[int] = None  # 私有时必填


class ChapterRequest(BaseModel):
    course_id: Optional[int] = None
    title: Optional[str] = None
    sort: Optional[int] = 0


class VideoRequest(BaseModel):
    course_id: Optional[int] = None
    courseId: Optional[int] = None  # 前端传 camelCase
    chapter_id: Optional[int] = None
    chapterId: Optional[int] = None
    title: Optional[str] = None
    url: Optional[str] = None
    duration: Optional[int] = 0
    sort: Optional[int] = 0


# ----- Learning -----
class JoinCourseRequest(BaseModel):
    course_id: int


class VideoProgressRequest(BaseModel):
    video_id: int
    progress: Optional[int] = 0
    duration: Optional[int] = 0


class PlayPingRequest(BaseModel):
    video_id: int


# ----- Department -----
class DepartmentRequest(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    parentId: Optional[int] = None  # 前端可能传 camelCase
    sort: Optional[int] = 0
    status: Optional[int] = 1


# ----- User -----
class UserRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    real_name: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    avatar: Optional[str] = None
    department_id: Optional[int] = None
    role: Optional[str] = "student"
    status: Optional[int] = 1


class ResetPasswordRequest(BaseModel):
    password: str = Field(..., min_length=1)


# ----- PageResult (for response) -----
def page_result(records: List[Any], total: int, current: int, size: int) -> dict:
    pages = (total + size - 1) // size if size else 0
    return {
        "records": records,
        "total": total,
        "current": current,
        "size": size,
        "pages": pages,
    }
