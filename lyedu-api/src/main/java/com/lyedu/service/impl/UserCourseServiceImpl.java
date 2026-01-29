package com.lyedu.service.impl;

import com.lyedu.entity.UserCourse;
import com.lyedu.service.UserCourseService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Service;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

/**
 * 用户课程服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class UserCourseServiceImpl implements UserCourseService {

    private final JdbcTemplate jdbcTemplate;

    @Override
    public void joinCourse(Long userId, Long courseId) {
        String checkSql = "SELECT COUNT(*) FROM ly_user_course WHERE user_id = ? AND course_id = ?";
        Integer count = jdbcTemplate.queryForObject(checkSql, new Object[]{userId, courseId}, Integer.class);
        
        if (count == 0) {
            String insertSql = "INSERT INTO ly_user_course (user_id, course_id, progress, status) VALUES (?, ?, 0, 0)";
            jdbcTemplate.update(insertSql, userId, courseId);
        }
    }

    @Override
    public List<UserCourse> listByUserId(Long userId) {
        String sql = "SELECT id, user_id, course_id, progress, status, create_time, update_time " +
                "FROM ly_user_course WHERE user_id = ? ORDER BY update_time DESC";
        return jdbcTemplate.query(sql, new Object[]{userId}, new UserCourseRowMapper());
    }

    @Override
    public UserCourse getByUserAndCourse(Long userId, Long courseId) {
        String sql = "SELECT id, user_id, course_id, progress, status, create_time, update_time " +
                "FROM ly_user_course WHERE user_id = ? AND course_id = ?";
        List<UserCourse> list = jdbcTemplate.query(sql, new Object[]{userId, courseId}, new UserCourseRowMapper());
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    public void updateProgress(Long userId, Long courseId, Integer progress) {
        String sql = "UPDATE ly_user_course SET progress = ?, status = ? WHERE user_id = ? AND course_id = ?";
        Integer status = progress >= 100 ? 1 : 0;
        jdbcTemplate.update(sql, progress, status, userId, courseId);
    }

    private static class UserCourseRowMapper implements RowMapper<UserCourse> {
        @Override
        public UserCourse mapRow(ResultSet rs, int rowNum) throws SQLException {
            UserCourse uc = new UserCourse();
            uc.setId(rs.getLong("id"));
            uc.setUserId(rs.getLong("user_id"));
            uc.setCourseId(rs.getLong("course_id"));
            uc.setProgress(rs.getInt("progress"));
            uc.setStatus(rs.getInt("status"));
            uc.setCreateTime(rs.getTimestamp("create_time").toLocalDateTime());
            uc.setUpdateTime(rs.getTimestamp("update_time").toLocalDateTime());
            return uc;
        }
    }
}
