# -*- coding: utf-8 -*-
"""认证路由，与 Java AuthController 对应（含飞书扫码/免登；扩展：后续可加钉钉/企业微信）"""
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from common.result import ResultCode, error, error_result, success
from services import user_service
from util.jwt_util import generate_token
from util import feishu_api

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str = ""
    password: str = ""


class FeishuCallbackRequest(BaseModel):
    code: str = ""
    redirectUri: str = ""


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
def login(body: LoginRequest):
    username = (body.username or "").strip()
    password = (body.password or "").strip()
    if not username or not password:
        return error_result(ResultCode.PARAM_ERROR)

    user = user_service.find_by_username(username)
    if not user:
        return error_result(ResultCode.USER_NOT_FOUND)
    if user.get("status") == 0:
        return error_result(ResultCode.FORBIDDEN)

    stored = _stored_password(user)
    if not stored:
        return error_result(ResultCode.LOGIN_ERROR)
    # 使用 bcrypt 包校验，与 Java Spring BCrypt 哈希兼容（passlib 与部分 Java 哈希不兼容）
    try:
        import bcrypt
        password_bytes = password.encode("utf-8")
        stored_bytes = stored.encode("utf-8") if isinstance(stored, str) else stored
        if not bcrypt.checkpw(password_bytes, stored_bytes):
            return error_result(ResultCode.LOGIN_ERROR)
    except Exception:
        try:
            from passlib.hash import bcrypt as passlib_bcrypt
            if not passlib_bcrypt.verify(password, stored):
                return error_result(ResultCode.LOGIN_ERROR)
        except Exception:
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
    return success(data)


@router.get("/feishu/url")
def feishu_url(redirect_uri: str, state: Optional[str] = None):
    """获取飞书授权页 URL（与 Java GET /auth/feishu/url 一致）"""
    try:
        url = feishu_api.build_authorize_url(redirect_uri, state or "")
        return success({"url": url})
    except ValueError as e:
        return error_result(400, str(e))


@router.post("/feishu/callback")
def feishu_callback(body: FeishuCallbackRequest):
    """飞书授权回调：用 code 换用户信息，查找或创建用户，返回 JWT（与 Java POST /auth/feishu/callback 一致）"""
    code = (body.code or "").strip()
    redirect_uri = (body.redirectUri or "").strip()
    if not code:
        return error(400, "缺少 code")
    feishu_user = feishu_api.get_user_info_by_code(code, redirect_uri or None)
    if not feishu_user:
        return error(400, "飞书授权失败或未配置飞书应用")
    feishu_open_id = feishu_user.get("open_id") or feishu_user.get("sub")
    if not feishu_open_id:
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
        return error(500, "用户创建失败")
    if user.get("status") == 0:
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
    return success(data)
