# -*- coding: utf-8 -*-
"""部门服务，与 Java DepartmentService 对应"""
from typing import List, Optional

import db

_SELECT_COLS = "id, name, parent_id, sort, status, feishu_department_id, create_time, update_time, deleted"
_SELECT_COLS_WITH_PATH = "id, name, parent_id, path, sort, status, feishu_department_id, create_time, update_time, deleted"


def _path_to_ancestor_ids(path: Optional[str]) -> List[int]:
    """从 path 解析祖籍 ID 列表（不含自身）。path 如 '1.2.3' -> ancestorIds [1, 2]"""
    if not path or not str(path).strip():
        return []
    parts = str(path).strip().split(".")
    if len(parts) <= 1:
        return []
    return [int(p) for p in parts[:-1] if p.isdigit()]


def _row_to_dept(row: dict, id_to_path: Optional[dict] = None) -> dict:
    """转为前端需要的 camelCase：id, name, parentId, sort, status, path, ancestorIds"""
    if not row:
        return {}
    path_val = row.get("path")
    if path_val is None and id_to_path and row.get("id") is not None:
        path_val = id_to_path.get(row["id"])
    out = {
        "id": row["id"],
        "name": row.get("name"),
        "parentId": row.get("parent_id") if row.get("parent_id") is not None else 0,
        "sort": row.get("sort", 0),
        "status": row.get("status", 1),
    }
    if path_val is not None:
        out["path"] = path_val if isinstance(path_val, str) else str(path_val or "")
    out["ancestorIds"] = _path_to_ancestor_ids(out.get("path"))
    if row.get("feishu_department_id") is not None:
        out["feishuDepartmentId"] = row.get("feishu_department_id")
    return out


def _has_path_column() -> bool:
    try:
        db.query_one("SELECT path FROM ly_department LIMIT 0", ())
        return True
    except Exception:
        return False


def _compute_path_from_flat(flat: List[dict], dept_id: int) -> str:
    """根据扁平列表计算某部门的 path（从根到自身）"""
    id_to_parent = {d["id"]: (d.get("parentId") or d.get("parent_id") or 0) for d in flat}
    cache = {}

    def get_path(did: int) -> str:
        if did in cache:
            return cache[did]
        pid = id_to_parent.get(did, 0)
        if not pid:
            cache[did] = str(did)
            return str(did)
        parent_path = get_path(pid)
        cache[did] = f"{parent_path}.{did}" if parent_path else str(did)
        return cache[did]

    return get_path(dept_id)


def list_all() -> List[dict]:
    """查询所有部门（未删除），按 sort、id 排序；含 path、ancestorIds（祖籍列表）"""
    has_path = _has_path_column()
    if has_path:
        try:
            rows = db.query_all(
                f"SELECT {_SELECT_COLS_WITH_PATH} FROM ly_department WHERE deleted = 0 ORDER BY sort ASC, id ASC"
            )
        except Exception:
            has_path = False
            rows = db.query_all(
                f"SELECT {_SELECT_COLS} FROM ly_department WHERE deleted = 0 ORDER BY sort ASC, id ASC"
            )
    else:
        try:
            rows = db.query_all(
                f"SELECT {_SELECT_COLS} FROM ly_department WHERE deleted = 0 ORDER BY sort ASC, id ASC"
            )
        except Exception:
            rows = db.query_all(
                "SELECT id, name, parent_id, sort, status, create_time, update_time, deleted "
                "FROM ly_department WHERE deleted = 0 ORDER BY sort ASC, id ASC"
            )
    flat = [{"id": r["id"], "parentId": r.get("parent_id") or 0, "parent_id": r.get("parent_id")} for r in rows]
    if has_path:
        id_to_path = {r["id"]: (r.get("path") or "") for r in rows if r.get("id") is not None}
    else:
        id_to_path = {d["id"]: _compute_path_from_flat(flat, d["id"]) for d in flat}
    return [_row_to_dept(r, id_to_path) for r in rows]


def get_by_feishu_department_id(feishu_department_id: str) -> Optional[dict]:
    """根据飞书部门ID查询（用于通讯录同步）"""
    if not (feishu_department_id or str(feishu_department_id).strip()):
        return None
    has_path = _has_path_column()
    if has_path:
        try:
            row = db.query_one(
                f"SELECT {_SELECT_COLS_WITH_PATH} FROM ly_department WHERE feishu_department_id = %s AND deleted = 0 LIMIT 1",
                (str(feishu_department_id).strip(),),
            )
        except Exception:
            row = db.query_one(
                f"SELECT {_SELECT_COLS} FROM ly_department WHERE feishu_department_id = %s AND deleted = 0 LIMIT 1",
                (str(feishu_department_id).strip(),),
            )
    else:
        row = db.query_one(
            f"SELECT {_SELECT_COLS} FROM ly_department WHERE feishu_department_id = %s AND deleted = 0 LIMIT 1",
            (str(feishu_department_id).strip(),),
        )
    if not row:
        return None
    if not has_path or row.get("path") is None:
        flat = [{"id": r["id"], "parentId": r.get("parent_id") or 0, "parent_id": r.get("parent_id")} for r in db.query_all("SELECT id, parent_id FROM ly_department WHERE deleted = 0")]
        row["path"] = _compute_path_from_flat(flat, row["id"])
    return _row_to_dept(row)


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
    has_path = _has_path_column()
    if has_path:
        try:
            row = db.query_one(
                f"SELECT {_SELECT_COLS_WITH_PATH} FROM ly_department WHERE id = %s AND deleted = 0",
                (dept_id,),
            )
        except Exception:
            row = db.query_one(
                f"SELECT {_SELECT_COLS} FROM ly_department WHERE id = %s AND deleted = 0",
                (dept_id,),
            )
    else:
        row = db.query_one(
            f"SELECT {_SELECT_COLS} FROM ly_department WHERE id = %s AND deleted = 0",
            (dept_id,),
        )
    if not row:
        return None
    if not has_path:
        flat = [{"id": r["id"], "parentId": r.get("parent_id") or 0, "parent_id": r.get("parent_id")} for r in db.query_all("SELECT id, parent_id FROM ly_department WHERE deleted = 0")]
        row["path"] = _compute_path_from_flat(flat, dept_id)
    return _row_to_dept(row)


def _get_parent_path(parent_id: int) -> str:
    """获取父部门的 path，用于计算新节点的 path"""
    if not parent_id:
        return ""
    if not _has_path_column():
        return ""
    row = db.query_one("SELECT path FROM ly_department WHERE id = %s AND deleted = 0", (parent_id,))
    return (row.get("path") or "").strip() if row else ""


def save(
    name: str,
    parent_id: Optional[int] = None,
    sort: int = 0,
    status: int = 1,
    feishu_department_id: Optional[str] = None,
) -> Optional[int]:
    pid = parent_id if parent_id is not None else 0
    cols = "name, parent_id, sort, status"
    vals = (name or "", pid, sort, status)
    if _has_path_column():
        if feishu_department_id is not None and str(feishu_department_id).strip():
            new_id = db.execute_insert(
                "INSERT INTO ly_department (name, parent_id, sort, status, feishu_department_id) VALUES (%s, %s, %s, %s, %s)",
                (name or "", pid, sort, status, str(feishu_department_id).strip()),
            )
        else:
            new_id = db.execute_insert(
                "INSERT INTO ly_department (name, parent_id, sort, status) VALUES (%s, %s, %s, %s)",
                vals,
            )
        if new_id:
            parent_path = _get_parent_path(pid)
            path = f"{parent_path}.{new_id}" if parent_path else str(new_id)
            db.execute("UPDATE ly_department SET path = %s WHERE id = %s AND deleted = 0", (path, new_id))
        return new_id if new_id else None
    if feishu_department_id is not None and str(feishu_department_id).strip():
        new_id = db.execute_insert(
            "INSERT INTO ly_department (name, parent_id, sort, status, feishu_department_id) VALUES (%s, %s, %s, %s, %s)",
            (name or "", pid, sort, status, str(feishu_department_id).strip()),
        )
    else:
        new_id = db.execute_insert(
            "INSERT INTO ly_department (name, parent_id, sort, status) VALUES (%s, %s, %s, %s)",
            vals,
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
    feishu_val = str(feishu_department_id).strip() if feishu_department_id else None
    if _has_path_column() and (parent_id is not None or row.get("parent_id") != pid):
        parent_path = _get_parent_path(pid)
        path = f"{parent_path}.{dept_id}" if parent_path else str(dept_id)
        if feishu_val is not None:
            db.execute(
                "UPDATE ly_department SET name = %s, parent_id = %s, path = %s, sort = %s, status = %s, feishu_department_id = %s WHERE id = %s AND deleted = 0",
                (name, pid, path, sort_val, status_val, feishu_val, dept_id),
            )
        else:
            db.execute(
                "UPDATE ly_department SET name = %s, parent_id = %s, path = %s, sort = %s, status = %s WHERE id = %s AND deleted = 0",
                (name, pid, path, sort_val, status_val, dept_id),
            )
        return 1
    if feishu_val is not None:
        return db.execute(
            "UPDATE ly_department SET name = %s, parent_id = %s, sort = %s, status = %s, feishu_department_id = %s WHERE id = %s AND deleted = 0",
            (name, pid, sort_val, status_val, feishu_val, dept_id),
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
