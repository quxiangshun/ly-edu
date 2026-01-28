package com.lyedu.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 用户实体
 *
 * @author LyEdu Team
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("ly_user")
public class User extends BaseEntity {

    /**
     * 用户名
     */
    private String username;

    /**
     * 密码（加密后）
     */
    private String password;

    /**
     * 真实姓名
     */
    private String realName;

    /**
     * 邮箱
     */
    private String email;

    /**
     * 手机号
     */
    private String mobile;

    /**
     * 头像
     */
    private String avatar;

    /**
     * 部门 ID
     */
    private Long departmentId;

    /**
     * 角色（admin-管理员，teacher-教师，student-学员）
     */
    private String role;

    /**
     * 状态（0-禁用，1-启用）
     */
    private Integer status;
}
