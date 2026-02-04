# -*- coding: utf-8 -*-
"""分片上传路由，与 Java FileUploadController 对应"""
from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel

from common.result import error, success
from services import upload_service

router = APIRouter(prefix="/upload", tags=["upload"])

DEFAULT_CHUNK_SIZE = 5 * 1024 * 1024  # 5MB


class InitUploadRequest(BaseModel):
    fileId: Optional[str] = None
    fileName: str
    fileSize: int
    fileType: Optional[str] = None
    chunkSize: Optional[int] = None


@router.post("/init")
def init_upload(body: InitUploadRequest):
    chunk_size = body.chunkSize or DEFAULT_CHUNK_SIZE
    result = upload_service.init_upload(
        body.fileId,
        body.fileName,
        body.fileSize,
        body.fileType or "video/mp4",
        chunk_size,
    )
    if not result:
        return error(500, "初始化上传失败")
    uploaded = upload_service.get_uploaded_chunks(result["fileId"])
    return success({
        "fileId": result["fileId"],
        "chunkSize": result["chunkSize"],
        "totalChunks": result["totalChunks"],
        "uploadedChunks": uploaded,
    })


@router.get("/progress/{file_id}")
def get_progress(file_id: str):
    result = upload_service.get_progress(file_id)
    if not result:
        return error(404, "Upload record not found")
    uploaded = upload_service.get_uploaded_chunks(file_id)
    total = result["totalChunks"]
    return success({
        "fileId": result["fileId"],
        "fileName": result["fileName"],
        "fileSize": result["fileSize"],
        "totalChunks": total,
        "uploadedChunks": len(uploaded),
        "uploadedChunkIndexes": uploaded,
        "status": result["status"],
        "progress": (len(uploaded) / total * 100) if total else 0,
    })


@router.post("/chunk")
def upload_chunk(
    fileId: str = Form(...),
    chunkIndex: int = Form(...),
    chunkSize: int = Form(...),
    file: UploadFile = File(...),
):
    try:
        content = file.file.read()
    except Exception as e:
        return error(500, "Failed to read chunk: " + str(e))
    try:
        upload_service.upload_chunk(fileId, chunkIndex, chunkSize, content)
        return success()
    except Exception as e:
        return error(500, str(e))


@router.post("/merge/{file_id}")
def merge_chunks(file_id: str):
    try:
        relative_path = upload_service.merge_chunks(file_id)
        return success({
            "fileId": file_id,
            "filePath": relative_path,
            "url": "/uploads/" + relative_path,
        })
    except Exception as e:
        return error(500, "Merge failed: " + str(e))


@router.delete("/{file_id}")
def cancel_upload(file_id: str):
    try:
        upload_service.cancel_upload(file_id)
        return success()
    except Exception as e:
        return error(500, str(e))
