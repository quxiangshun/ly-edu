# -*- coding: utf-8 -*-
"""认证路由：飞书/钉钉/企微 授权与扫码登录，微信小程序手机号登录；平台由管理后台配置，前端不写死"""
from typing import Optional

from fastapi import APIRouter, Request, Query
from pydantic import BaseModel

from common.result import ResultCode, error, error_result, success
from services.user import user_service
from services.auth import login_log_service
from services.system import config_service
from util.jwt_util import generate_token
from util import feishu_api
from util import wechat_api

router = APIRouter(prefix="/auth", tags=["auth"])

# 平台显示名称映射（内部用，前端通过 platform 识别后自行展示）
_PLATFORM_LABELS: dict[str, str] = {
    "feishu": "飞书",
    "dingtalk": "钉钉",
    "wecom": "企微",
}


class LoginRequest(BaseModel):
    username: str = ""
    password: str = ""


class FeishuCallbackRequest(BaseModel):
    code: str = ""
    redirectUri: str = ""


class WechatMpPhoneRequest(BaseModel):
    """微信小程序：wx.login 的 code + getPhoneNumber 的 code"""
    code: str = ""  # wx.login 返回，用于换 openid/session_key
    phoneCode: str = ""  # getPhoneNumber 返回，用于换手机号


def _ensure_str(v) -> str:
    """数据库可能返回 bytes，统一转为 str"""
    if v is None:
        return ""
    if isinstance(v, bytes):
        return v.decode("utf-8", errors="replace").strip()
    return str(v).strip()


def _stored_password(user: dict) -> str:
    """取数据库密码并保证为 str，与 Java BCrypt 校验兼容"""
    raw = user.get("password")
    if raw is None:
        return ""
    s = _ensure_str(raw)
    return s


@router.post("/login")
def login(body: LoginRequest, request: Request):
    username = (body.username or "").strip()
    password = (body.password or "").strip()
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent", "")

    if not username or not password:
        login_log_service.add_login_log(
            user_id=None,
            username=username,
            ip=ip,
            user_agent=ua,
            channel="password",
            success=False,
            message="PARAM_ERROR",
        )
        return error_result(ResultCode.PARAM_ERROR)

    user = user_service.find_by_username(username)
    if not user:
        login_log_service.add_login_log(
            user_id=None,
            username=username,
            ip=ip,
            user_agent=ua,
            channel="password",
            success=False,
            message="USER_NOT_FOUND",
        )
        return error_result(ResultCode.USER_NOT_FOUND)
    if user.get("status") == 0:
        login_log_service.add_login_log(
            user_id=user.get("id"),
            username=username,
            ip=ip,
            user_agent=ua,
            channel="password",
            success=False,
            message="FORBIDDEN",
        )
        return error_result(ResultCode.FORBIDDEN)

    stored = _stored_password(user)
    if not stored:
        login_log_service.add_login_log(
            user_id=user.get("id"),
            username=username,
            ip=ip,
            user_agent=ua,
            channel="password",
            success=False,
            message="NO_STORED_PASSWORD",
        )
        return error_result(ResultCode.LOGIN_ERROR)
    # 使用 bcrypt 包校验，与 Java Spring BCrypt 哈希兼容
    ok = False
    try:
        import bcrypt

        password_bytes = password.encode("utf-8")
        stored_bytes = stored.encode("utf-8") if isinstance(stored, str) else stored
        ok = bool(bcrypt.checkpw(password_bytes, stored_bytes))
    except Exception:
        ok = False
    if not ok:
        login_log_service.add_login_log(
            user_id=user.get("id"),
            username=username,
            ip=ip,
            user_agent=ua,
            channel="password",
            success=False,
            message="LOGIN_ERROR",
        )
        return error_result(ResultCode.LOGIN_ERROR)

    uid = user.get("id")
    uid = int(uid) if uid is not None else 0
    uname = _ensure_str(user.get("username"))
    token = generate_token(uid, uname)
    if hasattr(token, "decode"):
        token = token.decode("utf-8")

    data = {
        "token": str(token),
        "userInfo": {
            "id": uid,
            "username": uname,
            "realName": _ensure_str(user.get("real_name")) or None,
            "role": _ensure_str(user.get("role")) or "student",
        },
    }
    login_log_service.add_login_log(
        user_id=uid,
        username=uname,
        ip=ip,
        user_agent=ua,
        channel="password",
        success=True,
        message="",
    )
    return success(data)


@router.get("/platform-info")
def auth_platform_info():
    """返回当前应用发布平台（三选一：feishu/dingtalk/wecom），前端据此展示登录方式"""
    platform = (config_service.get_by_key("app.platform") or "feishu").strip().lower()
    if platform not in ("feishu", "dingtalk", "wecom", "wechat_mp", "local"):
        platform = "feishu"
    return success({
        "platform": platform,
        "authLabel": _PLATFORM_LABELS.get(
            platform if platform in _PLATFORM_LABELS else "feishu", "企业"
        ),
    })


@router.get("/feishu/url")
def feishu_url(
    redirect_uri: str,
    state: Optional[str] = None,
    device: Optional[str] = Query(None, description="mobile=App内跳转授权，pc=扫码登录用 goto URL"),
):
    """获取飞书授权 URL。device=pc 时同时返回 qrcodeGoto 供二维码 SDK 使用"""
    try:
        url = feishu_api.build_authorize_url(redirect_uri, state or "")
        data: dict = {"url": url}
        if device == "pc":
            data["qrcodeGoto"] = url  # 扫码登录时 QR SDK 的 goto 参数
        return success(data)
    except ValueError as e:
        return error_result(400, str(e))


@router.get("/feishu/qrcode")
def feishu_qrcode(redirect_uri: str, state: Optional[str] = None):
    """获取飞书扫码登录用 goto URL（PC/浏览器端展示二维码）"""
    try:
        url = feishu_api.build_authorize_url(redirect_uri, state or "")
        return success({"goto": url})
    except ValueError as e:
        return error_result(400, str(e))


@router.post("/feishu/callback")
def feishu_callback(body: FeishuCallbackRequest, request: Request):
    """飞书授权回调：用 code 换用户信息，查找或创建用户，返回 JWT（与 Java POST /auth/feishu/callback 一致）"""
    code = (body.code or "").strip()
    redirect_uri = (body.redirectUri or "").strip()
    if not code:
        return error(400, "缺少 code")
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent", "")

    feishu_user = feishu_api.get_user_info_by_code(code, redirect_uri or None)
    if not feishu_user:
        login_log_service.add_login_log(
            user_id=None,
            username=None,
            ip=ip,
            user_agent=ua,
            channel="feishu",
            success=False,
            message="FEISHU_AUTH_FAILED",
        )
        return error(400, "飞书授权失败或未配置飞书应用")
    feishu_open_id = feishu_user.get("open_id") or feishu_user.get("sub")
    if not feishu_open_id:
        login_log_service.add_login_log(
            user_id=None,
            username=None,
            ip=ip,
            user_agent=ua,
            channel="feishu",
            success=False,
            message="FEISHU_USER_INFO_INVALID",
        )
        return error(400, "飞书用户信息异常")
    feishu_open_id = str(feishu_open_id).strip()
    union_id_raw = feishu_user.get("union_id")
    union_id = str(union_id_raw).strip() if union_id_raw else None
    name = (feishu_user.get("name") or feishu_user.get("name_cn") or "飞书用户").strip() or "飞书用户"
    avatar_url = feishu_user.get("avatar_url") or feishu_user.get("picture")

    user = user_service.find_by_feishu_open_id(feishu_open_id)
    if not user:
        username = "feishu_" + feishu_open_id
        user_service.save(
            username=username,
            password=None,
            real_name=name,
            avatar=avatar_url,
            feishu_open_id=feishu_open_id,
            union_id=union_id,
            role="student",
            status=1,
        )
        user = user_service.find_by_feishu_open_id(feishu_open_id)
    if not user:
        login_log_service.add_login_log(
            user_id=None,
            username=None,
            ip=ip,
            user_agent=ua,
            channel="feishu",
            success=False,
            message="USER_CREATE_FAILED",
        )
        return error(500, "用户创建失败")
    if user.get("status") == 0:
        login_log_service.add_login_log(
            user_id=user.get("id") or 0,
            username=_ensure_str(user.get("username")),
            ip=ip,
            user_agent=ua,
            channel="feishu",
            success=False,
            message="FORBIDDEN",
        )
        return error_result(ResultCode.FORBIDDEN)
    uid = user.get("id") or 0
    uid = int(uid)
    uname = _ensure_str(user.get("username"))
    token = generate_token(uid, uname)
    if hasattr(token, "decode"):
        token = token.decode("utf-8")
    data = {
        "token": str(token),
        "userInfo": {
            "id": uid,
            "username": uname,
            "realName": _ensure_str(user.get("real_name")) or None,
            "role": _ensure_str(user.get("role")) or "student",
        },
    }
    login_log_service.add_login_log(
        user_id=uid,
        username=uname,
        ip=ip,
        user_agent=ua,
        channel="feishu",
        success=True,
        message="",
    )
    return success(data)


def _check_union_id() -> bool:
    """用户表是否有 union_id 列"""
    try:
        import db
        db.query_one("SELECT union_id FROM ly_user LIMIT 1")
        return True
    except Exception:
        return False


@router.post("/wechat-mp/phone")
def wechat_mp_phone_login(body: WechatMpPhoneRequest, request: Request):
    """微信小程序：手机号校验用户是否存在，存在则绑定 union_id 并返回 token"""
    code = (body.code or "").strip()
    phone_code = (body.phoneCode or "").strip()
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent", "")

    if not phone_code:
        login_log_service.add_login_log(
            user_id=None, username=None, ip=ip, user_agent=ua,
            channel="wechat_mp", success=False, message="PHONE_CODE_MISSING",
        )
        return error(400, "缺少手机号授权 code")

    phone_info = wechat_api.get_phone_number(phone_code)
    if not phone_info:
        login_log_service.add_login_log(
            user_id=None, username=None, ip=ip, user_agent=ua,
            channel="wechat_mp", success=False, message="PHONE_DECODE_FAILED",
        )
        return error(400, "获取手机号失败，请重试")

    mobile = (phone_info.get("purePhoneNumber") or phone_info.get("phoneNumber") or "").strip()
    if not mobile:
        return error(400, "未能解析到手机号")

    user = user_service.find_by_mobile(mobile)
    if not user:
        login_log_service.add_login_log(
            user_id=None, username=None, ip=ip, user_agent=ua,
            channel="wechat_mp", success=False, message="USER_NOT_FOUND",
        )
        return error(400, "用户不存在")

    union_id_to_bind = None
    if code:
        session_data = wechat_api.code2session(code)
        if session_data:
            union_id_to_bind = (session_data.get("unionid") or "").strip()
            if not union_id_to_bind:
                union_id_to_bind = (session_data.get("openid") or "").strip()

    if union_id_to_bind and _check_union_id():
        user_service.update(user["id"], union_id=union_id_to_bind)

    if user.get("status") == 0:
        login_log_service.add_login_log(
            user_id=user.get("id"), username=_ensure_str(user.get("username")),
            ip=ip, user_agent=ua, channel="wechat_mp", success=False, message="FORBIDDEN",
        )
        return error_result(ResultCode.FORBIDDEN)

    uid = user.get("id") or 0
    uid = int(uid)
    uname = _ensure_str(user.get("username"))
    token = generate_token(uid, uname)
    if hasattr(token, "decode"):
        token = token.decode("utf-8")
    data = {
        "token": str(token),
        "userInfo": {
            "id": uid,
            "username": uname,
            "realName": _ensure_str(user.get("real_name")) or None,
            "role": _ensure_str(user.get("role")) or "student",
        },
    }
    login_log_service.add_login_log(
        user_id=uid, username=uname, ip=ip, user_agent=ua,
        channel="wechat_mp", success=True, message="",
    )
    return success(data)


# ---------- 钉钉、企微（预留接口，暂未实现） ----------

@router.get("/dingtalk/url")
def dingtalk_url(redirect_uri: str, state: Optional[str] = None):
    """钉钉授权 URL（预留）"""
    return error(501, "钉钉登录暂未开放，请在后端配置 DINGTALK_APP_ID 等并实现")


@router.post("/dingtalk/callback")
def dingtalk_callback():
    """钉钉授权回调（预留）"""
    return error(501, "钉钉登录暂未开放")


@router.get("/dingtalk/qrcode")
def dingtalk_qrcode():
    """钉钉扫码登录（预留）"""
    return error(501, "钉钉扫码登录暂未开放")


@router.get("/wecom/url")
def wecom_url(redirect_uri: str, state: Optional[str] = None):
    """企微授权 URL（预留）"""
    return error(501, "企微登录暂未开放")


@router.post("/wecom/callback")
def wecom_callback():
    """企微授权回调（预留）"""
    return error(501, "企微登录暂未开放")


@router.get("/wecom/qrcode")
def wecom_qrcode():
    """企微扫码登录（预留）"""
    return error(501, "企微扫码登录暂未开放")
