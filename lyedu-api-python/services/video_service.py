# -*- coding: utf-8 -*-
"""视频服务，与 Java VideoService 对应"""
from typing import Any, List, Optional

import db
from models.schemas import page_result


def _row_to_video(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "course_id": row["course_id"],
        "chapter_id": row.get("chapter_id"),
        "title": row.get("title"),
        "url": row.get("url"),
        "cover": row.get("cover"),
        "duration": row.get("duration", 0),
        "sort": row.get("sort", 0),
        "create_time": row.get("create_time"),
        "update_time": row.get("update_time"),
        "deleted": row.get("deleted"),
    }


def _row_to_video_with_names(row: dict) -> dict:
    """分页列表用：含 courseName、chapterName，且带 camelCase 供前端"""
    base = _row_to_video(row)
    base["courseId"] = row.get("course_id")
    base["chapterId"] = row.get("chapter_id")
    base["courseName"] = (row.get("course_name") or "").strip() or None
    base["chapterName"] = (row.get("chapter_name") or "").strip() or None
    return base


def page(
    page_num: int = 1,
    size: int = 10,
    course_id: Optional[int] = None,
    keyword: Optional[str] = None,
) -> dict:
    offset = (page_num - 1) * size
    where = ["v.deleted = 0"]
    params: List[Any] = []
    if course_id is not None:
        where.append("v.course_id = %s")
        params.append(course_id)
    if keyword and keyword.strip():
        where.append("v.title LIKE %s")
        params.append("%" + keyword.strip() + "%")
    where_sql = " AND ".join(where)
    total_row = db.query_one(
        "SELECT COUNT(*) AS cnt FROM ly_video v WHERE " + where_sql, tuple(params)
    )
    total = total_row["cnt"] or 0
    sql = (
        "SELECT v.id, v.course_id, v.chapter_id, v.title, v.url, v.cover, v.duration, v.sort, "
        "c.title AS course_name, ch.title AS chapter_name "
        "FROM ly_video v "
        "LEFT JOIN ly_course c ON v.course_id = c.id AND c.deleted = 0 "
        "LEFT JOIN ly_course_chapter ch ON v.chapter_id = ch.id AND ch.deleted = 0 "
        "WHERE " + where_sql + " ORDER BY v.sort ASC, v.id DESC LIMIT %s OFFSET %s"
    )
    params.extend([size, offset])
    rows = db.query_all(sql, tuple(params))
    records = [_row_to_video_with_names(r) for r in rows]
    return page_result(records, total, page_num, size)


def list_by_course_id(course_id: int) -> List[dict]:
    rows = db.query_all(
        "SELECT id, course_id, chapter_id, title, url, cover, duration, sort, create_time, update_time, deleted "
        "FROM ly_video WHERE course_id = %s AND deleted = 0 ORDER BY sort ASC, id ASC",
        (course_id,),
    )
    return [_row_to_video(r) for r in rows]


def list_by_chapter_id(chapter_id: int) -> List[dict]:
    rows = db.query_all(
        "SELECT id, course_id, chapter_id, title, url, cover, duration, sort, create_time, update_time, deleted "
        "FROM ly_video WHERE chapter_id = %s AND deleted = 0 ORDER BY sort ASC, id ASC",
        (chapter_id,),
    )
    return [_row_to_video(r) for r in rows]


def get_by_id(video_id: int) -> Optional[dict]:
    row = db.query_one(
        "SELECT id, course_id, chapter_id, title, url, cover, duration, sort, create_time, update_time, deleted "
        "FROM ly_video WHERE id = %s AND deleted = 0",
        (video_id,),
    )
    return _row_to_video(row) if row else None


def save(
    course_id: int,
    chapter_id: Optional[int],
    title: str,
    url: str,
    cover: Optional[str] = None,
    duration: int = 0,
    sort: int = 0,
) -> int:
    db.execute(
        "INSERT INTO ly_video (course_id, chapter_id, title, url, cover, duration, sort) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (course_id, chapter_id, title or "", url or "", cover or "", duration, sort),
    )
    return 0


def update(
    video_id: int,
    course_id: int,
    chapter_id: Optional[int],
    title: str,
    url: str,
    cover: Optional[str] = None,
    duration: int = 0,
    sort: int = 0,
) -> int:
    return db.execute(
        "UPDATE ly_video SET course_id = %s, chapter_id = %s, title = %s, url = %s, cover = %s, duration = %s, sort = %s WHERE id = %s AND deleted = 0",
        (course_id, chapter_id, title or "", url or "", cover or "", duration, sort, video_id),
    )


def delete(video_id: int) -> int:
    return db.execute("UPDATE ly_video SET deleted = 1 WHERE id = %s", (video_id,))
