# -*- coding: utf-8 -*-
"""用户视频学习进度服务，与 Java UserVideoProgressService 对应"""
from datetime import datetime
from typing import Dict, List, Optional

import db


def _row_to_progress(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "video_id": row["video_id"],
        "progress": row.get("progress", 0),
        "duration": row.get("duration", 0),
        "is_finished": row.get("is_finished", 0),
        "create_time": row.get("create_time"),
        "update_time": row.get("update_time"),
    }


def update_progress(
    user_id: int, video_id: int, progress: int = 0, duration: int = 0
) -> None:
    cnt = db.query_one(
        "SELECT COUNT(*) AS cnt FROM ly_user_video_progress WHERE user_id = %s AND video_id = %s",
        (user_id, video_id),
    )
    is_finished = 1 if (duration and progress >= int(duration * 0.9)) else 0
    if (cnt.get("cnt") or 0) == 0:
        db.execute(
            "INSERT INTO ly_user_video_progress (user_id, video_id, progress, duration, is_finished) VALUES (%s, %s, %s, %s, %s)",
            (user_id, video_id, progress, duration, is_finished),
        )
    else:
        db.execute(
            "UPDATE ly_user_video_progress SET progress = %s, duration = %s, is_finished = %s WHERE user_id = %s AND video_id = %s",
            (progress, duration, is_finished, user_id, video_id),
        )


def get_by_user_and_video(user_id: int, video_id: int) -> Optional[dict]:
    row = db.query_one(
        "SELECT id, user_id, video_id, progress, duration, is_finished, create_time, update_time "
        "FROM ly_user_video_progress WHERE user_id = %s AND video_id = %s",
        (user_id, video_id),
    )
    return _row_to_progress(row) if row else None


def get_progress_map(user_id: int, video_ids: List[int]) -> Dict[int, dict]:
    if not video_ids:
        return {}
    placeholders = ",".join(["%s"] * len(video_ids))
    params = [user_id] + list(video_ids)
    rows = db.query_all(
        "SELECT id, user_id, video_id, progress, duration, is_finished, create_time, update_time "
        f"FROM ly_user_video_progress WHERE user_id = %s AND video_id IN ({placeholders})",
        tuple(params),
    )
    return {r["video_id"]: _row_to_progress(r) for r in rows}


def update_last_play_ping(user_id: int, video_id: int) -> int:
    return db.execute(
        "UPDATE ly_user_video_progress SET last_play_ping_at = %s WHERE user_id = %s AND video_id = %s",
        (datetime.now(), user_id, video_id),
    )


def list_watched_course_ids(user_id: int) -> List[int]:
    rows = db.query_all(
        "SELECT t.course_id FROM ("
        "SELECT v.course_id, MAX(uvp.update_time) AS last_time FROM ly_user_video_progress uvp "
        "JOIN ly_video v ON uvp.video_id = v.id WHERE uvp.user_id = %s AND uvp.progress > 0 "
        "GROUP BY v.course_id"
        ") t ORDER BY t.last_time DESC",
        (user_id,),
    )
    return [r["course_id"] for r in rows if r.get("course_id")]
