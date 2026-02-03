# -*- coding: utf-8 -*-
"""图片库服务，与 Java ImageService 对应"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

import pymysql

import db
from config import UPLOAD_PATH

ALLOWED_EXT = {"jpg", "jpeg", "png", "gif", "webp"}


def _ext(name: str) -> str:
    i = name.rfind(".")
    return name[i + 1 :].lower() if i > 0 else "jpg"


def _row_to_image(row: dict) -> dict:
    if not row:
        return {}
    path = row.get("path") or ""
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
    """Upload image; file is FastAPI UploadFile. Returns image dict with url."""
    if not file or not file.filename:
        return None
    name = file.filename
    ext = _ext(name)
    if ext not in ALLOWED_EXT:
        return None
    now = datetime.now()
    sub_dir = now.strftime("%Y/%m")
    file_name = uuid.uuid4().hex + "." + ext
    relative_path = sub_dir + "/" + file_name
    full_dir = UPLOAD_PATH / "images" / sub_dir
    full_dir.mkdir(parents=True, exist_ok=True)
    full_path = full_dir / file_name
    try:
        content = file.file.read()
        full_path.write_bytes(content)
        file_size = len(content)
    except Exception:
        return None
    try:
        db.execute(
            "INSERT INTO ly_image (name, path, file_size) VALUES (%s, %s, %s)",
            (name, relative_path, file_size),
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
    if not image_id:
        return
    try:
        row = db.query_one("SELECT id, path FROM ly_image WHERE id = %s", (image_id,))
        if row and row.get("path"):
            full = UPLOAD_PATH / "images" / row["path"]
            try:
                full.unlink(missing_ok=True)
            except Exception:
                pass
        db.execute("DELETE FROM ly_image WHERE id = %s", (image_id,))
    except pymysql.err.MySQLError as e:
        if getattr(e, "args", (None,))[0] == 1146:
            return
        raise
