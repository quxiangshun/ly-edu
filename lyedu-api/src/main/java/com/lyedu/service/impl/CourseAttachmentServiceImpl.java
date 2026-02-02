package com.lyedu.service.impl;

import com.lyedu.entity.CourseAttachment;
import com.lyedu.service.CourseAttachmentService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Service;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

/**
 * 课程附件服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class CourseAttachmentServiceImpl implements CourseAttachmentService {

    private final JdbcTemplate jdbcTemplate;

    @Override
    public List<CourseAttachment> listByCourseId(Long courseId) {
        String sql = "SELECT id, course_id, name, type, file_url, sort, create_time, update_time, deleted " +
                "FROM ly_course_attachment WHERE course_id = ? AND deleted = 0 ORDER BY sort ASC, id ASC";
        return jdbcTemplate.query(sql, new Object[]{courseId}, new CourseAttachmentRowMapper());
    }

    @Override
    public void save(CourseAttachment attachment) {
        String sql = "INSERT INTO ly_course_attachment (course_id, name, type, file_url, sort) VALUES (?, ?, ?, ?, ?)";
        jdbcTemplate.update(sql,
                attachment.getCourseId(),
                attachment.getName(),
                attachment.getType(),
                attachment.getFileUrl(),
                attachment.getSort() != null ? attachment.getSort() : 0);
    }

    @Override
    public void delete(Long id) {
        String sql = "UPDATE ly_course_attachment SET deleted = 1 WHERE id = ?";
        jdbcTemplate.update(sql, id);
    }

    private static class CourseAttachmentRowMapper implements RowMapper<CourseAttachment> {
        @Override
        public CourseAttachment mapRow(ResultSet rs, int rowNum) throws SQLException {
            CourseAttachment a = new CourseAttachment();
            a.setId(rs.getLong("id"));
            a.setCourseId(rs.getLong("course_id"));
            a.setName(rs.getString("name"));
            a.setType(rs.getString("type"));
            a.setFileUrl(rs.getString("file_url"));
            a.setSort(rs.getInt("sort"));
            a.setCreateTime(rs.getTimestamp("create_time").toLocalDateTime());
            a.setUpdateTime(rs.getTimestamp("update_time").toLocalDateTime());
            a.setDeleted(rs.getInt("deleted"));
            return a;
        }
    }
}
