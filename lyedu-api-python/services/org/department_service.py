# -*- coding: utf-8 -*-
"""部门服务，与 Java DepartmentService 对应"""
from typing import List, Optional

import db


def _row_to_dept(row: dict) -> dict:
    """转为前端需要的 camelCase：id, name, parentId, sort, status, feishuDepartmentId"""
    if not row:
        return {}
    out = {
        "id": row["id"],
        "name": row.get("name"),
        "parentId": row.get("parent_id") if row.get("parent_id") is not None else 0,
        "sort": row.get("sort", 0),
        "status": row.get("status", 1),
    }
    if row.get("feishu_department_id") is not None:
        out["feishuDepartmentId"] = row.get("feishu_department_id")
    return out


def list_all() -> List[dict]:
    """查询所有部门（未删除），按 sort、id 排序（不含 feishu_department_id，以兼容未执行 v3 迁移的环境）"""
    try:
        rows = db.query_all(
            "SELECT id, name, parent_id, sort, status, feishu_department_id, create_time, update_time, deleted "
            "FROM ly_department WHERE deleted = 0 ORDER BY sort ASC, id ASC"
        )
    except Exception:
        rows = db.query_all(
            "SELECT id, name, parent_id, sort, status, create_time, update_time, deleted "
            "FROM ly_department WHERE deleted = 0 ORDER BY sort ASC, id ASC"
        )
    return [_row_to_dept(r) for r in rows]


def get_by_feishu_department_id(feishu_department_id: str) -> Optional[dict]:
    """根据飞书部门ID查询（用于通讯录同步）"""
    if not (feishu_department_id or str(feishu_department_id).strip()):
        return None
    row = db.query_one(
        "SELECT id, name, parent_id, sort, status, feishu_department_id FROM ly_department "
        "WHERE feishu_department_id = %s AND deleted = 0 LIMIT 1",
        (str(feishu_department_id).strip(),),
    )
    return _row_to_dept(row) if row else None


def _build_tree(dept_list: List[dict], parent_id: int) -> List[dict]:
    """递归构建多级树：parent_id 为 0 或 None 表示根级"""
    result = []
    for d in dept_list:
        pid = d.get("parentId")
        if (pid is None or pid == 0) and (parent_id == 0 or parent_id is None):
            result.append(d)
        elif pid == parent_id:
            result.append(d)
    for node in result:
        kids = _build_tree(dept_list, node["id"])
        node["children"] = kids if kids else None
    result.sort(key=lambda x: (x.get("sort", 0), x.get("id", 0)))
    return result


def list_tree() -> List[dict]:
    """部门多级树：返回树形结构，每节点含 children（子部门列表）"""
    flat = list_all()
    return _build_tree(flat, 0)


def get_by_id(dept_id: int) -> Optional[dict]:
    try:
        row = db.query_one(
            "SELECT id, name, parent_id, sort, status, feishu_department_id, create_time, update_time, deleted "
            "FROM ly_department WHERE id = %s AND deleted = 0",
            (dept_id,),
        )
    except Exception:
        row = db.query_one(
            "SELECT id, name, parent_id, sort, status, create_time, update_time, deleted "
            "FROM ly_department WHERE id = %s AND deleted = 0",
            (dept_id,),
        )
    return _row_to_dept(row) if row else None


def save(
    name: str,
    parent_id: Optional[int] = None,
    sort: int = 0,
    status: int = 1,
    feishu_department_id: Optional[str] = None,
) -> Optional[int]:
    pid = parent_id if parent_id is not None else 0
    if feishu_department_id is not None and str(feishu_department_id).strip():
        new_id = db.execute_insert(
            "INSERT INTO ly_department (name, parent_id, sort, status, feishu_department_id) VALUES (%s, %s, %s, %s, %s)",
            (name or "", pid, sort, status, str(feishu_department_id).strip()),
        )
    else:
        new_id = db.execute_insert(
            "INSERT INTO ly_department (name, parent_id, sort, status) VALUES (%s, %s, %s, %s)",
            (name or "", pid, sort, status),
        )
    return new_id if new_id else None


def update(
    dept_id: int,
    name: Optional[str] = None,
    parent_id: Optional[int] = None,
    sort: Optional[int] = None,
    status: Optional[int] = None,
    feishu_department_id: Optional[str] = None,
) -> int:
    row = db.query_one(
        "SELECT id, name, parent_id, sort, status, feishu_department_id FROM ly_department WHERE id = %s AND deleted = 0",
        (dept_id,),
    )
    if not row:
        return 0
    name = name if name is not None else row["name"]
    pid = parent_id if parent_id is not None else row["parent_id"]
    if pid is None:
        pid = 0
    sort_val = sort if sort is not None else row["sort"]
    status_val = status if status is not None else row["status"]
    if feishu_department_id is not None:
        return db.execute(
            "UPDATE ly_department SET name = %s, parent_id = %s, sort = %s, status = %s, feishu_department_id = %s WHERE id = %s AND deleted = 0",
            (name, pid, sort_val, status_val, str(feishu_department_id).strip() if feishu_department_id else None, dept_id),
        )
    return db.execute(
        "UPDATE ly_department SET name = %s, parent_id = %s, sort = %s, status = %s WHERE id = %s AND deleted = 0",
        (name, pid, sort_val, status_val, dept_id),
    )


def delete(dept_id: int) -> int:
    return db.execute("UPDATE ly_department SET deleted = 1 WHERE id = %s", (dept_id,))


def get_department_id_and_descendant_ids(department_id: int) -> List[int]:
    """获取指定部门及其所有子部门ID（含自身），用于课程可见性过滤"""
    if department_id is None:
        return []
    flat = list_all()
    result = [department_id]
    _collect_descendant_ids(flat, department_id, result)
    return result


def _collect_descendant_ids(dept_list: List[dict], parent_id: int, result: List[int]) -> None:
    for d in dept_list:
        pid = d.get("parentId") if d.get("parentId") is not None else d.get("parent_id")
        if pid == parent_id:
            kid_id = d["id"]
            result.append(kid_id)
            _collect_descendant_ids(dept_list, kid_id, result)
