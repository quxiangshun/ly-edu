# -*- coding: utf-8 -*-
"""Loguru 日志配置，统一输出格式并拦截 stdlib logging"""
import logging
import sys

from loguru import logger

# 移除 loguru 默认 handler，添加自定义格式
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# 拦截标准库 logging，使 logging.getLogger() 的输出也经 loguru 处理
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name if record.levelname in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL") else "INFO"
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def _intercept_stdlib():
    """将 root logger 和 uvicorn 等的日志重定向到 loguru"""
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers = [InterceptHandler()]
        lg.propagate = False


_intercept_stdlib()
