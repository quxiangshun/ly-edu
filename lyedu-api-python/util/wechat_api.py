# -*- coding: utf-8 -*-
"""微信小程序 API：code2session、getPhoneNumber"""
from typing import Any, Optional

import config


def _get_access_token() -> Optional[str]:
    """获取小程序 access_token"""
    if not (config.WECHAT_MP_APP_ID and config.WECHAT_MP_APP_SECRET):
        return None
    try:
        import requests
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={config.WECHAT_MP_APP_ID}&secret={config.WECHAT_MP_APP_SECRET}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if "access_token" in data:
            return data["access_token"]
    except Exception:
        pass
    return None


def code2session(code: str) -> Optional[dict]:
    """wx.login 的 code 换取 openid、session_key、unionid（若已绑定开放平台）"""
    if not (config.WECHAT_MP_APP_ID and config.WECHAT_MP_APP_SECRET) or not code:
        return None
    try:
        import requests
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": config.WECHAT_MP_APP_ID,
            "secret": config.WECHAT_MP_APP_SECRET,
            "js_code": code,
            "grant_type": "authorization_code",
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("errcode") == 0:
            return {
                "openid": data.get("openid") or "",
                "session_key": data.get("session_key"),
                "unionid": data.get("unionid"),
            }
    except Exception:
        pass
    return None


def get_phone_number(phone_code: str) -> Optional[dict]:
    """getPhoneNumber 返回的 code 换取手机号"""
    token = _get_access_token()
    if not token or not phone_code:
        return None
    try:
        import requests
        url = f"https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={token}"
        resp = requests.post(url, json={"code": phone_code}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("errcode") == 0:
            info = data.get("phone_info") or {}
            return {
                "phoneNumber": info.get("phoneNumber") or "",
                "purePhoneNumber": info.get("purePhoneNumber") or "",
                "countryCode": info.get("countryCode") or "86",
            }
    except Exception:
        pass
    return None
