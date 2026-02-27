# -*- coding: utf-8 -*-
"""飞书开放平台 API（与 Java FeishuApiService 一致；扩展：后续可加 dingtalk_api / wecom_api）"""
from typing import Any, List, Optional
from urllib.parse import quote

import config
from loguru import logger

FEISHU_BASE = "https://open.feishu.cn/open-apis"
SCOPE = "contact:user.base:readonly"

# 通讯录同步需要：contact:department:readonly_as_app, contact:user:readonly_as_app
# 在飞书开放平台应用权限中勾选「通讯录-部门信息」「通讯录-用户信息」只读


def _get_tenant_access_token() -> Optional[str]:
    """获取 tenant_access_token（用于通讯录等需要企业维度的接口）"""
    if not (config.FEISHU_APP_ID and config.FEISHU_APP_SECRET):
        return None
    try:
        import requests
        url = f"{FEISHU_BASE}/auth/v3/tenant_access_token/internal"
        resp = requests.post(
            url,
            json={"app_id": config.FEISHU_APP_ID, "app_secret": config.FEISHU_APP_SECRET},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == 0:
            return (data or {}).get("tenant_access_token")
    except Exception:
        pass
    return None


def list_department_children(
    department_id: str,
    page_token: Optional[str] = None,
    page_size: int = 50,
    fetch_child: bool = False,
) -> dict:
    """
    获取子部门列表（文档 4.2）。department_id=0 表示根部门。
    建议 fetch_child=false，只取直接子部门，递归由调用方完成。
    返回 {"items": [{"department_id":"od-xxx","name":"xxx","parent_department_id":"0","order":"0"}, ...], "page_token": "xxx", "has_more": bool}
    """
    token = _get_tenant_access_token()
    if not token:
        return {"items": [], "page_token": "", "has_more": False}
    try:
        import requests
        path_id = "0" if (department_id == "0" or not department_id) else quote(str(department_id), safe="")
        url = f"{FEISHU_BASE}/contact/v3/departments/{path_id}/children"
        params = {
            "user_id_type": "open_id",
            "department_id_type": "department_id",
            "fetch_child": str(fetch_child).lower(),
            "page_size": page_size,
        }
        if page_token:
            params["page_token"] = page_token
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            try:
                logger.warning(
                    "feishu list_department_children code={} msg={}",
                    data.get("code"),
                    data.get("msg", ""),
                )
            except Exception:
                pass
            return {"items": [], "page_token": "", "has_more": False}
        d = data.get("data") or {}
        return {
            "items": d.get("items") or [],
            "page_token": d.get("page_token") or "",
            "has_more": bool(d.get("has_more")),
        }
    except Exception as e:
        try:
            logger.warning(
                "feishu list_department_children 请求异常 department_id={}: {}",
                department_id, e,
            )
        except Exception:
            pass
        return {"items": [], "page_token": "", "has_more": False}


def list_departments_by_parent(
    parent_department_id: str,
    page_token: Optional[str] = None,
    page_size: int = 100,
) -> dict:
    """
    按父部门 ID 获取子部门列表（仅用于根 0 的兜底；飞书仅保证「子部门」接口 /departments/{id}/children 可用）。
    parent_department_id=0 表示根部门下的直属部门。非根部门请用 list_department_children。
    返回格式与 list_department_children 一致。
    """
    token = _get_tenant_access_token()
    if not token:
        return {"items": [], "page_token": "", "has_more": False}
    try:
        import requests
        # 飞书无 /department/list，使用 /departments 路径尝试根部门兜底；若 404 则调用方仅依赖 children 接口
        url = f"{FEISHU_BASE}/contact/v3/departments"
        params = {
            "parent_department_id": parent_department_id,
            "page_size": page_size,
        }
        if page_token:
            params["page_token"] = page_token
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            timeout=15,
        )
        # 飞书可能无此路径，404 时静默返回空，避免异常日志
        if resp.status_code == 404:
            return {"items": [], "page_token": "", "has_more": False}
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            try:
                logger.warning(
                    "feishu list_departments_by_parent code={} msg={} parent_department_id={}",
                    data.get("code"),
                    data.get("msg", ""),
                    parent_department_id,
                )
            except Exception:
                pass
            return {"items": [], "page_token": "", "has_more": False}
        d = data.get("data") or {}
        items = d.get("items") or d.get("departments") or []
        return {
            "items": items,
            "page_token": d.get("page_token") or "",
            "has_more": bool(d.get("has_more")),
        }
    except Exception as e:
        try:
            logger.warning(
                "feishu list_departments_by_parent 请求异常 parent_department_id={}: {}",
                parent_department_id, e,
            )
        except Exception:
            pass
        return {"items": [], "page_token": "", "has_more": False}


def list_all_users(
    page_token: Optional[str] = None,
    page_size: int = 50,
) -> dict:
    """
    方式 A：全量用户列表（不传 department_id），分页拉取。
    文档：GET contact/v3/users，仅 page_size、page_token。
    返回 {"items": [...], "page_token": "xxx", "has_more": bool}
    """
    token = _get_tenant_access_token()
    if not token:
        return {"items": [], "page_token": "", "has_more": False}
    try:
        import requests
        url = f"{FEISHU_BASE}/contact/v3/users"
        params = {
            "user_id_type": "open_id",
            "department_id_type": "department_id",
            "page_size": page_size,
        }
        if page_token:
            params["page_token"] = page_token
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            try:
                logger.warning(
                    "feishu list_all_users code={} msg={}",
                    data.get("code"),
                    data.get("msg", ""),
                )
            except Exception:
                pass
            return {"items": [], "page_token": "", "has_more": False}
        d = data.get("data") or {}
        return {
            "items": d.get("items") or [],
            "page_token": d.get("page_token") or "",
            "has_more": bool(d.get("has_more")),
        }
    except Exception:
        return {"items": [], "page_token": "", "has_more": False}


def list_users_by_department(
    department_id: str,
    page_token: Optional[str] = None,
    page_size: int = 100,
    fetch_child: bool = True,
) -> dict:
    """
    获取部门下用户列表（可含子部门）。department_id=0 表示全量。
    方式 B 兜底：按部门拉取时使用。
    返回 {"items": [{"user_id":"ou-xxx","open_id":"xxx","name":"xxx","mobile":"","email":"", "department_ids":["od-xxx"]}, ...], "page_token": "xxx", "has_more": bool}
    """
    token = _get_tenant_access_token()
    if not token:
        return {"items": [], "page_token": "", "has_more": False}
    try:
        import requests
        url = f"{FEISHU_BASE}/contact/v3/users"
        params = {
            "user_id_type": "open_id",
            "department_id_type": "department_id",
            "department_id": department_id,
            "page_size": page_size,
            "fetch_child": str(fetch_child).lower(),
        }
        if page_token:
            params["page_token"] = page_token
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            try:
                logger.warning(
                    "feishu list_users_by_department code={} msg={}",
                    data.get("code"),
                    data.get("msg", ""),
                )
            except Exception:
                pass
            return {"items": [], "page_token": "", "has_more": False}
        d = data.get("data") or {}
        return {
            "items": d.get("items") or [],
            "page_token": d.get("page_token") or "",
            "has_more": bool(d.get("has_more")),
        }
    except Exception:
        return {"items": [], "page_token": "", "has_more": False}


def build_authorize_url(redirect_uri: str, state: Optional[str] = None) -> str:
    if not (config.FEISHU_APP_ID or config.FEISHU_APP_ID.strip()):
        raise ValueError("飞书 App ID 未配置")
    encoded = quote(redirect_uri, safe="")
    url = f"{FEISHU_BASE}/authen/v1/authorize?app_id={config.FEISHU_APP_ID}&redirect_uri={encoded}&response_type=code&scope={SCOPE}"
    if state:
        url += f"&state={quote(state, safe='')}"
    return url


def get_user_info_by_code(code: str, redirect_uri: Optional[str] = None) -> Optional[dict]:
    if not (config.FEISHU_APP_ID and config.FEISHU_APP_SECRET):
        return None
    redirect_uri = redirect_uri or config.FEISHU_REDIRECT_URI or ""
    try:
        import requests
        app_url = f"{FEISHU_BASE}/auth/v3/app_access_token/internal"
        app_resp = requests.post(app_url, json={"app_id": config.FEISHU_APP_ID, "app_secret": config.FEISHU_APP_SECRET}, timeout=10)
        app_resp.raise_for_status()
        app_data = app_resp.json()
        app_token = (app_data or {}).get("app_access_token")
        if not app_token:
            return None
        oidc_url = f"{FEISHU_BASE}/authen/v1/oidc/access_token"
        oidc_resp = requests.post(
            oidc_url,
            headers={"Authorization": f"Bearer {app_token}", "Content-Type": "application/json"},
            json={"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri},
            timeout=10,
        )
        oidc_resp.raise_for_status()
        oidc_data = oidc_resp.json()
        data = (oidc_data or {}).get("data")
        if not isinstance(data, dict):
            return None
        user_token = data.get("access_token")
        if not user_token:
            return None
        user_url = f"{FEISHU_BASE}/authen/v1/user_info"
        user_resp = requests.get(user_url, headers={"Authorization": f"Bearer {user_token}"}, timeout=10)
        user_resp.raise_for_status()
        user_data = user_resp.json()
        ud = (user_data or {}).get("data")
        return ud if isinstance(ud, dict) else None
    except Exception:
        return None
