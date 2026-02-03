# -*- coding: utf-8 -*-
"""图片库路由，与 Java ImageController 对应"""
from typing import Optional

from fastapi import APIRouter, File, UploadFile

from common.result import success
from services import image_service

router = APIRouter(prefix="/image", tags=["image"])


@router.post("/upload")
def upload_image(file: UploadFile = File(...)):
    result = image_service.upload(file)
    if not result:
        return {"code": 400, "message": "上传失败或非图片类型"}
    return success(result)


@router.get("/page")
def page(page: int = 1, size: int = 20, keyword: Optional[str] = None):
    return success(image_service.page(page_num=page, size=size, keyword=keyword))


@router.delete("/{image_id}")
def delete_image(image_id: int):
    image_service.delete_by_id(image_id)
    return success()
