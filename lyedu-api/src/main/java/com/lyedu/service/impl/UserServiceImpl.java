package com.lyedu.service.impl;

import com.lyedu.entity.User;
import com.lyedu.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Service;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

/**
 * 用户服务实现（基于 JdbcTemplate，避免 MyBatis 依赖）
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {

    private final JdbcTemplate jdbcTemplate;

    private static final String SELECT_BY_USERNAME_SQL =
            "SELECT id, username, password, real_name, email, mobile, avatar, department_id, role, status, deleted " +
            "FROM ly_user WHERE username = ? AND deleted = 0 LIMIT 1";

    @Override
    public User findByUsername(String username) {
        List<User> list = jdbcTemplate.query(SELECT_BY_USERNAME_SQL, new Object[]{username}, new UserRowMapper());
        return list.isEmpty() ? null : list.get(0);
    }

    private static class UserRowMapper implements RowMapper<User> {
        @Override
        public User mapRow(ResultSet rs, int rowNum) throws SQLException {
            User user = new User();
            user.setId(rs.getLong("id"));
            user.setUsername(rs.getString("username"));
            user.setPassword(rs.getString("password"));
            
            user.setRealName(rs.getString("real_name"));
            
            user.setEmail(rs.getString("email"));
            user.setMobile(rs.getString("mobile"));
            user.setAvatar(rs.getString("avatar"));
            user.setDepartmentId(rs.getLong("department_id"));
            user.setRole(rs.getString("role"));
            user.setStatus(rs.getInt("status"));
            return user;
        }
    }
}

