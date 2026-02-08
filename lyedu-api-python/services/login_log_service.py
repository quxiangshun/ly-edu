# -*- coding: utf-8 -*-
"""登录监控日志服务"""
from typing import Optional

import db


def add_login_log(
    *,
    user_id: Optional[int],
    username: Optional[str],
    ip: Optional[str],
    user_agent: Optional[str],
    channel: str,
    success: bool,
    message: str = "",
) -> None:
  """写入一条登录日志。失败不影响主流程。"""
  try:
    db.execute(
        "INSERT INTO ly_login_log (user_id, username, ip, user_agent, channel, success, message) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (
            user_id,
            (username or "").strip() or None,
            (ip or "").strip() or None,
            (user_agent or "").strip() or None,
            (channel or "").strip() or None,
            1 if success else 0,
            (message or "").strip() or None,
        ),
    )
  except Exception:
    # 日志失败不抛出，避免影响正常登录
    return

