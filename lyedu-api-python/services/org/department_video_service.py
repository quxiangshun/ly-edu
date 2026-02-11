# -*- coding: utf-8 -*-
"""部门(机构)-视频多对多关联服务"""
from typing import List, Optional

import db

TABLE = "ly_department_video"


def list_video_ids_by_department_id(department_id: Optional[int]) -> List[int]:
    if not department_id:
        return []
    rows = db.query_all("SELECT video_id FROM " + TABLE + " WHERE department_id = %s", (department_id,))
    return [r["video_id"] for r in (rows or []) if r.get("video_id") is not None]


def list_department_ids_by_video_id(video_id: Optional[int]) -> List[int]:
    if not video_id:
        return []
    rows = db.query_all("SELECT department_id FROM " + TABLE + " WHERE video_id = %s", (video_id,))
    return [r["department_id"] for r in (rows or []) if r.get("department_id") is not None]


def set_department_videos(department_id: Optional[int], video_ids: Optional[List[int]]) -> None:
    if not department_id:
        return
    db.execute("DELETE FROM " + TABLE + " WHERE department_id = %s", (department_id,))
    if video_ids:
        for vid in video_ids:
            if vid is not None:
                db.execute(
                    "INSERT INTO " + TABLE + " (department_id, video_id) VALUES (%s, %s)",
                    (department_id, vid),
                )


def set_video_departments(video_id: Optional[int], department_ids: Optional[List[int]]) -> None:
    if not video_id:
        return
    db.execute("DELETE FROM " + TABLE + " WHERE video_id = %s", (video_id,))
    if department_ids:
        for dept_id in department_ids:
            if dept_id is not None:
                db.execute(
                    "INSERT INTO " + TABLE + " (department_id, video_id) VALUES (%s, %s)",
                    (dept_id, video_id),
                )


def add_videos_to_department(department_id: Optional[int], video_ids: Optional[List[int]]) -> None:
    if not department_id or not video_ids:
        return
    for vid in video_ids:
        if vid is not None:
            db.execute(
                "INSERT IGNORE INTO " + TABLE + " (department_id, video_id) VALUES (%s, %s)",
                (department_id, vid),
            )


def remove_video_from_department(department_id: Optional[int], video_id: Optional[int]) -> None:
    if not department_id or not video_id:
        return
    db.execute("DELETE FROM " + TABLE + " WHERE department_id = %s AND video_id = %s", (department_id, video_id))


def table_exists() -> bool:
    try:
        db.query_one("SELECT 1 FROM " + TABLE + " LIMIT 0", ())
        return True
    except Exception:
        return False
