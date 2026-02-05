# -*- coding: utf-8 -*-
"""课程评论管理路由（后台管理）"""
from typing import Optional

from fastapi import APIRouter, Header

from common.result import error, success
from services import course_comment_service
from util.jwt_util import parse_authorization


router = APIRouter(prefix="/course-comment", tags=["course-comment"])


def _user_id(authorization: Optional[str]) -> Optional[int]:
    """从Authorization header中提取用户ID"""
    return parse_authorization(authorization)


@router.get("/page")
def comment_page(
    page: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    courseId: Optional[int] = None,
    status: Optional[int] = None,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """分页查询评论（管理员）"""
    if not _user_id(authorization):
        return error(401, "请先登录")
    result = course_comment_service.page(page, size, keyword, courseId, status)
    return success(result)


@router.get("/{comment_id}")
def get_comment(
    comment_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """获取评论详情（管理员）"""
    if not _user_id(authorization):
        return error(401, "请先登录")
    comment = course_comment_service.get_by_id(comment_id)
    if not comment:
        return error(404, "评论不存在")
    return success(comment)


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """删除评论（假删除，管理员）"""
    if not _user_id(authorization):
        return error(401, "请先登录")
    n = course_comment_service.delete(comment_id)
    if n == 0:
        return error(404, "评论不存在")
    return success(None)


@router.put("/{comment_id}/status")
def update_comment_status(
    comment_id: int,
    status: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """更新评论状态（0-隐藏，1-显示）"""
    if not _user_id(authorization):
        return error(401, "请先登录")
    if status not in [0, 1]:
        return error(400, "状态值无效")
    n = course_comment_service.update_status(comment_id, status)
    if n == 0:
        return error(404, "评论不存在")
    return success(None)
