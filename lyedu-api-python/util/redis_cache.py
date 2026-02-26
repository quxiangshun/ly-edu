# -*- coding: utf-8 -*-
"""Redis 缓存工具：get/set/delete，支持 TTL 与 JSON；Redis 不可用时静默降级，不抛错"""
import json
from typing import Any, Optional

try:
    import redis
except ImportError:
    redis = None

import config

# 全局客户端，懒加载
_client: Optional[Any] = None
_key_prefix = "lyedu:"


def _get_client():
    global _client
    if _client is not None:
        return _client
    if redis is None:
        return None
    try:
        host = config.REDIS_HOST
        if host == "localhost":
            host = "127.0.0.1"  # 避免 IPv6 解析导致 exe 连接失败
        _client = redis.Redis(
            host=host,
            port=config.REDIS_PORT,
            username=config.REDIS_USERNAME,
            password=config.REDIS_PASSWORD,
            db=config.REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=10,
        )
        _client.ping()
        return _client
    except Exception:
        _client = None
        return None


def _key(k: str) -> str:
    return _key_prefix + k if _key_prefix else k


def get(key: str) -> Optional[str]:
    """获取字符串缓存，不存在或 Redis 不可用时返回 None"""
    c = _get_client()
    if not c:
        return None
    try:
        v = c.get(_key(key))
        return v if v is None else str(v)
    except Exception:
        return None


def set(key: str, value: str, ttl_seconds: Optional[int] = None) -> bool:
    """设置字符串缓存；ttl_seconds 为 None 表示不过期。成功返回 True，失败返回 False"""
    c = _get_client()
    if not c:
        return False
    try:
        k = _key(key)
        if ttl_seconds is not None:
            c.setex(k, ttl_seconds, value)
        else:
            c.set(k, value)
        return True
    except Exception:
        return False


def delete(key: str) -> bool:
    """删除缓存。成功返回 True，失败或 Redis 不可用返回 False"""
    c = _get_client()
    if not c:
        return False
    try:
        c.delete(_key(key))
        return True
    except Exception:
        return False


def get_json(key: str) -> Optional[Any]:
    """获取 JSON 缓存（dict/list 等），不存在或解析失败或 Redis 不可用时返回 None"""
    raw = get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


def set_json(key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
    """设置 JSON 缓存。成功返回 True，失败返回 False"""
    try:
        raw = json.dumps(value, ensure_ascii=False)
        return set(key, raw, ttl_seconds)
    except (TypeError, ValueError):
        return False


def is_available() -> bool:
    """当前 Redis 是否可用（用于运维或开关逻辑）"""
    return _get_client() is not None
