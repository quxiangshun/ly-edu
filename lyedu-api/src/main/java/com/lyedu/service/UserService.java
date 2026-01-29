package com.lyedu.service;

import com.lyedu.common.PageResult;
import com.lyedu.entity.User;

/**
 * 用户服务接口
 *
 * @author LyEdu Team
 */
public interface UserService {

    /**
     * 根据用户名查询用户
     *
     * @param username 用户名
     * @return 用户实体，未找到返回 null
     */
    User findByUsername(String username);

    /**
     * 分页查询用户
     *
     * @param page 页码（从1开始）
     * @param size 每页大小
     * @param keyword 关键词（用户名、真实姓名、邮箱、手机号）
     * @param departmentId 部门ID（可选）
     * @param role 角色（可选）
     * @param status 状态（可选）
     * @return 分页结果
     */
    PageResult<User> page(Integer page, Integer size, String keyword, Long departmentId, String role, Integer status);

    /**
     * 根据ID查询用户
     *
     * @param id 用户ID
     * @return 用户实体，未找到返回 null
     */
    User getById(Long id);

    /**
     * 创建用户
     *
     * @param user 用户实体
     */
    void save(User user);

    /**
     * 更新用户
     *
     * @param user 用户实体
     */
    void update(User user);

    /**
     * 删除用户（软删除）
     *
     * @param id 用户ID
     */
    void delete(Long id);

    /**
     * 重置用户密码
     *
     * @param id 用户ID
     * @param password 新密码（明文）
     */
    void updatePassword(Long id, String password);
}
