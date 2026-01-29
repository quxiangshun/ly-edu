package com.lyedu.service.impl;

import com.lyedu.common.PageResult;
import com.lyedu.entity.User;
import com.lyedu.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.security.crypto.password.PasswordEncoder;
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
    private final PasswordEncoder passwordEncoder;

    private static final String SELECT_BY_USERNAME_SQL =
            "SELECT id, username, password, CONVERT(real_name USING utf8mb4) as real_name, email, mobile, avatar, department_id, role, status, deleted " +
            "FROM ly_user WHERE username = ? AND deleted = 0 LIMIT 1";

    private static final String SELECT_BY_ID_SQL =
            "SELECT id, username, password, CONVERT(real_name USING utf8mb4) as real_name, email, mobile, avatar, department_id, role, status, deleted " +
            "FROM ly_user WHERE id = ? AND deleted = 0";

    private static final String INSERT_SQL =
            "INSERT INTO ly_user (username, password, real_name, email, mobile, avatar, department_id, role, status) " +
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)";

    private static final String UPDATE_SQL =
            "UPDATE ly_user SET real_name = ?, email = ?, mobile = ?, avatar = ?, department_id = ?, role = ?, status = ? " +
            "WHERE id = ? AND deleted = 0";

    private static final String UPDATE_PASSWORD_SQL =
            "UPDATE ly_user SET password = ? WHERE id = ? AND deleted = 0";

    private static final String DELETE_SQL =
            "UPDATE ly_user SET deleted = 1 WHERE id = ?";

    @Override
    public User findByUsername(String username) {
        List<User> list = jdbcTemplate.query(SELECT_BY_USERNAME_SQL, new Object[]{username}, new UserRowMapper());
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    public PageResult<User> page(Integer page, Integer size, String keyword, Long departmentId, String role, Integer status) {
        int offset = (page - 1) * size;
        
        StringBuilder whereClause = new StringBuilder("WHERE deleted = 0");
        List<Object> params = new java.util.ArrayList<>();
        
        if (keyword != null && !keyword.trim().isEmpty()) {
            whereClause.append(" AND (username LIKE ? OR real_name LIKE ? OR email LIKE ? OR mobile LIKE ?)");
            String likeKeyword = "%" + keyword + "%";
            params.add(likeKeyword);
            params.add(likeKeyword);
            params.add(likeKeyword);
            params.add(likeKeyword);
        }
        
        if (departmentId != null) {
            whereClause.append(" AND department_id = ?");
            params.add(departmentId);
        }
        
        if (role != null && !role.trim().isEmpty()) {
            whereClause.append(" AND role = ?");
            params.add(role);
        }
        
        if (status != null) {
            whereClause.append(" AND status = ?");
            params.add(status);
        }
        
        String countSql = "SELECT COUNT(*) FROM ly_user " + whereClause;
        Integer totalInt = jdbcTemplate.queryForObject(countSql, params.toArray(), Integer.class);
        Long total = totalInt != null ? totalInt.longValue() : 0L;
        
        String querySql = "SELECT id, username, password, CONVERT(real_name USING utf8mb4) as real_name, email, mobile, avatar, department_id, role, status, deleted " +
                "FROM ly_user " + whereClause + " ORDER BY id DESC LIMIT ? OFFSET ?";
        List<Object> queryParams = new java.util.ArrayList<>(params);
        queryParams.add(size);
        queryParams.add(offset);
        
        List<User> list = jdbcTemplate.query(querySql, queryParams.toArray(), new UserRowMapper());
        
        return new PageResult<User>(list, total, (long) page, (long) size);
    }

    @Override
    public User getById(Long id) {
        List<User> list = jdbcTemplate.query(SELECT_BY_ID_SQL, new Object[]{id}, new UserRowMapper());
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    public void save(User user) {
        // 如果提供了密码，则加密；否则使用默认密码
        String password = user.getPassword();
        if (password == null || password.trim().isEmpty()) {
            password = "123456"; // 默认密码
        }
        String encodedPassword = passwordEncoder.encode(password);
        
        jdbcTemplate.update(INSERT_SQL,
                user.getUsername(),
                encodedPassword,
                user.getRealName(),
                user.getEmail(),
                user.getMobile(),
                user.getAvatar(),
                user.getDepartmentId(),
                user.getRole() != null ? user.getRole() : "student",
                user.getStatus() != null ? user.getStatus() : 1);
    }

    @Override
    public void update(User user) {
        jdbcTemplate.update(UPDATE_SQL,
                user.getRealName(),
                user.getEmail(),
                user.getMobile(),
                user.getAvatar(),
                user.getDepartmentId(),
                user.getRole(),
                user.getStatus(),
                user.getId());
    }

    @Override
    public void delete(Long id) {
        jdbcTemplate.update(DELETE_SQL, id);
    }

    @Override
    public void updatePassword(Long id, String password) {
        String encodedPassword = passwordEncoder.encode(password);
        jdbcTemplate.update(UPDATE_PASSWORD_SQL, encodedPassword, id);
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
            long deptId = rs.getLong("department_id");
            if (!rs.wasNull()) {
                user.setDepartmentId(deptId);
            }
            user.setRole(rs.getString("role"));
            user.setStatus(rs.getInt("status"));
            return user;
        }
    }
}

