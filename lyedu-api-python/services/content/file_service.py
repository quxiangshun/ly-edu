# -*- coding: utf-8 -*-
"""知识库文件上传服务：按内容哈希去重，同内容只保留一份物理文件"""
from datetime import datetime
from typing import Optional

import db
from config import UPLOAD_PATH
from util.upload_util import get_chunk_hash

# 知识库常用文档类型
ALLOWED_EXT = {"pdf", "doc", "docx", "txt", "xls", "xlsx", "ppt", "pptx", "md", "csv", "zip"}

SELECT_BY_HASH = "SELECT relative_path, file_size FROM ly_file_hash WHERE content_hash = %s LIMIT 1"
INSERT_FILE_HASH = "INSERT INTO ly_file_hash (content_hash, relative_path, file_size) VALUES (%s, %s, %s)"
UPDATE_FILE_HASH_PATH = "UPDATE ly_file_hash SET relative_path = %s WHERE content_hash = %s"


def _ext(name: str) -> str:
    i = name.rfind(".")
    return name[i + 1 :].lower() if i > 0 else ""


def _ym_path(prefix: str) -> str:
    """生成 年/月 路径，如 files/2025/02"""
    now = datetime.now()
    return f"{prefix}/{now.year}/{now.month:02d}"


def upload(file) -> Optional[dict]:
    """
    上传文件：按内容 SHA256 去重，同名/改名只保留一份物理文件。
    若内容已存在则仅返回已有 url，不重复存储。
    """
    if not file or not file.filename:
        return None
    name = file.filename
    ext = _ext(name)
    if ext not in ALLOWED_EXT:
        return None
    try:
        content = file.file.read()
    except Exception:
        return None
    file_size = len(content)
    content_hash = get_chunk_hash(content).lower()
    storage_rel = f"{_ym_path('files')}/{content_hash}.{ext}"
    full_path = UPLOAD_PATH / storage_rel
    try:
        existing = db.query_one(SELECT_BY_HASH, (content_hash,))
        if existing:
            old_path = existing["relative_path"]
            old_full = UPLOAD_PATH / old_path
            if old_full.is_file():
                url = "/uploads/" + old_path.lstrip("/")
                return {
                    "url": url,
                    "path": old_path,
                    "fileName": name,
                    "fileSize": existing.get("file_size") or file_size,
                    "fileType": ext,
                }
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_bytes(content)
            db.execute(UPDATE_FILE_HASH_PATH, (storage_rel, content_hash))
        else:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_bytes(content)
            db.execute(INSERT_FILE_HASH, (content_hash, storage_rel, file_size))
        url = "/uploads/" + storage_rel.lstrip("/")
        return {
            "url": url,
            "path": storage_rel,
            "fileName": name,
            "fileSize": file_size,
            "fileType": ext,
        }
    except Exception:
        return None
