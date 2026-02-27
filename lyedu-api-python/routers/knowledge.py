# -*- coding: utf-8 -*-
"""知识库路由，与 Java KnowledgeController 对应"""
from typing import List, Optional

import pymysql
from fastapi import APIRouter, File, Header, UploadFile
from loguru import logger
from pydantic import BaseModel

import db
from common.result import error, error_result, success
from services.content import file_service, knowledge_service
from util.jwt_util import parse_authorization

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# 知识库表建表 SQL（与 v1_init_schema 一致，用于表不存在时自动创建）
_CREATE_LY_KNOWLEDGE = """
CREATE TABLE IF NOT EXISTS ly_knowledge (
    id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    title VARCHAR(200) NOT NULL COMMENT '标题/名称',
    category VARCHAR(100) DEFAULT NULL COMMENT '分类',
    file_name VARCHAR(255) DEFAULT NULL COMMENT '文件名',
    file_url VARCHAR(500) NOT NULL COMMENT '文件地址',
    file_size BIGINT DEFAULT NULL COMMENT '文件大小（字节）',
    file_type VARCHAR(50) DEFAULT NULL COMMENT '文件类型/扩展名',
    sort INT DEFAULT 0 COMMENT '排序',
    visibility TINYINT DEFAULT 1 COMMENT '可见性：1-公开，0-私有',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT DEFAULT 0,
    PRIMARY KEY (id),
    KEY idx_category (category),
    KEY idx_sort (sort)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库表'
"""


def _user_id(authorization: Optional[str]) -> Optional[int]:
    return parse_authorization(authorization)


class KnowledgeRequest(BaseModel):
    title: str = ""
    category: Optional[str] = None
    fileName: Optional[str] = None
    fileUrl: str = ""
    fileSize: Optional[int] = None
    fileType: Optional[str] = None
    sort: Optional[int] = 0
    visibility: Optional[int] = 1
    departmentIds: Optional[List[int]] = None


@router.get("/admin/{knowledge_id}")
def get_by_id_admin(knowledge_id: int):
    k = knowledge_service.get_by_id_ignore_visibility(knowledge_id)
    if not k:
        return error_result((404, "资源不存在"))
    return success(k)


@router.get("/page")
def page(
    page: int = 1,
    size: int = 20,
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    return success(
        knowledge_service.page(page_num=page, size=size, keyword=keyword, category=category, user_id=user_id)
    )


@router.get("/{knowledge_id}")
def get_by_id(
    knowledge_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    user_id = _user_id(authorization)
    k = knowledge_service.get_by_id(knowledge_id, user_id)
    if not k:
        return error_result((404, "资源不存在"))
    return success(k)


@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    """上传知识库文件，按内容哈希去重，同内容只保留一份；同时创建知识库记录以便在知识库中显示"""
    result = file_service.upload(file)
    if not result:
        return error(400, "上传失败或文件类型不支持（支持 pdf/doc/docx/txt/xls/xlsx/ppt/pptx/md/csv/zip）")
    # 创建知识库记录，使上传的文件在知识库中显示（若该 file_url 已存在则跳过，避免重复）
    file_url = result.get("url") or ("/uploads/" + (result.get("path") or "").lstrip("/"))
    title = result.get("fileName") or "未命名文件"
    knowledge_saved = True

    def _save_to_knowledge(retry_after_create: bool = False) -> tuple:
        """尝试写入知识库，返回 (success: bool, knowledge_id: int|None)"""
        try:
            existing = db.query_one(
                "SELECT id FROM ly_knowledge WHERE file_url = %s AND deleted = 0 LIMIT 1",
                (file_url,),
            )
            if not existing:
                kid = knowledge_service.save(
                    title=title,
                    file_url=file_url,
                    file_name=result.get("fileName"),
                    file_size=result.get("fileSize"),
                    file_type=result.get("fileType"),
                    sort=0,
                    visibility=1,
                )
                knowledge_id = kid if kid else None
            else:
                knowledge_id = existing.get("id")
            return (True, knowledge_id)
        except pymysql.err.MySQLError as e:
            err_code = getattr(e, "args", (None,))[0]
            if err_code == 1146 and not retry_after_create:  # Table doesn't exist
                logger.warning("ly_knowledge 表不存在，尝试自动创建: {}", e)
                try:
                    db.execute(_CREATE_LY_KNOWLEDGE)
                    logger.info("ly_knowledge 表已创建，重试写入")
                    return _save_to_knowledge(retry_after_create=True)
                except Exception as create_e:
                    logger.exception("创建 ly_knowledge 表失败: {}", create_e)
                    return (False, None)
            logger.exception("知识库记录创建失败 (code={}): {}", err_code, e)
            return (False, None)
        except Exception as e:
            logger.exception("知识库记录创建失败: {}", e)
            return (False, None)

    knowledge_saved, knowledge_id = _save_to_knowledge()
    result["knowledgeSaved"] = knowledge_saved
    result["knowledgeId"] = knowledge_id
    return success(result)


@router.post("")
def create(body: KnowledgeRequest, authorization: Optional[str] = Header(None, alias="Authorization")):
    title = (body.title or "").strip()
    file_url = (body.fileUrl or "").strip()
    if not title or not file_url:
        return error(400, "标题和文件地址不能为空")
    kid = knowledge_service.save(
        title=title,
        file_url=file_url,
        category=body.category,
        file_name=body.fileName,
        file_size=body.fileSize,
        file_type=body.fileType,
        sort=body.sort or 0,
        visibility=body.visibility or 1,
        department_ids=body.departmentIds,
    )
    return success(kid)


@router.put("/{knowledge_id}")
def update(
    knowledge_id: int,
    body: KnowledgeRequest,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    existing = knowledge_service.get_by_id_ignore_visibility(knowledge_id)
    if not existing:
        return error_result((404, "资源不存在"))
    title = (body.title or "").strip()
    file_url = (body.fileUrl or "").strip()
    if not title or not file_url:
        return error(400, "标题和文件地址不能为空")
    ok = knowledge_service.update(
        knowledge_id=knowledge_id,
        title=title,
        file_url=file_url,
        category=body.category,
        file_name=body.fileName,
        file_size=body.fileSize,
        file_type=body.fileType,
        sort=body.sort or 0,
        visibility=body.visibility or 1,
        department_ids=body.departmentIds,
    )
    if not ok:
        return error(500, "更新失败")
    return success(None)


@router.delete("/{knowledge_id}")
def delete(
    knowledge_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    existing = knowledge_service.get_by_id_ignore_visibility(knowledge_id)
    if not existing:
        return error_result((404, "资源不存在"))
    knowledge_service.delete(knowledge_id)
    return success(None)
