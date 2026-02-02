package com.lyedu.service.impl;

import com.lyedu.entity.CourseChapter;
import com.lyedu.service.CourseChapterService;
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
import java.util.List;

/**
 * 课程章节服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class CourseChapterServiceImpl implements CourseChapterService {

    private final JdbcTemplate jdbcTemplate;

    @Override
    public List<CourseChapter> listByCourseId(Long courseId) {
        String sql = "SELECT id, course_id, title, sort, create_time, update_time, deleted " +
                "FROM ly_course_chapter WHERE course_id = ? AND deleted = 0 ORDER BY sort ASC, id ASC";
        return jdbcTemplate.query(sql, new Object[]{courseId}, new CourseChapterRowMapper());
    }

    @Override
    public CourseChapter getById(Long id) {
        String sql = "SELECT id, course_id, title, sort, create_time, update_time, deleted " +
                "FROM ly_course_chapter WHERE id = ? AND deleted = 0";
        List<CourseChapter> list = jdbcTemplate.query(sql, new Object[]{id}, new CourseChapterRowMapper());
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    public void save(CourseChapter chapter) {
        String sql = "INSERT INTO ly_course_chapter (course_id, title, sort) VALUES (?, ?, ?)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(con -> {
            PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setObject(1, chapter.getCourseId());
            ps.setString(2, chapter.getTitle());
            ps.setInt(3, chapter.getSort() != null ? chapter.getSort() : 0);
            return ps;
        }, keyHolder);
        if (keyHolder.getKey() != null) {
            chapter.setId(keyHolder.getKey().longValue());
        }
    }

    @Override
    public void update(CourseChapter chapter) {
        String sql = "UPDATE ly_course_chapter SET title = ?, sort = ? WHERE id = ? AND deleted = 0";
        jdbcTemplate.update(sql,
                chapter.getTitle(),
                chapter.getSort() != null ? chapter.getSort() : 0,
                chapter.getId());
    }

    @Override
    public void delete(Long id) {
        String sql = "UPDATE ly_course_chapter SET deleted = 1 WHERE id = ?";
        jdbcTemplate.update(sql, id);
    }

    private static class CourseChapterRowMapper implements RowMapper<CourseChapter> {
        @Override
        public CourseChapter mapRow(ResultSet rs, int rowNum) throws SQLException {
            CourseChapter c = new CourseChapter();
            c.setId(rs.getLong("id"));
            c.setCourseId(rs.getLong("course_id"));
            c.setTitle(rs.getString("title"));
            c.setSort(rs.getInt("sort"));
            c.setCreateTime(rs.getTimestamp("create_time").toLocalDateTime());
            c.setUpdateTime(rs.getTimestamp("update_time").toLocalDateTime());
            c.setDeleted(rs.getInt("deleted"));
            return c;
        }
    }
}
