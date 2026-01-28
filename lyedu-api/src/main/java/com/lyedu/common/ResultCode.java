package com.lyedu.common;

import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * 响应码枚举
 *
 * @author LyEdu Team
 */
@Getter
@AllArgsConstructor
public enum ResultCode {

    /**
     * 成功
     */
    SUCCESS(200, "操作成功"),

    /**
     * 失败
     */
    ERROR(500, "操作失败"),

    /**
     * 参数错误
     */
    PARAM_ERROR(400, "参数错误"),

    /**
     * 未授权
     */
    UNAUTHORIZED(401, "未授权"),

    /**
     * 禁止访问
     */
    FORBIDDEN(403, "禁止访问"),

    /**
     * 资源不存在
     */
    NOT_FOUND(404, "资源不存在"),

    /**
     * 用户名或密码错误
     */
    LOGIN_ERROR(1001, "用户名或密码错误"),

    /**
     * 用户不存在
     */
    USER_NOT_FOUND(1002, "用户不存在"),

    /**
     * 用户已存在
     */
    USER_EXISTS(1003, "用户已存在"),

    /**
     * Token 无效
     */
    TOKEN_INVALID(1004, "Token 无效或已过期"),

    /**
     * 课程不存在
     */
    COURSE_NOT_FOUND(2001, "课程不存在"),

    /**
     * 部门不存在
     */
    DEPARTMENT_NOT_FOUND(3001, "部门不存在");

    /**
     * 响应码
     */
    private final Integer code;

    /**
     * 响应消息
     */
    private final String message;
}
