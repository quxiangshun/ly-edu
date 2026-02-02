# -*- coding: utf-8 -*-
"""统一响应结果，与 Java Result/ResultCode 对应"""
import time
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class ResultCode:
    SUCCESS = (200, "操作成功")
    ERROR = (500, "操作失败")
    PARAM_ERROR = (400, "参数错误")
    UNAUTHORIZED = (401, "未授权")
    FORBIDDEN = (403, "禁止访问")
    NOT_FOUND = (404, "资源不存在")
    LOGIN_ERROR = (1001, "用户名或密码错误")
    USER_NOT_FOUND = (1002, "用户不存在")
    USER_EXISTS = (1003, "用户已存在")
    TOKEN_INVALID = (1004, "Token 无效或已过期")
    COURSE_NOT_FOUND = (2001, "课程不存在")
    DEPARTMENT_NOT_FOUND = (3001, "部门不存在")


def success(data: Any = None) -> dict:
    code, message = ResultCode.SUCCESS
    return {"code": code, "message": message, "data": data, "timestamp": int(time.time() * 1000)}


def error(code: int = None, message: str = None) -> dict:
    if code is None:
        code, _ = ResultCode.ERROR
    if message is None:
        _, message = ResultCode.ERROR
    return {"code": code, "message": message, "data": None, "timestamp": int(time.time() * 1000)}


def error_result(result_code: tuple) -> dict:
    return error(result_code[0], result_code[1])
