# -*- coding: utf-8 -*-
"""考试记录路由，与 Java ExamRecordController 对应"""
from typing import Optional

from fastapi import APIRouter, Header
from pydantic import BaseModel

from common.result import error_result, success
from services import exam_record_service
from util.jwt_util import parse_authorization

router = APIRouter(prefix="/exam-record", tags=["exam-record"])


def _user_id(authorization: Optional[str]) -> Optional[int]:
    return parse_authorization(authorization)


class SubmitRequest(BaseModel):
    examId: Optional[int] = None
    answers: Optional[str] = None


@router.post("/submit")
def submit(
    body: SubmitRequest,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    if not user_id:
        return error_result((401, "未授权"))
    if body.examId is None:
        return error_result((400, "考试ID不能为空"))
    r = exam_record_service.submit(body.examId, user_id, body.answers)
    if not r:
        return error_result((500, "交卷失败"))
    return success(r)


@router.get("/my")
def my_records(authorization: Optional[str] = Header(None, alias="Authorization")):
    user_id = _user_id(authorization)
    if not user_id:
        return error_result((401, "未授权"))
    return success(exam_record_service.list_by_user_id(user_id))


@router.get("/exam/{exam_id}")
def list_by_exam(exam_id: int):
    return success(exam_record_service.list_by_exam_id(exam_id))


@router.get("/exam/{exam_id}/user/{user_id}")
def get_by_exam_and_user(exam_id: int, user_id: int):
    r = exam_record_service.get_by_exam_and_user(exam_id, user_id)
    return success(r)


@router.get("/page")
def page(
    page: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    examId: Optional[int] = None,
    userId: Optional[int] = None,
):
    """分页查询考试记录（管理员）"""
    return success(exam_record_service.page(page_num=page, size=size, keyword=keyword, exam_id=examId, user_id=userId))
