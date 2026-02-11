# -*- coding: utf-8 -*-
"""Pydantic request/response schemas, mirroring Java DTOs."""
from typing import Any, List, Optional

from pydantic import BaseModel, Field, root_validator


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
    department_ids: Optional[List[int]] = None  # 关联部门ID列表（私有时必填，可多选）
    tag_ids: Optional[List[int]] = None
    tagIds: Optional[List[int]] = None


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
    cover: Optional[str] = None
    duration: Optional[int] = 0
    sort: Optional[int] = 0


# ----- Learning -----
class JoinCourseRequest(BaseModel):
    course_id: int


class VideoProgressRequest(BaseModel):
    video_id: Optional[int] = None
    videoId: Optional[int] = None  # 前端传 camelCase
    progress: Optional[int] = 0
    duration: Optional[int] = 0

    def get_video_id(self) -> Optional[int]:
        return self.video_id if self.video_id is not None else self.videoId


class PlayPingRequest(BaseModel):
    video_id: Optional[int] = None
    videoId: Optional[int] = None  # 前端传 camelCase

    def get_video_id(self) -> Optional[int]:
        return self.video_id if self.video_id is not None else self.videoId


# ----- Department -----
class DepartmentRequest(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    parentId: Optional[int] = None  # 前端可能传 camelCase
    sort: Optional[int] = 0
    status: Optional[int] = 1
    tag_ids: Optional[List[int]] = None
    tagIds: Optional[List[int]] = None


# ----- User -----
class UserRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    real_name: Optional[str] = None
    nickname: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    avatar: Optional[str] = None
    union_id: Optional[str] = None
    unionId: Optional[str] = None  # 前端驼峰，兼容处理
    department_id: Optional[int] = None
    departmentId: Optional[int] = None  # 前端使用的驼峰命名，兼容处理
    entry_date: Optional[str] = None  # YYYY-MM-DD
    entryDate: Optional[str] = None  # 前端使用的驼峰命名，兼容处理
    role: Optional[str] = "student"
    status: Optional[int] = 1
    tag_ids: Optional[List[int]] = None
    tagIds: Optional[List[int]] = None  # 前端驼峰，兼容处理

    @root_validator(pre=True)
    def convert_camel_case(cls, values):
        # 统一处理：如果前端传了驼峰命名，转换为下划线命名
        if isinstance(values, dict):
            if 'departmentId' in values and 'department_id' not in values:
                values['department_id'] = values.get('departmentId')
            if 'entryDate' in values and 'entry_date' not in values:
                values['entry_date'] = values.get('entryDate')
            if 'unionId' in values and 'union_id' not in values:
                values['union_id'] = values.get('unionId')
            if 'tagIds' in values and 'tag_ids' not in values:
                values['tag_ids'] = values.get('tagIds')
        return values


class ResetPasswordRequest(BaseModel):
    password: str = Field(..., min_length=1)


# ----- Feishu Sync（飞书同步，与 docs/飞书同步.md 一致） -----
class FeishuSyncRequest(BaseModel):
    """飞书同步请求：是否同步部门/用户，是否覆盖已存在"""
    sync_departments: bool = Field(True, description="是否同步部门")
    sync_users: bool = Field(True, description="是否同步用户")
    overwrite_existing: bool = Field(False, description="是否覆盖已存在的数据")


class FeishuSyncStats(BaseModel):
    """飞书同步统计"""
    departments_created: int = 0
    departments_updated: int = 0
    departments_skipped: int = 0
    departments_failed: int = 0
    users_created: int = 0
    users_updated: int = 0
    users_skipped: int = 0
    users_failed: int = 0


class FeishuSyncResponse(BaseModel):
    """飞书同步响应：统计 + 错误列表"""
    success: bool = True
    message: str = "同步完成"
    stats: Optional[FeishuSyncStats] = None
    departments: Optional[dict] = None
    users: Optional[dict] = None
    errors: List[str] = Field(default_factory=list)


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
