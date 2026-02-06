# -*- coding: utf-8 -*-
"""飞书开放平台 API（与 Java FeishuApiService 一致；扩展：后续可加 dingtalk_api / wecom_api）"""
from typing import Any, List, Optional
from urllib.parse import quote

import config

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
) -> dict:
    """
    获取子部门列表。department_id=0 表示根部门。
    返回 {"items": [{"department_id":"od-xxx","name":"xxx","parent_department_id":"0","order":"0"}, ...], "page_token": "xxx", "has_more": bool}
    """
    token = _get_tenant_access_token()
    if not token:
        return {"items": [], "page_token": "", "has_more": False}
    try:
        import requests
        url = f"{FEISHU_BASE}/contact/v3/departments/{department_id}/children"
        params = {"page_size": page_size}
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
    page_size: int = 50,
    fetch_child: bool = True,
) -> dict:
    """
    获取部门下用户列表（可含子部门）。department_id=0 表示全量。
    返回 {"items": [{"user_id":"ou-xxx","open_id":"xxx","name":"xxx","mobile":"","email":"", "department_ids":["od-xxx"]}, ...], "page_token": "xxx", "has_more": bool}
    """
    token = _get_tenant_access_token()
    if not token:
        return {"items": [], "page_token": "", "has_more": False}
    try:
        import requests
        url = f"{FEISHU_BASE}/contact/v3/users"
        params = {
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
