# -*- coding: utf-8 -*-
"""JWT 工具，与 Java JwtUtil 对应"""
import time
from typing import Optional

import jwt

import config


def generate_token(user_id: int, username: str) -> str:
    payload = {
        "userId": user_id,
        "username": username,
        "iat": int(time.time()),
        "exp": int(time.time()) + config.JWT_EXPIRE_SECONDS,
    }
    return jwt.encode(
        payload,
        config.JWT_SECRET,
        algorithm="HS256",
    )


def get_user_id_from_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
        return payload.get("userId")
    except Exception:
        return None


def parse_authorization(authorization: Optional[str]) -> Optional[int]:
    if not authorization or not authorization.strip():
        return None
    token = authorization.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    return get_user_id_from_token(token)
