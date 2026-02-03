package com.lyedu.service.impl;

import com.lyedu.common.CourseCommentDto;
import com.lyedu.entity.CourseComment;
import com.lyedu.service.CourseCommentService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Service;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class CourseCommentServiceImpl implements CourseCommentService {

    private final JdbcTemplate jdbcTemplate;

    @Override
    public List<CourseCommentDto> listByCourse(Long courseId, Long chapterId) {
        String sql = "SELECT c.id, c.course_id, c.chapter_id, c.user_id, c.parent_id, c.content, c.status, c.create_time, " +
                "u.real_name AS user_real_name FROM ly_course_comment c " +
                "LEFT JOIN ly_user u ON c.user_id = u.id AND u.deleted = 0 " +
                "WHERE c.course_id = ? AND c.deleted = 0 AND (c.status IS NULL OR c.status = 1) ";
        List<Object> params = new ArrayList<>();
        params.add(courseId);
        if (chapterId != null) {
            sql += "AND (c.chapter_id IS NULL OR c.chapter_id = ?) ";
            params.add(chapterId);
        }
        sql += "ORDER BY c.id ASC";
        return jdbcTemplate.query(sql, params.toArray(), new CourseCommentDtoRowMapper());
    }

    @Override
    public CourseComment add(Long courseId, Long chapterId, Long userId, Long parentId, String content) {
        String sql = "INSERT INTO ly_course_comment (course_id, chapter_id, user_id, parent_id, content, status) VALUES (?, ?, ?, ?, ?, 1)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(con -> {
            PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setLong(1, courseId);
            ps.setObject(2, chapterId);
            ps.setLong(3, userId);
            ps.setObject(4, parentId);
            ps.setString(5, content != null ? content.trim() : "");
            return ps;
        }, keyHolder);
        Number key = keyHolder.getKey();
        if (key == null) return null;
        CourseComment c = new CourseComment();
        c.setId(key.longValue());
        c.setCourseId(courseId);
        c.setChapterId(chapterId);
        c.setUserId(userId);
        c.setParentId(parentId);
        c.setContent(content);
        c.setStatus(1);
        return c;
    }

    @Override
    public void delete(Long id) {
        jdbcTemplate.update("UPDATE ly_course_comment SET deleted = 1 WHERE id = ?", id);
    }

    private static class CourseCommentDtoRowMapper implements RowMapper<CourseCommentDto> {
        @Override
        public CourseCommentDto mapRow(ResultSet rs, int rowNum) throws SQLException {
            CourseCommentDto dto = new CourseCommentDto();
            dto.setId(rs.getLong("id"));
            dto.setCourseId(rs.getLong("course_id"));
            long ch = rs.getLong("chapter_id");
            dto.setChapterId(rs.wasNull() ? null : ch);
            dto.setUserId(rs.getLong("user_id"));
            dto.setUserRealName(rs.getString("user_real_name"));
            long p = rs.getLong("parent_id");
            dto.setParentId(rs.wasNull() ? null : p);
            dto.setContent(rs.getString("content"));
            dto.setStatus(rs.getObject("status") != null ? rs.getInt("status") : 1);
            dto.setCreateTime(rs.getTimestamp("create_time") != null ? rs.getTimestamp("create_time").toLocalDateTime() : null);
            return dto;
        }
    }
}
