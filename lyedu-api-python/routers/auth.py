# -*- coding: utf-8 -*-
"""认证路由，与 Java AuthController 对应"""
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from common.result import ResultCode, error_result, success
from services import user_service
from util.jwt_util import generate_token

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str = ""
    password: str = ""


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
