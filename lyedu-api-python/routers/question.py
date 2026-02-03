# -*- coding: utf-8 -*-
"""试题路由，与 Java QuestionController 对应"""
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from common.result import error, error_result, success
from services import question_service

router = APIRouter(prefix="/question", tags=["question"])


class QuestionRequest(BaseModel):
    type: str = ""
    title: str = ""
    options: Optional[str] = None
    answer: Optional[str] = None
    score: Optional[int] = 10
    analysis: Optional[str] = None
    sort: Optional[int] = 0


@router.get("/page")
def page(page: int = 1, size: int = 20, keyword: Optional[str] = None, type: Optional[str] = None):
    return success(question_service.page(page_num=page, size=size, keyword=keyword, type_=type))


@router.get("/{question_id}")
def get_by_id(question_id: int):
    q = question_service.get_by_id(question_id)
    if not q:
        return error_result((404, "资源不存在"))
    return success(q)


@router.post("")
def create(body: QuestionRequest):
    type_ = (body.type or "").strip()
    title = (body.title or "").strip()
    if not type_ or not title:
        return error(400, "题型和标题不能为空")
    qid = question_service.save(
        type_=type_,
        title=title,
        options=body.options,
        answer=body.answer,
        score=body.score or 10,
        analysis=body.analysis,
        sort=body.sort or 0,
    )
    return success(qid)


@router.put("/{question_id}")
def update(question_id: int, body: QuestionRequest):
    existing = question_service.get_by_id(question_id)
    if not existing:
        return error_result((404, "资源不存在"))
    type_ = (body.type or "").strip()
    title = (body.title or "").strip()
    if not type_ or not title:
        return error(400, "题型和标题不能为空")
    ok = question_service.update(
        question_id=question_id,
        type_=type_,
        title=title,
        options=body.options,
        answer=body.answer,
        score=body.score or 10,
        analysis=body.analysis,
        sort=body.sort or 0,
    )
    if not ok:
        return error(500, "更新失败")
    return success(None)


@router.delete("/{question_id}")
def delete(question_id: int):
    existing = question_service.get_by_id(question_id)
    if not existing:
        return error_result((404, "资源不存在"))
    question_service.delete(question_id)
    return success(None)
