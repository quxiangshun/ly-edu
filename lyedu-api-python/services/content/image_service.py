# -*- coding: utf-8 -*-
"""图片库服务：按内容哈希去重，不论文件名只保留一份"""
from typing import Any, List, Optional

import pymysql

import db
from config import UPLOAD_PATH
from util.upload_util import get_chunk_hash

ALLOWED_EXT = {"jpg", "jpeg", "png", "gif", "webp"}
SELECT_BY_HASH = "SELECT relative_path FROM ly_file_hash WHERE content_hash = %s LIMIT 1"
INSERT_FILE_HASH = "INSERT INTO ly_file_hash (content_hash, relative_path, file_size) VALUES (%s, %s, %s)"


def _ext(name: str) -> str:
    i = name.rfind(".")
    return name[i + 1 :].lower() if i > 0 else "jpg"


def _row_to_image(row: dict) -> dict:
    if not row:
        return {}
    path = row.get("path") or ""
    if path.startswith("videos/"):
        url = "/uploads/" + path
    else:
        url = "/uploads/images/" + path if path else ""
    return {
        "id": row["id"],
        "name": row.get("name"),
        "path": path,
        "url": url,
        "fileSize": row.get("file_size"),
        "createTime": row.get("create_time"),
    }


def upload(file) -> Optional[dict]:
    """
    上传图片：按内容 SHA256 去重，同名/改名只保留一份物理文件。
    若内容已存在则仅新增 ly_image 记录并返回同一 url。
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
    storage_rel = f"images/by_hash/{content_hash}.{ext}"
    full_path = UPLOAD_PATH / storage_rel
    try:
        existing = db.query_one(SELECT_BY_HASH, (content_hash,))
        if existing:
            storage_rel = existing["relative_path"]
        else:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_bytes(content)
            db.execute(INSERT_FILE_HASH, (content_hash, storage_rel, file_size))
        path_for_image = storage_rel.replace("images/", "", 1) if (storage_rel or "").startswith("images/") else storage_rel
        db.execute(
            "INSERT INTO ly_image (name, path, file_size) VALUES (%s, %s, %s)",
            (name, path_for_image, file_size),
        )
        row = db.query_one("SELECT id, name, path, file_size, create_time FROM ly_image ORDER BY id DESC LIMIT 1")
        return _row_to_image(row) if row else None
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:
            return None
        raise


def page(page_num: int = 1, size: int = 20, keyword: Optional[str] = None) -> dict:
    from models.schemas import page_result
    try:
        where = " WHERE 1=1 "
        params: List[Any] = []
        if keyword and keyword.strip():
            where += " AND name LIKE %s "
            params.append("%" + keyword.strip() + "%")
        total_row = db.query_one("SELECT COUNT(*) AS cnt FROM ly_image " + where, tuple(params))
        total = total_row["cnt"] or 0
        offset = (page_num - 1) * size
        params.extend([size, offset])
        rows = db.query_all(
            "SELECT id, name, path, file_size, create_time FROM ly_image " + where + " ORDER BY id DESC LIMIT %s OFFSET %s",
            tuple(params),
        )
        records = [_row_to_image(r) for r in (rows or [])]
        return page_result(records, total, page_num, size)
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:  # Table doesn't exist
            return page_result([], 0, page_num, size)
        raise


def delete_by_id(image_id: int) -> None:
    """删除图片库记录；物理文件不删除（by_hash 可能被多条记录引用，资源只保留一份）"""
    if not image_id:
        return
    try:
        db.execute("DELETE FROM ly_image WHERE id = %s", (image_id,))
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:
            return
        raise
