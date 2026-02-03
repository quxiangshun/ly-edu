# -*- coding: utf-8 -*-
"""用户任务进度服务，与 Java UserTaskService 对应"""
import json
from typing import Any, List, Optional

import db
from services import task_service
from services import user_certificate_service

SELECT_COLS = "id, user_id, task_id, progress, status, completed_at, create_time, update_time"


def _row_to_user_task(row: dict) -> dict:
    if not row:
        return {}
    return {
        "id": row["id"],
        "userId": row.get("user_id"),
        "taskId": row.get("task_id"),
        "progress": row.get("progress"),
        "status": row.get("status", 0),
        "completedAt": row.get("completed_at"),
        "createTime": row.get("create_time"),
        "updateTime": row.get("update_time"),
    }


def _get_by_user_and_task(user_id: int, task_id: int) -> Optional[dict]:
    if not user_id or not task_id:
        return None
    sql = "SELECT " + SELECT_COLS + " FROM ly_user_task WHERE user_id = %s AND task_id = %s"
    row = db.query_one(sql, (user_id, task_id))
    return _row_to_user_task(row) if row else None


def _is_all_items_done(items_json: Optional[str], progress_json: Optional[str]) -> bool:
    if not items_json or not items_json.strip():
        return True
    try:
        items = json.loads(items_json)
        if not items:
            return True
        progress_items = []
        if progress_json and progress_json.strip():
            progress = json.loads(progress_json)
            if progress and progress.get("items"):
                progress_items = progress.get("items") or []
        for item in items:
            itype = item.get("type")
            iid = item.get("id")
            if itype is None or iid is None:
                continue
            iid = int(iid) if not isinstance(iid, int) else iid
            done = False
            for p in progress_items:
                pt = p.get("type")
                pid = p.get("id")
                pdone = p.get("done")
                if pt and str(pt) == str(itype) and pid is not None:
                    pid = int(pid) if not isinstance(pid, int) else pid
                    if pid == iid:
                        done = pdone is not None and (int(pdone) == 1 if isinstance(pdone, (int, float)) else str(pdone) == "1")
                        break
            if not done:
                return False
        return True
    except Exception:
        return False


def list_my_tasks(user_id: int) -> List[dict]:
    if not user_id:
        return []
    page = task_service.page(page_num=1, size=500, keyword=None, user_id=user_id)
    records = page.get("records") or []
    result = []
    for task in records:
        ut = _get_by_user_and_task(user_id, task.get("id"))
        result.append({"task": task, "userTask": ut})
    return result


def get_task_detail(task_id: int, user_id: int) -> Optional[dict]:
    return task_service.get_by_id(task_id, user_id)


def get_or_create_user_task(task_id: int, user_id: int) -> Optional[dict]:
    if not task_id or not user_id:
        return None
    task = task_service.get_by_id(task_id, user_id)
    if not task:
        return None
    ut = _get_by_user_and_task(user_id, task_id)
    if ut:
        return ut
    db.execute(
        "INSERT INTO ly_user_task (user_id, task_id, progress, status) VALUES (%s, %s, %s, %s)",
        (user_id, task_id, '{"items":[]}', 0),
    )
    row = db.query_one("SELECT LAST_INSERT_ID() AS id", ())
    uid = row.get("id") if row else None
    if not uid:
        return None
    return _get_by_user_and_task(user_id, task_id)


def update_progress(task_id: int, user_id: int, progress_json: Optional[str]) -> Optional[dict]:
    if not task_id or not user_id:
        return None
    ut = _get_by_user_and_task(user_id, task_id)
    if not ut:
        ut = get_or_create_user_task(task_id, user_id)
    if not ut:
        return None
    if ut.get("status") == 1:
        return _get_by_user_and_task(user_id, task_id)
    db.execute(
        "UPDATE ly_user_task SET progress = %s, update_time = NOW() WHERE id = %s",
        (progress_json or "{}", ut["id"]),
    )
    task = task_service.get_by_id_ignore_visibility(task_id)
    if task and _is_all_items_done(task.get("items"), progress_json):
        db.execute(
            "UPDATE ly_user_task SET status = 1, completed_at = NOW(), update_time = NOW() WHERE id = %s",
            (ut["id"],),
        )
        cert_id = task.get("certificateId")
        if cert_id:
            user_certificate_service.issue_if_eligible("task", task_id, user_id)
    return _get_by_user_and_task(user_id, task_id)
