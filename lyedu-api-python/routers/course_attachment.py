# -*- coding: utf-8 -*-
"""课程-知识库关联路由（API 路径保持 /course-attachment 兼容前端）"""
from typing import Optional

from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

from common.result import error, error_result, success
from common.result import ResultCode
from services.course import course_knowledge_service
from services.content import file_service, knowledge_service

router = APIRouter(prefix="/course-attachment", tags=["course-attachment"])


class AttachmentRequest(BaseModel):
    courseId: int
    knowledgeId: int
    sort: Optional[int] = 0


@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    """上传课程附件文件，支持 pdf/doc/docx/txt/xls/xlsx/ppt/pptx/md/csv/zip"""
    result = file_service.upload(file)
    if not result:
        return error(400, "上传失败或文件类型不支持（支持 pdf/doc/docx/txt/xls/xlsx/ppt/pptx/md/csv/zip）")
    return success(result)


@router.get("")
def list_by_course(courseId: int):
    """按课程 ID 查询关联的知识库文件列表"""
    records = course_knowledge_service.list_by_course_id_camel(courseId)
    return success({"records": records})


@router.post("")
def create(body: AttachmentRequest):
    """添加课程-知识库关联"""
    k = knowledge_service.get_by_id_ignore_visibility(body.knowledgeId)
    if not k:
        return error_result((404, "知识库文件不存在"))
    try:
        rid = course_knowledge_service.save(
            course_id=body.courseId,
            knowledge_id=body.knowledgeId,
            sort=body.sort or 0,
        )
        if not rid:
            return error(500, "添加失败，请确认已执行数据库迁移（ly_course_knowledge 表）")
        return success(rid)
    except Exception as e:
        return error(500, f"添加失败: {str(e)[:100]}")


@router.delete("/{id}")
def delete(id: int):
    """删除课程-知识库关联（软删除）"""
    n = course_knowledge_service.delete(id)
    if n == 0:
        return error_result(ResultCode.NOT_FOUND)
    return success()
