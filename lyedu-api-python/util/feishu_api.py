# -*- coding: utf-8 -*-
"""飞书开放平台 API（与 Java FeishuApiService 一致；扩展：后续可加 dingtalk_api / wecom_api）"""
from typing import Any, Optional
from urllib.parse import quote

import config

FEISHU_BASE = "https://open.feishu.cn/open-apis"
SCOPE = "contact:user.base:readonly"


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
