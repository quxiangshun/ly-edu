# -*- coding: utf-8 -*-
"""试卷路由，与 Java PaperController 对应"""
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from common.result import error_result, success
from services import paper_service

router = APIRouter(prefix="/paper", tags=["paper"])


class PaperQuestionItem(BaseModel):
    questionId: Optional[int] = None
    score: Optional[int] = 10
    sort: Optional[int] = 0


class PaperRequest(BaseModel):
    title: str = ""
    totalScore: Optional[int] = 100
    passScore: Optional[int] = 60
    durationMinutes: Optional[int] = 60
    status: Optional[int] = 1
    questions: Optional[List[dict]] = None


@router.get("/page")
def page(page: int = 1, size: int = 20, keyword: Optional[str] = None):
    return success(paper_service.page(page_num=page, size=size, keyword=keyword))


@router.get("/{paper_id}")
def get_by_id(paper_id: int):
    p = paper_service.get_by_id(paper_id)
    if not p:
        return error_result((404, "资源不存在"))
    return success(p)


@router.get("/{paper_id}/questions")
def get_questions(paper_id: int):
    items = paper_service.list_questions_by_paper_id(paper_id)
    for item in items:
        q = item.get("question")
        if q:
            q["answer"] = None
            q["analysis"] = None
    return success(items)


@router.post("")
def create(body: PaperRequest):
    title = (body.title or "").strip()
    if not title:
        return error_result((400, "试卷名称不能为空"))
    pid = paper_service.save(
        title=title,
        total_score=body.totalScore or 100,
        pass_score=body.passScore or 60,
        duration_minutes=body.durationMinutes or 60,
        status=body.status or 1,
        questions=body.questions,
    )
    return success(pid)


@router.put("/{paper_id}")
def update(paper_id: int, body: PaperRequest):
    existing = paper_service.get_by_id(paper_id)
    if not existing:
        return error_result((404, "资源不存在"))
    title = (body.title or "").strip()
    if not title:
        return error_result((400, "试卷名称不能为空"))
    ok = paper_service.update(
        paper_id=paper_id,
        title=title,
        total_score=body.totalScore or 100,
        pass_score=body.passScore or 60,
        duration_minutes=body.durationMinutes or 60,
        status=body.status or 1,
        questions=body.questions,
    )
    if not ok:
        return error_result((500, "更新失败"))
    return success(None)


@router.delete("/{paper_id}")
def delete(paper_id: int):
    existing = paper_service.get_by_id(paper_id)
    if not existing:
        return error_result((404, "资源不存在"))
    paper_service.delete(paper_id)
    return success(None)
