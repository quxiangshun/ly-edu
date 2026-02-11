# -*- coding: utf-8 -*-
"""
飞书通讯录同步：与 docs/飞书同步.md（完整实现：部门 + 用户 + 覆盖）对齐。
- 部门：递归拉取全量，两阶段写库（先 parent_id=0 建映射，再更新 parent_id）；overwrite_existing 控制是否更新已存在部门。
- 用户：优先全量用户列表，≤5 则按部门兜底去重；union_id/open_id 匹配；手机号去国家码；覆盖时若用手机号作用户名则校验唯一性（已被占用则保留原用户名并记入 errors）。
- 本系统无 department_closures、user_oauth 表，部门用 ly_department.parent_id，用户用 ly_user.feishu_open_id/union_id。
"""
import re
import random
from typing import Dict, List, Optional, Any

from util import feishu_api
from services.org import department_service
from services.user import user_service


# ---------- 部门：递归拉取（与文档 2.2 一致） ----------

def _normalize_dept_item(it: dict, parent_feishu_id: str) -> Optional[Dict[str, Any]]:
    """从飞书部门项解析 feishu_id、name、sort、parent_feishu_id。"""
    feishu_id = (it.get("department_id") or it.get("open_department_id") or "").strip()
    if not feishu_id:
        return None
    name = (it.get("name") or "").strip() or "未命名部门"
    order_val = it.get("order") or "0"
    try:
        sort_val = int(order_val) if str(order_val).isdigit() else 0
    except Exception:
        sort_val = 0
    parent_from_api = (it.get("parent_department_id") or "").strip() or parent_feishu_id
    return {
        "feishu_id": feishu_id,
        "name": name,
        "sort": sort_val,
        "parent_feishu_id": parent_from_api or "0",
    }


def _collect_all_departments_recursive() -> List[Dict[str, Any]]:
    """
    递归拉取全量部门（文档 2.2）：从根 "0" 开始，对每层调用「获取子部门」，分页拉全。
    返回列表，每项含 feishu_id, name, sort, parent_feishu_id。
    """
    all_depts: List[Dict[str, Any]] = []
    seen: set = set()
    queue: List[str] = ["0"]
    page_size = 50

    while queue:
        parent_feishu_id = queue.pop(0)
        page_token: Optional[str] = None
        while True:
            page = feishu_api.list_department_children(
                parent_feishu_id, page_token=page_token, page_size=page_size
            )
            items = page.get("items") or []
            if not items and page_token is None:
                page = feishu_api.list_departments_by_parent(
                    parent_feishu_id, page_token=None, page_size=page_size
                )
                items = page.get("items") or []
            for it in items:
                norm = _normalize_dept_item(it, parent_feishu_id)
                if not norm or norm["feishu_id"] in seen:
                    continue
                seen.add(norm["feishu_id"])
                all_depts.append(norm)
                queue.append(norm["feishu_id"])
            page_token = page.get("page_token") or ""
            if not page.get("has_more") or not page_token:
                break
    return all_depts


def sync_departments(overwrite_existing: bool = False) -> Dict[str, Any]:
    """
    部门同步（文档三）：两阶段。
    第一次遍历：创建/更新部门，parent_id 先统一 0，建立 飞书部门ID → 本地部门ID 映射。
    第二次遍历：根据 parent_department_id 更新每个部门的 parent_id。
    返回 {"created": int, "updated": int, "skipped": int, "failed": int, "errors": []}
    """
    result = {"created": 0, "updated": 0, "skipped": 0, "failed": 0, "errors": []}
    feishu_to_our: Dict[str, int] = {"0": 0}

    try:
        all_depts = _collect_all_departments_recursive()
        if not all_depts:
            return result

        # 第一次遍历：创建或更新（仅 name），parent_id 先设为 0
        for d in all_depts:
            feishu_id = d["feishu_id"]
            name = d["name"]
            sort_val = d["sort"]
            try:
                existing = department_service.get_by_feishu_department_id(feishu_id)
                if existing:
                    if overwrite_existing:
                        department_service.update(
                            existing["id"],
                            name=name,
                            parent_id=0,
                            sort=sort_val,
                            feishu_department_id=feishu_id,
                        )
                        result["updated"] += 1
                    else:
                        result["skipped"] += 1
                    feishu_to_our[feishu_id] = existing["id"]
                else:
                    new_id = department_service.save(
                        name=name,
                        parent_id=0,
                        sort=sort_val,
                        status=1,
                        feishu_department_id=feishu_id,
                    )
                    if new_id:
                        result["created"] += 1
                        feishu_to_our[feishu_id] = new_id
            except Exception as e:
                result["failed"] += 1
                result["errors"].append(f"部门 {name}({feishu_id}): {e}")

        # 第二次遍历：更新 parent_id（文档 3.3）
        for d in all_depts:
            feishu_id = d["feishu_id"]
            parent_feishu_id = d["parent_feishu_id"]
            if not parent_feishu_id or parent_feishu_id == "0":
                continue
            if feishu_id not in feishu_to_our or parent_feishu_id not in feishu_to_our:
                continue
            try:
                our_id = feishu_to_our[feishu_id]
                our_parent_id = feishu_to_our[parent_feishu_id]
                existing = department_service.get_by_id(our_id)
                if existing:
                    current_parent = existing.get("parentId") if existing.get("parentId") is not None else 0
                    if current_parent != our_parent_id:
                        department_service.update(our_id, parent_id=our_parent_id)
            except Exception as e:
                result["errors"].append(f"部门 parent {feishu_id}: {e}")
    except Exception as e:
        result["errors"].append(f"部门同步异常: {e}")
    return result


# ---------- 用户：手机号去国家码（文档 4.6） ----------

def _normalize_mobile(mobile: str) -> str:
    """飞书可能返回 +8613800138000，去掉国家码后入库。"""
    if not mobile or not isinstance(mobile, str):
        return ""
    s = mobile.strip()
    if s.startswith("+86"):
        return s[3:].strip()
    if s.startswith("+1"):
        return s[2:].strip()
    m = re.match(r"^\+(\d{2,3})(\d{7,})$", s)
    if m:
        return m.group(2)
    return s


def _get_avatar_url(feishu_user: dict) -> Optional[str]:
    """文档 5.2：avatar.avatar_240。"""
    avatar = feishu_user.get("avatar")
    if isinstance(avatar, dict):
        return (avatar.get("avatar_240") or avatar.get("avatar_72") or "").strip() or None
    if isinstance(avatar, str):
        return avatar.strip() or None
    return None


# ---------- 用户同步（文档四） ----------

def _fetch_all_users_method_a() -> List[dict]:
    """方式 A：全量用户列表（不传 department_id），分页拉全。部分应用/权限下可能返回空。"""
    all_items: List[dict] = []
    page_token: Optional[str] = None
    page_size = 50
    while True:
        page = feishu_api.list_all_users(page_token=page_token, page_size=page_size)
        items = page.get("items") or []
        all_items.extend(items)
        page_token = page.get("page_token") or ""
        if not page.get("has_more") or not page_token:
            break
    return all_items


def _fetch_all_users_under_root() -> List[dict]:
    """兜底：按根部门(0)+含子部门(fetch_child=True)分页拉全量用户，飞书通讯录常用方式。"""
    all_items: List[dict] = []
    page_token: Optional[str] = None
    page_size = 100
    while True:
        page = feishu_api.list_users_by_department(
            "0", page_token=page_token, page_size=page_size, fetch_child=True
        )
        items = page.get("items") or []
        all_items.extend(items)
        page_token = page.get("page_token") or ""
        if not page.get("has_more") or not page_token:
            break
    return all_items


def _fetch_all_users_method_b(feishu_dept_id_to_our: Dict[str, int]) -> List[dict]:
    """方式 B：按每个部门拉取（含子部门 fetch_child=True）并按 open_id 去重。"""
    user_map: Dict[str, dict] = {}
    for feishu_dept_id in feishu_dept_id_to_our:
        if feishu_dept_id == "0":
            continue
        page_token: Optional[str] = None
        while True:
            page = feishu_api.list_users_by_department(
                feishu_dept_id, page_token=page_token, page_size=50, fetch_child=True
            )
            for it in page.get("items") or []:
                open_id = (it.get("open_id") or it.get("user_id") or "").strip()
                if open_id and open_id not in user_map:
                    user_map[open_id] = it
            page_token = page.get("page_token") or ""
            if not page.get("has_more") or not page_token:
                break
    return list(user_map.values())


def sync_users(
    feishu_dept_id_to_our: Optional[Dict[str, int]] = None,
    overwrite_existing: bool = False,
) -> Dict[str, Any]:
    """
    用户同步（文档四）：
    - 优先方式 A 全量；若条数 ≤5 则用方式 B 按部门拉取去重。
    - 匹配：union_id 优先，否则 open_id（文档 4.3）。
    - 已存在：overwrite_existing 为 True 时更新，否则跳过。
    - 新用户：用户名 = 手机号 or 邮箱前缀 or feishu_<open_id前8位>，冲突加后缀；不设密码（文档 4.5 可配置）。
    返回 {"created": int, "updated": int, "skipped": int, "failed": int, "errors": []}
    """
    result = {"created": 0, "updated": 0, "skipped": 0, "failed": 0, "errors": []}
    if feishu_dept_id_to_our is None:
        flat = department_service.list_all()
        feishu_dept_id_to_our = {}
        for d in flat:
            fid = d.get("feishuDepartmentId") or d.get("feishu_department_id")
            if fid:
                feishu_dept_id_to_our[str(fid)] = d["id"]
        feishu_dept_id_to_our["0"] = 0

    feishu_users = _fetch_all_users_method_a()
    if len(feishu_users) <= 5:
        under_root = _fetch_all_users_under_root()
        if len(under_root) > len(feishu_users):
            feishu_users = under_root
        if len(feishu_users) <= 5:
            feishu_users = _fetch_all_users_method_b(feishu_dept_id_to_our)

    for it in feishu_users:
        open_id = (it.get("open_id") or it.get("user_id") or "").strip()
        if not open_id:
            continue
        name = (it.get("name") or it.get("en_name") or "").strip() or "飞书用户"
        mobile_raw = (it.get("mobile") or "").strip()
        mobile = _normalize_mobile(mobile_raw) or None
        email = (it.get("email") or "").strip() or None
        avatar_url = _get_avatar_url(it)
        dept_ids = it.get("department_ids") or []
        our_dept_id = None
        if dept_ids:
            first = dept_ids[0] if isinstance(dept_ids[0], str) else str(dept_ids[0])
            our_dept_id = feishu_dept_id_to_our.get(first)

        union_id_raw = it.get("union_id")
        union_id = str(union_id_raw).strip() if union_id_raw else None

        try:
            existing = None
            if union_id:
                existing = user_service.find_by_union_id(union_id)
            if existing is None:
                existing = user_service.find_by_feishu_open_id(open_id)

            if existing:
                if overwrite_existing:
                    update_kw: Dict[str, Any] = {
                        "real_name": name,
                        "nickname": name,
                        "mobile": mobile,
                        "email": email,
                        "avatar": avatar_url,
                        "department_id": our_dept_id,
                    }
                    if union_id is not None:
                        update_kw["union_id"] = union_id
                    if mobile:
                        other = user_service.find_by_username(mobile)
                        if other and (other.get("id") or 0) != (existing.get("id") or 0):
                            result["errors"].append(
                                f"用户 {name}({open_id}) 手机号 {mobile} 已被占用，保留原用户名"
                            )
                        else:
                            update_kw["username"] = mobile
                    user_service.update(existing["id"], **update_kw)
                    result["updated"] += 1
                else:
                    result["skipped"] += 1
            else:
                username = mobile or (email.split("@")[0] if email else f"feishu_{open_id[:8]}")
                if not username:
                    username = f"feishu_{open_id[:8]}"
                if user_service.find_by_username(username):
                    username = f"{username}_{random.randint(1000, 9999)}"
                user_service.save(
                    username=username,
                    real_name=name,
                    nickname=name,
                    email=email,
                    mobile=mobile,
                    avatar=avatar_url,
                    feishu_open_id=open_id,
                    union_id=union_id,
                    department_id=our_dept_id,
                    set_password=False,
                )
                result["created"] += 1
        except Exception as e:
            result["failed"] += 1
            result["errors"].append(f"用户 {name}({open_id}): {e}")

    return result


def run_full_sync(
    sync_departments_flag: bool = True,
    sync_users_flag: bool = True,
    overwrite_existing: bool = False,
) -> Dict[str, Any]:
    """
    飞书同步入口（文档六）：先部门后用户，返回完整统计与错误列表。
    """
    dept_result = {"created": 0, "updated": 0, "skipped": 0, "failed": 0, "errors": []}
    user_result = {"created": 0, "updated": 0, "skipped": 0, "failed": 0, "errors": []}
    feishu_to_our: Dict[str, int] = {"0": 0}

    if sync_departments_flag:
        dept_result = sync_departments(overwrite_existing=overwrite_existing)
        flat = department_service.list_all()
        for d in flat:
            fid = d.get("feishuDepartmentId") or d.get("feishu_department_id")
            if fid:
                feishu_to_our[str(fid)] = d["id"]
        feishu_to_our["0"] = 0

    if sync_users_flag:
        user_result = sync_users(
            feishu_dept_id_to_our=feishu_to_our,
            overwrite_existing=overwrite_existing,
        )

    return {
        "departments": dept_result,
        "users": user_result,
        "stats": {
            "departments_created": dept_result["created"],
            "departments_updated": dept_result["updated"],
            "departments_skipped": dept_result["skipped"],
            "departments_failed": dept_result["failed"],
            "users_created": user_result["created"],
            "users_updated": user_result["updated"],
            "users_skipped": user_result["skipped"],
            "users_failed": user_result["failed"],
        },
        "errors": dept_result["errors"] + user_result["errors"],
    }
