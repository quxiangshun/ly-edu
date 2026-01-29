package com.lyedu.service;

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
}

