# -*- coding: utf-8 -*-
"""视频服务，与 Java VideoService 对应"""
from typing import Any, List, Optional

import pymysql

import db
from models.schemas import page_result


def _int(v: Any, default: int = 0) -> int:
    """将 DB 返回的 int/Decimal/None 转为 int，避免 JSON 序列化报错。"""
    if v is None:
        return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _row_to_video(row: dict, extra: Optional[dict] = None) -> dict:
    if not row:
        return {}
    pc = _int(row.get("play_count"), 0)
    lc = _int(row.get("like_count"), 0)
    out = {
        "id": _int(row["id"]),
        "course_id": _int(row["course_id"]),
        "chapter_id": row.get("chapter_id") if row.get("chapter_id") is None else _int(row["chapter_id"]),
        "title": row.get("title"),
        "url": row.get("url"),
        "cover": row.get("cover"),
        "duration": _int(row.get("duration"), 0),
        "sort": _int(row.get("sort"), 0),
        "play_count": pc,
        "like_count": lc,
        "playCount": pc,
        "likeCount": lc,
        "create_time": row.get("create_time"),
        "update_time": row.get("update_time"),
        "deleted": row.get("deleted"),
    }
    if extra:
        out.update(extra)
    return out


def _row_to_video_with_names(row: dict, extra: Optional[dict] = None) -> dict:
    """分页列表用：含 courseName、chapterName、playCount、likeCount，且带 camelCase 供前端"""
    base = _row_to_video(row, extra)
    base["courseId"] = row.get("course_id")
    base["chapterId"] = row.get("chapter_id")
    base["courseName"] = (row.get("course_name") or "").strip() or None
    base["chapterName"] = (row.get("chapter_name") or "").strip() or None
    base["playCount"] = row.get("play_count", 0)
    base["likeCount"] = row.get("like_count", 0)
    return base


def _page_sql(where_sql: str, params: List[Any], size: int, offset: int, with_play_like: bool) -> tuple:
    """构建分页 SQL；with_play_like=False 时不含 play_count/like_count（兼容未执行 V13 的库）。"""
    base = (
        "SELECT v.id, v.course_id, v.chapter_id, v.title, v.url, v.cover, v.duration, v.sort, "
        "c.title AS course_name, ch.title AS chapter_name "
    )
    if with_play_like:
        base = (
            "SELECT v.id, v.course_id, v.chapter_id, v.title, v.url, v.cover, v.duration, v.sort, "
            "v.play_count, v.like_count, c.title AS course_name, ch.title AS chapter_name "
        )
    sql = (
        base
        + "FROM ly_video v "
        "LEFT JOIN ly_course c ON v.course_id = c.id AND c.deleted = 0 "
        "LEFT JOIN ly_course_chapter ch ON v.chapter_id = ch.id AND ch.deleted = 0 "
        "WHERE " + where_sql + " ORDER BY v.sort ASC, v.id DESC LIMIT %s OFFSET %s"
    )
    return sql, tuple(params) + (size, offset)


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
    sql, query_params = _page_sql(where_sql, list(params), size, offset, with_play_like=True)
    try:
        rows = db.query_all(sql, query_params)
    except pymysql.err.OperationalError as e:
        err = (e.args[0] or 0)
        msg = (e.args[1] or "") if len(e.args) > 1 else ""
        if err == 1054 and "play_count" in str(msg):
            sql, query_params = _page_sql(where_sql, list(params), size, offset, with_play_like=False)
            rows = db.query_all(sql, query_params)
            for r in rows:
                r.setdefault("play_count", 0)
                r.setdefault("like_count", 0)
        else:
            raise
    records = [_row_to_video_with_names(r) for r in rows]
    return page_result(records, total, page_num, size)


def _query_video_rows(sql_full: str, params: tuple) -> List[dict]:
    """执行视频列表/单条查询；若库中无 play_count/like_count 则降级查询并补 0。"""
    # 降级 SQL：不含 play_count, like_count（兼容未执行 V13 的库）
    if " FROM ly_video " in sql_full:
        rest = sql_full.split(" FROM ly_video ", 1)[-1]
        sql_minimal = (
            "SELECT id, course_id, chapter_id, title, url, cover, duration, sort, "
            "create_time, update_time, deleted FROM ly_video " + rest
        )
    else:
        sql_minimal = sql_full.replace("play_count, like_count, ", "").replace(" play_count, like_count ", " ")
    try:
        return db.query_all(sql_full, params) or []
    except pymysql.err.OperationalError as e:
        err = (e.args[0] or 0)
        msg = (e.args[1] or "") if len(e.args) > 1 else ""
        if err == 1054 and "play_count" in str(msg):
            rows = db.query_all(sql_minimal, params) or []
            for r in rows:
                r.setdefault("play_count", 0)
                r.setdefault("like_count", 0)
            return rows
        raise


def list_by_course_id(course_id: int, user_id: Optional[int] = None) -> List[dict]:
    sql = (
        "SELECT id, course_id, chapter_id, title, url, cover, duration, sort, "
        "play_count, like_count, create_time, update_time, deleted "
        "FROM ly_video WHERE course_id = %s AND deleted = 0 ORDER BY sort ASC, id ASC"
    )
    rows = _query_video_rows(sql, (course_id,))
    liked_set = _get_liked_set(user_id, [r["id"] for r in rows]) if user_id else set()
    return [_row_to_video(r, {"liked": r["id"] in liked_set}) for r in rows]


def list_by_chapter_id(chapter_id: int, user_id: Optional[int] = None) -> List[dict]:
    sql = (
        "SELECT id, course_id, chapter_id, title, url, cover, duration, sort, "
        "play_count, like_count, create_time, update_time, deleted "
        "FROM ly_video WHERE chapter_id = %s AND deleted = 0 ORDER BY sort ASC, id ASC"
    )
    rows = _query_video_rows(sql, (chapter_id,))
    liked_set = _get_liked_set(user_id, [r["id"] for r in rows]) if user_id else set()
    return [_row_to_video(r, {"liked": r["id"] in liked_set}) for r in rows]


def get_by_id(video_id: int, user_id: Optional[int] = None) -> Optional[dict]:
    sql = (
        "SELECT id, course_id, chapter_id, title, url, cover, duration, sort, "
        "play_count, like_count, create_time, update_time, deleted "
        "FROM ly_video WHERE id = %s AND deleted = 0"
    )
    rows = _query_video_rows(sql, (video_id,))
    row = rows[0] if rows else None
    if not row:
        return None
    extra = {}
    if user_id:
        extra["liked"] = _is_liked(user_id, video_id)
    return _row_to_video(row, extra)


def _is_table_missing_error(e: Exception) -> bool:
    """判断是否为表不存在（1146 或 ly_video_like 不存在），兼容不同 PyMySQL 的 args 格式。"""
    args = getattr(e, "args", ()) or ()
    if args and args[0] == 1146:
        return True
    msg = str(e).lower()
    return "1146" in msg or "ly_video_like" in msg or "doesn't exist" in msg


def _get_liked_set(user_id: int, video_ids: List[int]) -> set:
    if not video_ids:
        return set()
    try:
        placeholders = ",".join(["%s"] * len(video_ids))
        rows = db.query_all(
            f"SELECT video_id FROM ly_video_like WHERE user_id = %s AND video_id IN ({placeholders})",
            (user_id, *video_ids),
        )
        return {r["video_id"] for r in (rows or [])}
    except Exception as e:
        if _is_table_missing_error(e):
            return set()
        raise


def _is_liked(user_id: int, video_id: int) -> bool:
    try:
        row = db.query_one("SELECT 1 FROM ly_video_like WHERE user_id = %s AND video_id = %s", (user_id, video_id))
        return bool(row)
    except Exception as e:
        if _is_table_missing_error(e):
            return False
        raise


def list_liked_by_user(
    user_id: int,
    page_num: int = 1,
    size: int = 10,
) -> dict:
    """我点赞的视频，分页；按点赞时间倒序。"""
    offset = (page_num - 1) * size
    count_sql = (
        "SELECT COUNT(*) AS cnt FROM ly_video_like l "
        "INNER JOIN ly_video v ON l.video_id = v.id AND v.deleted = 0 WHERE l.user_id = %s"
    )
    total_row = db.query_one(count_sql, (user_id,))
    total = total_row["cnt"] or 0
    sql = (
        "SELECT v.id, v.course_id, v.chapter_id, v.title, v.url, v.cover, v.duration, v.sort, "
        "v.play_count, v.like_count, v.create_time, v.update_time, v.deleted "
        "FROM ly_video_like l INNER JOIN ly_video v ON l.video_id = v.id AND v.deleted = 0 "
        "WHERE l.user_id = %s ORDER BY l.create_time DESC LIMIT %s OFFSET %s"
    )
    rows = db.query_all(sql, (user_id, size, offset))
    records = [_row_to_video(r, {"liked": True}) for r in (rows or [])]
    return page_result(records, total, page_num, size)


def record_play(video_id: int) -> None:
    try:
        db.execute("UPDATE ly_video SET play_count = play_count + 1 WHERE id = %s AND deleted = 0", (video_id,))
    except Exception as e:
        if not _is_play_count_error(e):
            raise
        # V13 未执行时无 play_count 列，忽略


def _is_play_count_error(e: Exception) -> bool:
    """是否为 play_count 列不存在（1054）错误。"""
    args = getattr(e, "args", ()) or ()
    if args and args[0] == 1054:
        return True
    return "1054" in str(e) or "play_count" in str(e).lower()


def like(video_id: int, user_id: int) -> bool:
    """点赞，一人只能点一次。已点赞则返回 True 不重复插入。"""
    try:
        db.execute("INSERT INTO ly_video_like (user_id, video_id) VALUES (%s, %s)", (user_id, video_id))
        db.execute("UPDATE ly_video SET like_count = like_count + 1 WHERE id = %s AND deleted = 0", (video_id,))
        return True
    except Exception:
        return False  # 唯一键冲突表示已点赞


def unlike(video_id: int, user_id: int) -> int:
    """取消点赞。返回删除行数。"""
    n = db.execute("DELETE FROM ly_video_like WHERE user_id = %s AND video_id = %s", (user_id, video_id))
    if n > 0:
        db.execute("UPDATE ly_video SET like_count = GREATEST(0, like_count - 1) WHERE id = %s AND deleted = 0", (video_id,))
    return n


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
