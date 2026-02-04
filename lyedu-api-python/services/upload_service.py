# -*- coding: utf-8 -*-
"""分片上传服务，与 Java FileUploadService 对应"""
import os
import shutil
import uuid
from pathlib import Path
from typing import List, Optional

import db
from config import UPLOAD_PATH

SELECT_BY_FILE_ID = (
    "SELECT id, file_id, file_name, file_size, file_type, chunk_size, total_chunks, "
    "uploaded_chunks, upload_path, status, create_time, update_time "
    "FROM ly_file_upload WHERE file_id = %s"
)
INSERT_UPLOAD = (
    "INSERT INTO ly_file_upload (file_id, file_name, file_size, file_type, chunk_size, total_chunks, uploaded_chunks, upload_path, status) "
    "VALUES (%s, %s, %s, %s, %s, %s, 0, %s, 0)"
)
UPDATE_UPLOAD_PROGRESS = (
    "UPDATE ly_file_upload SET uploaded_chunks = uploaded_chunks + 1, "
    "status = CASE WHEN uploaded_chunks + 1 >= total_chunks THEN 1 ELSE 0 END WHERE file_id = %s"
)
UPDATE_UPLOAD_PATH = "UPDATE ly_file_upload SET upload_path = %s, status = 1 WHERE file_id = %s"
SELECT_UPLOADED_CHUNKS = "SELECT chunk_index FROM ly_file_chunk WHERE file_id = %s ORDER BY chunk_index"
INSERT_CHUNK = "INSERT INTO ly_file_chunk (file_id, chunk_index, chunk_size, chunk_path) VALUES (%s, %s, %s, %s)"
DELETE_UPLOAD = "DELETE FROM ly_file_upload WHERE file_id = %s"
DELETE_CHUNKS = "DELETE FROM ly_file_chunk WHERE file_id = %s"


def _generate_file_id(file_name: str, file_size: int) -> str:
    return f"{file_name}_{file_size}_{uuid.uuid4().hex[:16]}"


def init_upload(
    file_id: Optional[str],
    file_name: str,
    file_size: int,
    file_type: str,
    chunk_size: int,
) -> dict:
    file_id = (file_id or "").strip() or _generate_file_id(file_name, file_size)
    total_chunks = (file_size + chunk_size - 1) // chunk_size
    relative_path = f"videos/{file_id}/{file_name}"
    chunk_dir = UPLOAD_PATH / "videos" / file_id / "chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)
    db.execute(
        INSERT_UPLOAD,
        (file_id, file_name, file_size, file_type or "video/mp4", chunk_size, total_chunks, relative_path),
    )
    return get_progress(file_id)


def get_progress(file_id: str) -> Optional[dict]:
    row = db.query_one(SELECT_BY_FILE_ID, (file_id,))
    if not row:
        return None
    return {
        "fileId": row["file_id"],
        "fileName": row["file_name"],
        "fileSize": row["file_size"],
        "fileType": row.get("file_type"),
        "chunkSize": row["chunk_size"],
        "totalChunks": row["total_chunks"],
        "uploadedChunks": row["uploaded_chunks"],
        "uploadPath": row.get("upload_path"),
        "status": row["status"],
    }


def get_uploaded_chunks(file_id: str) -> List[int]:
    rows = db.query_all(SELECT_UPLOADED_CHUNKS, (file_id,))
    return [r["chunk_index"] for r in rows]


def upload_chunk(file_id: str, chunk_index: int, chunk_size: int, chunk_data: bytes) -> bool:
    uploaded = get_uploaded_chunks(file_id)
    if chunk_index in uploaded:
        return True
    chunk_dir = UPLOAD_PATH / "videos" / file_id / "chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)
    chunk_path = chunk_dir / f"{chunk_index}.chunk"
    chunk_path.write_bytes(chunk_data)
    rel_path = str(chunk_path.relative_to(UPLOAD_PATH)).replace("\\", "/")
    db.execute(INSERT_CHUNK, (file_id, chunk_index, chunk_size, rel_path))
    db.execute(UPDATE_UPLOAD_PROGRESS, (file_id,))
    return True


def merge_chunks(file_id: str) -> str:
    prog = get_progress(file_id)
    if not prog:
        raise RuntimeError(f"Upload record not found: {file_id}")
    uploaded = get_uploaded_chunks(file_id)
    total = prog["totalChunks"]
    if len(uploaded) != total:
        raise RuntimeError(f"Not all chunks uploaded. Expected {total}, got {len(uploaded)}")
    relative_path = prog["uploadPath"]
    merged_file = UPLOAD_PATH / relative_path
    merged_file.parent.mkdir(parents=True, exist_ok=True)
    chunk_dir = UPLOAD_PATH / "videos" / file_id / "chunks"
    with open(merged_file, "wb") as out:
        for i in range(total):
            chunk_file = chunk_dir / f"{i}.chunk"
            if not chunk_file.exists():
                raise RuntimeError(f"Chunk file not found: {chunk_file}")
            out.write(chunk_file.read_bytes())
    if chunk_dir.exists():
        shutil.rmtree(chunk_dir, ignore_errors=True)
    db.execute(UPDATE_UPLOAD_PATH, (relative_path, file_id))
    return relative_path


def cancel_upload(file_id: str) -> None:
    prog = get_progress(file_id)
    if prog and prog.get("uploadPath"):
        full = UPLOAD_PATH / prog["uploadPath"]
        if full.exists():
            try:
                full.unlink()
            except OSError:
                pass
    chunk_dir = UPLOAD_PATH / "videos" / file_id
    if chunk_dir.exists():
        shutil.rmtree(chunk_dir, ignore_errors=True)
    db.execute(DELETE_CHUNKS, (file_id,))
    db.execute(DELETE_UPLOAD, (file_id,))
