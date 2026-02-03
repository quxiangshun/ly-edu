# -*- coding: utf-8 -*-
"""考试任务路由，与 Java ExamController 对应"""
from typing import List, Optional

from fastapi import APIRouter, Header
from pydantic import BaseModel

from common.result import error_result, success
from services import exam_service
from util.jwt_util import parse_authorization

router = APIRouter(prefix="/exam", tags=["exam"])


def _user_id(authorization: Optional[str]) -> Optional[int]:
    return parse_authorization(authorization)


class ExamRequest(BaseModel):
    title: str = ""
    paperId: Optional[int] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    durationMinutes: Optional[int] = None
    passScore: Optional[int] = None
    visibility: Optional[int] = 1
    status: Optional[int] = 1
    departmentIds: Optional[List[int]] = None


def _parse_datetime(s: Optional[str]):
    if not s:
        return None
    try:
        from datetime import datetime
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


@router.get("/admin/{exam_id}")
def get_by_id_admin(exam_id: int):
    e = exam_service.get_by_id_ignore_visibility(exam_id)
    if not e:
        return error_result((404, "资源不存在"))
    return success(e)


@router.get("/page")
def page(
    page: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    return success(exam_service.page(page_num=page, size=size, keyword=keyword, user_id=user_id))


@router.get("/{exam_id}")
def get_by_id(
    exam_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    e = exam_service.get_by_id(exam_id, user_id)
    if not e:
        return error_result((404, "资源不存在"))
    return success(e)


@router.post("")
def create(body: ExamRequest):
    title = (body.title or "").strip()
    if not title or body.paperId is None:
        return error_result((400, "考试名称和试卷不能为空"))
    eid = exam_service.save(
        title=title,
        paper_id=body.paperId,
        start_time=_parse_datetime(body.startTime),
        end_time=_parse_datetime(body.endTime),
        duration_minutes=body.durationMinutes,
        pass_score=body.passScore,
        visibility=body.visibility or 1,
        status=body.status or 1,
        department_ids=body.departmentIds,
    )
    return success(eid)


@router.put("/{exam_id}")
def update(exam_id: int, body: ExamRequest):
    existing = exam_service.get_by_id_ignore_visibility(exam_id)
    if not existing:
        return error_result((404, "资源不存在"))
    title = (body.title or "").strip()
    if not title or body.paperId is None:
        return error_result((400, "考试名称和试卷不能为空"))
    ok = exam_service.update(
        exam_id=exam_id,
        title=title,
        paper_id=body.paperId,
        start_time=_parse_datetime(body.startTime),
        end_time=_parse_datetime(body.endTime),
        duration_minutes=body.durationMinutes,
        pass_score=body.passScore,
        visibility=body.visibility or 1,
        status=body.status or 1,
        department_ids=body.departmentIds,
    )
    if not ok:
        return error_result((500, "更新失败"))
    return success(None)


@router.delete("/{exam_id}")
def delete(exam_id: int):
    existing = exam_service.get_by_id_ignore_visibility(exam_id)
    if not existing:
        return error_result((404, "资源不存在"))
    exam_service.delete(exam_id)
    return success(None)
