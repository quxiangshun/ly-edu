# -*- coding: utf-8 -*-
"""飞书通讯录同步：机构（部门）与用户，不存在则创建、存在则更新"""
from typing import Dict, List, Optional, Any

from util import feishu_api
from services import department_service
from services import user_service


def sync_departments() -> Dict[str, Any]:
    """
    同步飞书部门到本地。按 BFS 顺序获取子部门，创建/更新。
    返回 {"created": int, "updated": int, "errors": []}
    """
    result = {"created": 0, "updated": 0, "errors": []}
    feishu_to_our: Dict[str, int] = {"0": 0}  # 飞书部门ID -> 本地部门ID
    queue: List[str] = ["0"]

    try:
        while queue:
            parent_feishu_id = queue.pop(0)
            our_parent_id = feishu_to_our.get(parent_feishu_id, 0)
            page_token: Optional[str] = None
            while True:
                page = feishu_api.list_department_children(parent_feishu_id, page_token=page_token)
                items = page.get("items") or []
                for it in items:
                    feishu_id = (it.get("department_id") or "").strip()
                    name = (it.get("name") or "").strip() or "未命名部门"
                    order_val = it.get("order") or "0"
                    try:
                        sort_val = int(order_val) if str(order_val).isdigit() else 0
                    except Exception:
                        sort_val = 0
                    if not feishu_id:
                        continue
                    existing = department_service.get_by_feishu_department_id(feishu_id)
                    if existing:
                        department_service.update(
                            existing["id"],
                            name=name,
                            parent_id=our_parent_id,
                            sort=sort_val,
                            feishu_department_id=feishu_id,
                        )
                        result["updated"] += 1
                        feishu_to_our[feishu_id] = existing["id"]
                    else:
                        new_id = department_service.save(
                            name=name,
                            parent_id=our_parent_id,
                            sort=sort_val,
                            status=1,
                            feishu_department_id=feishu_id,
                        )
                        if new_id:
                            result["created"] += 1
                            feishu_to_our[feishu_id] = new_id
                    queue.append(feishu_id)
                page_token = page.get("page_token") or ""
                if not page.get("has_more") or not page_token:
                    break
    except Exception as e:
        result["errors"].append(str(e))
    return result


def sync_users(feishu_dept_id_to_our: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """
    同步飞书用户到本地。若未传 feishu_dept_id_to_our，会先拉取全部部门构建映射。
    按 open_id 查找用户，不存在则创建，存在则更新姓名、部门等。
    返回 {"created": int, "updated": int, "errors": []}
    """
    result = {"created": 0, "updated": 0, "errors": []}
    if feishu_dept_id_to_our is None:
        flat = department_service.list_all()
        feishu_dept_id_to_our = {}
        for d in flat:
            fid = d.get("feishuDepartmentId") or d.get("feishu_department_id")
            if fid:
                feishu_dept_id_to_our[str(fid)] = d["id"]
        feishu_dept_id_to_our["0"] = 0

    page_token: Optional[str] = None
    while True:
        page = feishu_api.list_users_by_department(
            "0",
            page_token=page_token,
            page_size=50,
            fetch_child=True,
        )
        items = page.get("items") or []
        for it in items:
            open_id = (it.get("open_id") or it.get("user_id") or "").strip()
            if not open_id:
                continue
            name = (it.get("name") or it.get("en_name") or "").strip() or "飞书用户"
            mobile = (it.get("mobile") or "").strip()
            email = (it.get("email") or "").strip()
            dept_ids = it.get("department_ids") or []
            our_dept_id = None
            if dept_ids:
                first_feishu_dept = dept_ids[0] if isinstance(dept_ids[0], str) else str(dept_ids[0])
                our_dept_id = feishu_dept_id_to_our.get(first_feishu_dept)

            try:
                existing = user_service.find_by_feishu_open_id(open_id)
                if existing:
                    user_service.update(
                        existing["id"],
                        real_name=name,
                        mobile=mobile or None,
                        email=email or None,
                        department_id=our_dept_id,
                    )
                    result["updated"] += 1
                else:
                    username = "feishu_" + open_id
                    if user_service.find_by_username(username):
                        username = "feishu_" + open_id[:16] + "_" + str(hash(open_id) % 100000)
                    user_service.save(
                        username=username,
                        real_name=name,
                        email=email or None,
                        mobile=mobile or None,
                        feishu_open_id=open_id,
                        department_id=our_dept_id,
                    )
                    result["created"] += 1
            except Exception as e:
                result["errors"].append(f"user {open_id}: {e}")
        page_token = page.get("page_token") or ""
        if not page.get("has_more") or not page_token:
            break
    return result


def run_full_sync() -> Dict[str, Any]:
    """先同步部门，再同步用户。返回 {"departments": {...}, "users": {...}}"""
    dept_result = sync_departments()
    user_result = sync_users()
    return {"departments": dept_result, "users": user_result}
