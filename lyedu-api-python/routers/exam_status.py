# -*- coding: utf-8 -*-
"""考试状态查询：支持固定时间/无限制"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Header

from common.result import error_result, success
from services import exam_service
from util.jwt_util import parse_authorization

router = APIRouter(prefix="/exam-status", tags=["exam-status"])


def _now_utc():
    return datetime.now(timezone.utc)


@router.get("/{exam_id}")
def get_status(exam_id: int, authorization: Optional[str] = Header(None, alias="Authorization")):
    user_id = parse_authorization(authorization)
    exam = exam_service.get_by_id(exam_id, user_id)
    if not exam:
        return error_result((404, "考试不存在或无权查看"))
    start = exam.get("startTime")
    end = exam.get("endTime")
    duration = exam.get("durationMinutes")
    now = _now_utc()

    # start/end 可能是 datetime 或 None
    def _as_dt(v):
        return v if isinstance(v, datetime) else None

    start_dt = _as_dt(start)
    end_dt = _as_dt(end)

    unlimited = (start_dt is None and end_dt is None)
    can_start = True
    status = "ready"
    message = ""
    if not unlimited:
        if start_dt and now < start_dt:
            can_start = False
            status = "not_started"
            message = "考试未开始"
        elif end_dt and now > end_dt:
            can_start = False
            status = "ended"
            message = "考试已结束"

    return success(
        {
            "examId": exam_id,
            "canStart": can_start,
            "status": status,
            "message": message,
            "startTime": start_dt,
            "endTime": end_dt,
            "durationMinutes": duration,
            "unlimited": unlimited,
        }
    )
