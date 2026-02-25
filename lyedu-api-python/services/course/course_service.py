# -*- coding: utf-8 -*-
"""课程服务，与 Java CourseService 对应"""
from typing import Any, List, Optional

import db
from models.schemas import page_result

SELECT_COLS_BASE = (
    "id, title, cover, description, category_id, status, sort, is_required, "
    "create_time, update_time, deleted"
)
SELECT_COLS_EXT = "play_count, like_count, comment_count"
_course_play_like_exists: Optional[bool] = None


def _course_has_play_like() -> bool:
    """课程表是否有 play_count/like_count 列（v4 迁移后）"""
    global _course_play_like_exists
    if _course_play_like_exists is not None:
        return _course_play_like_exists
    try:
        db.query_one("SELECT play_count, like_count, comment_count FROM ly_course LIMIT 0", ())
        _course_play_like_exists = True
    except Exception:
        _course_play_like_exists = False
    return _course_play_like_exists


def _select_cols() -> str:
    if _course_has_play_like():
        return SELECT_COLS_BASE + ", " + SELECT_COLS_EXT
    return SELECT_COLS_BASE


SELECT_COLS = SELECT_COLS_BASE  # 兼容旧调用，page 等用 _select_cols()


def _int(v: Any, default: int = 0) -> int:
    """将 DB 返回的 int/Decimal/None 转为 int，避免 JSON 序列化报错。"""
    if v is None:
        return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _row_to_course(row: dict) -> dict:
    if not row:
        return {}
    out = {
        "id": _int(row["id"]),
        "title": row.get("title"),
        "cover": row.get("cover"),
        "description": row.get("description"),
        "category_id": row.get("category_id") if row.get("category_id") is None else _int(row["category_id"]),
        "status": _int(row.get("status"), 1),
        "sort": _int(row.get("sort"), 0),
        "is_required": _int(row.get("is_required"), 0),
        "create_time": row.get("create_time"),
        "update_time": row.get("update_time"),
        "deleted": row.get("deleted"),
    }
    if _course_has_play_like():
        out["playCount"] = _int(row.get("play_count"), 0)
        out["likeCount"] = _int(row.get("like_count"), 0)
        out["commentCount"] = _int(row.get("comment_count"), 0)
    return out


def _order_by_clause(sort: Optional[str]) -> str:
    """根据 sort 参数返回 ORDER BY 子句。default 综合排序, latest 最新发布, play 最多播放, like 最多点赞, comment 最多评论"""
    if not sort or (sort or "").strip().lower() == "default":
        return "sort ASC, id DESC"
    s = (sort or "").strip().lower()
    if s == "latest":
        return "create_time DESC, id DESC"
    if s == "play" and _course_has_play_like():
        return "play_count DESC, id DESC"
    if s == "like" and _course_has_play_like():
        return "like_count DESC, id DESC"
    if s == "comment" and _course_has_play_like():
        return "comment_count DESC, id DESC"
    return "sort ASC, id DESC"


def page(
    page_num: int = 1,
    size: int = 10,
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    status: Optional[int] = None,
    sort: Optional[str] = None,
) -> dict:
    """分页查询课程。status=1 时仅返回上架课程（PC/uni 学员端用）；不传则返回全部（管理端用）。
    sort: default 综合排序, latest 最新发布, play 最多播放, like 最多点赞, comment 最多评论"""
    offset = (page_num - 1) * size
    where = ["deleted = 0"]
    params: List[Any] = []
    if status is not None:
        where.append("status = %s")
        params.append(status)
    if keyword and keyword.strip():
        where.append("(title LIKE %s OR description LIKE %s)")
        like = "%" + keyword.strip() + "%"
        params.extend([like, like])
    if category_id is not None:
        where.append("category_id = %s")
        params.append(category_id)
    if tag_id is not None:
        try:
            from services.learning import tag_service

            if tag_service._table_exists():
                where.append(
                    "EXISTS (SELECT 1 FROM ly_course_tag ct WHERE ct.course_id = ly_course.id AND ct.tag_id = %s)"
                )
                params.append(tag_id)
        except Exception:
            pass
    where_sql = " AND ".join(where)
    total_row = db.query_one(
        "SELECT COUNT(*) AS cnt FROM ly_course WHERE " + where_sql, tuple(params)
    )
    total = total_row["cnt"] or 0
    order_by = _order_by_clause(sort)
    cols = _select_cols()
    sql = (
        f"SELECT {cols} FROM ly_course WHERE " + where_sql + " ORDER BY " + order_by + " LIMIT %s OFFSET %s"
    )
    params.extend([size, offset])
    rows = db.query_all(sql, tuple(params))
    records = [_row_to_course(r) for r in rows]
    return page_result(records, total, page_num, size)


def get_detail_by_id(course_id: int, user_id: Optional[int] = None) -> Optional[dict]:
    row = db.query_one(
        f"SELECT {_select_cols()} FROM ly_course WHERE id = %s AND deleted = 0",
        (course_id,),
    )
    return _row_to_course(row) if row else None


def get_by_id_ignore_visibility(course_id: int) -> Optional[dict]:
    """管理端用：按ID获取课程"""
    row = db.query_one(
        f"SELECT {_select_cols()} FROM ly_course WHERE id = %s AND deleted = 0",
        (course_id,),
    )
    return _row_to_course(row) if row else None


def save(
    title: Optional[str] = None,
    cover: Optional[str] = None,
    description: Optional[str] = None,
    category_id: Optional[int] = None,
    status: int = 1,
    sort: int = 0,
    is_required: int = 0,
) -> int:
    last_id = db.execute_insert(
        "INSERT INTO ly_course (title, cover, description, category_id, status, sort, is_required) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (title or "", cover, description, category_id, status, sort, is_required),
    )
    return last_id or 0


def update(
    course_id: int,
    title: Optional[str] = None,
    cover: Optional[str] = None,
    description: Optional[str] = None,
    category_id: Optional[int] = None,
    status: Optional[int] = None,
    sort: Optional[int] = None,
    is_required: Optional[int] = None,
) -> int:
    row = db.query_one(f"SELECT {SELECT_COLS} FROM ly_course WHERE id = %s AND deleted = 0", (course_id,))
    if not row:
        return 0
    sql = "UPDATE ly_course SET title = %s, cover = %s, description = %s, category_id = %s, status = %s, sort = %s, is_required = %s WHERE id = %s AND deleted = 0"
    db.execute(
        sql,
        (title or row.get("title"), cover if cover is not None else row.get("cover"), description if description is not None else row.get("description"), category_id if category_id is not None else row.get("category_id"), status if status is not None else row.get("status"), sort if sort is not None else row.get("sort"), is_required if is_required is not None else row.get("is_required", 0), course_id),
    )
    return 0


def delete(course_id: int) -> int:
    return db.execute("UPDATE ly_course SET deleted = 1 WHERE id = %s", (course_id,))


def list_recommended(limit: int = 6, user_id: Optional[int] = None) -> List[dict]:
    """推荐课程：仅返回上架课程"""
    rows = db.query_all(
        f"SELECT {_select_cols()} FROM ly_course WHERE deleted = 0 AND status = 1 ORDER BY sort ASC, id DESC LIMIT %s",
        (limit,),
    )
    return [_row_to_course(r) for r in rows]


def sync_play_like_from_videos(course_id: int) -> None:
    """根据课程下视频的 play_count/like_count 汇总更新 ly_course"""
    if not _course_has_play_like():
        return
    try:
        db.execute(
            "UPDATE ly_course c SET "
            "c.play_count = COALESCE((SELECT SUM(v.play_count) FROM ly_video v WHERE v.course_id = c.id AND v.deleted = 0), 0), "
            "c.like_count = COALESCE((SELECT SUM(v.like_count) FROM ly_video v WHERE v.course_id = c.id AND v.deleted = 0), 0) "
            "WHERE c.id = %s AND c.deleted = 0",
            (course_id,),
        )
    except Exception:
        pass


def sync_comment_count(course_id: int) -> None:
    """根据 ly_course_comment 更新课程 comment_count"""
    if not _course_has_play_like():
        return
    try:
        db.execute(
            "UPDATE ly_course c SET "
            "c.comment_count = COALESCE((SELECT COUNT(*) FROM ly_course_comment cc WHERE cc.course_id = c.id AND cc.deleted = 0 AND (cc.status IS NULL OR cc.status = 1)), 0) "
            "WHERE c.id = %s AND c.deleted = 0",
            (course_id,),
        )
    except Exception:
        pass
