# -*- coding: utf-8 -*-
"""
飞书通讯录同步（按部门拉取、缓存部门映射、手机号唯一性）：
1. 先同步所有部门，再按每个部门拉取该部门下所有用户（含子部门），部门 id 以 feishu_department_id 匹配，写入用户时用缓存 feishu_department_id->本地 id。
2. 部门：仅根据 feishu_department_id 匹配；覆盖则更新，不覆盖则存在跳过、不存在插入。
3. 用户：始终按部门维度拉取（遍历部门调用接口），保证效率；用户以手机号做唯一性校验，存在则覆盖/跳过，不存在则插入；部门 id 从缓存取，不重复查库。
"""
import re
import random
from typing import Dict, List, Optional, Any

from loguru import logger
from util import feishu_api
from services.org import department_service
from services.user import user_service


# ---------- 部门：递归拉取 ----------

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
    """从根 0 递归拉取全量部门（仅用「获取子部门」接口），返回 feishu_id, name, sort, parent_feishu_id。"""
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
            if not items and page_token is None and parent_feishu_id == "0":
                logger.warning("feishu 根部门 0 下未获取到任何子部门，请检查飞书应用权限与 token")
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
    只同步部门：根据 feishu_department_id 匹配。
    - 覆盖：已存在则按 feishu_department_id 更新记录。
    - 不覆盖：已存在则跳过，不存在则插入。
    两阶段写库：先 parent_id=0 建映射，再按 parent_feishu_id 更新 parent_id。
    """
    result = {"created": 0, "updated": 0, "skipped": 0, "failed": 0, "errors": []}
    feishu_to_our: Dict[str, int] = {"0": 0}

    try:
        all_depts = _collect_all_departments_recursive()
        if not all_depts:
            logger.warning("feishu sync_departments: 未拉取到任何部门，跳过写库")
            return result
        logger.info("feishu sync_departments: 拉取到 {} 个部门，开始写库", len(all_depts))

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


def _build_feishu_to_our_cache() -> Dict[str, int]:
    """从数据库构建 feishu_department_id -> 本地部门 id 的缓存，避免同步用户时重复查库。"""
    cache: Dict[str, int] = {"0": 0}
    flat = department_service.list_all()
    for d in flat:
        fid = d.get("feishuDepartmentId") or d.get("feishu_department_id")
        if fid:
            cache[str(fid)] = d["id"]
    return cache


# ---------- 用户：手机号去国家码、头像 ----------

def _normalize_mobile(mobile: str) -> str:
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
    avatar = feishu_user.get("avatar")
    if isinstance(avatar, dict):
        return (avatar.get("avatar_240") or avatar.get("avatar_72") or "").strip() or None
    if isinstance(avatar, str):
        return avatar.strip() or None
    return None


def _fetch_users_by_departments(feishu_dept_id_to_our: Dict[str, int]) -> List[dict]:
    """按部门拉取：遍历所有有映射的飞书部门，逐个调用「部门下用户」接口，按 open_id 去重。"""
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


def _resolve_our_dept_id(feishu_user: dict, feishu_dept_id_to_our: Dict[str, int]) -> Optional[int]:
    """从飞书用户信息中取第一个部门 id，在缓存中解析为本地部门 id。"""
    raw_depts = feishu_user.get("department_ids") or feishu_user.get("department_id") or feishu_user.get("open_department_id")
    if isinstance(raw_depts, str) and raw_depts.strip():
        raw_depts = [raw_depts]
    elif not isinstance(raw_depts, list):
        raw_depts = []
    for d in raw_depts:
        feishu_dept_id = (d if isinstance(d, str) else str(d)).strip() if d is not None else ""
        if feishu_dept_id and feishu_dept_id in feishu_dept_id_to_our:
            return feishu_dept_id_to_our[feishu_dept_id]
    return None


def sync_users(
    feishu_dept_id_to_our: Dict[str, int],
    overwrite_existing: bool = False,
) -> Dict[str, Any]:
    """
    只同步用户：仍通过部门维度拉取（遍历部门查用户），不处理部门数据。
    - 部门 id：从缓存 feishu_dept_id_to_our 根据 feishu_department_id 得到本地 id 写入用户。
    - 唯一性：按手机号判断是否存在；存在则覆盖则更新、不覆盖则跳过；不存在则插入。
    - 无手机号时用 union_id / feishu_open_id 匹配已存在用户。
    """
    result = {"created": 0, "updated": 0, "skipped": 0, "failed": 0, "errors": []}

    feishu_users = _fetch_users_by_departments(feishu_dept_id_to_our)

    for it in feishu_users:
        open_id = (it.get("open_id") or it.get("user_id") or "").strip()
        if not open_id:
            continue
        name = (it.get("name") or it.get("en_name") or "").strip() or "飞书用户"
        mobile_raw = (it.get("mobile") or "").strip()
        mobile = _normalize_mobile(mobile_raw) or None
        email = (it.get("email") or "").strip() or None
        avatar_url = _get_avatar_url(it)
        our_dept_id = _resolve_our_dept_id(it, feishu_dept_id_to_our)
        union_id_raw = it.get("union_id")
        union_id = str(union_id_raw).strip() if union_id_raw else None

        try:
            # 唯一性：优先手机号，无手机号时用 union_id / feishu_open_id
            existing = None
            if mobile:
                existing = user_service.find_by_mobile(mobile)
            if existing is None and union_id:
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
    1. 先同步所有部门（若勾选），并构建 feishu_department_id -> 本地 id 缓存；
    2. 再同步用户时按部门拉取、用缓存写部门 id，不重复查库；
    3. 若只同步用户，不处理部门数据，但仍从 DB 读缓存用于解析用户部门。
    """
    dept_result = {"created": 0, "updated": 0, "skipped": 0, "failed": 0, "errors": []}
    user_result = {"created": 0, "updated": 0, "skipped": 0, "failed": 0, "errors": []}
    feishu_to_our: Dict[str, int] = {"0": 0}

    if sync_departments_flag:
        dept_result = sync_departments(overwrite_existing=overwrite_existing)
        feishu_to_our = _build_feishu_to_our_cache()

    if sync_users_flag:
        if not feishu_to_our or feishu_to_our == {"0": 0}:
            feishu_to_our = _build_feishu_to_our_cache()
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
