package com.lyedu.service.impl;

import com.lyedu.common.PageResult;
import com.lyedu.entity.Course;
import com.lyedu.service.CourseService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Service;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

/**
 * 课程服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class CourseServiceImpl implements CourseService {

    private final JdbcTemplate jdbcTemplate;

    @Override
    public PageResult<Course> page(Integer page, Integer size, String keyword, Long categoryId) {
        int offset = (page - 1) * size;
        
        StringBuilder whereClause = new StringBuilder("WHERE deleted = 0");
        List<Object> params = new java.util.ArrayList<>();
        
        if (keyword != null && !keyword.trim().isEmpty()) {
            whereClause.append(" AND (title LIKE ? OR description LIKE ?)");
            String likeKeyword = "%" + keyword + "%";
            params.add(likeKeyword);
            params.add(likeKeyword);
        }
        
        if (categoryId != null) {
            whereClause.append(" AND category_id = ?");
            params.add(categoryId);
        }
        
        String countSql = "SELECT COUNT(*) FROM ly_course " + whereClause;
        Integer totalInt = jdbcTemplate.queryForObject(countSql, params.toArray(), Integer.class);
        Long total = totalInt != null ? totalInt.longValue() : 0L;
        
        String querySql = "SELECT id, CONVERT(title USING utf8mb4) as title, cover, CONVERT(description USING utf8mb4) as description, category_id, status, sort, create_time, update_time, deleted " +
                "FROM ly_course " + whereClause + " ORDER BY sort ASC, id DESC LIMIT ? OFFSET ?";
        List<Object> queryParams = new java.util.ArrayList<>(params);
        queryParams.add(size);
        queryParams.add(offset);
        
        List<Course> list = jdbcTemplate.query(querySql, queryParams.toArray(), new CourseRowMapper());
        
        return new PageResult<Course>(list, total, (long) page, (long) size);
    }

    @Override
    public Course getDetailById(Long id) {
        String sql = "SELECT id, CONVERT(title USING utf8mb4) as title, cover, CONVERT(description USING utf8mb4) as description, category_id, status, sort, create_time, update_time, deleted " +
                "FROM ly_course WHERE id = ? AND deleted = 0";
        List<Course> list = jdbcTemplate.query(sql, new Object[]{id}, new CourseRowMapper());
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    public void save(Course course) {
        String sql = "INSERT INTO ly_course (title, cover, description, category_id, status, sort) VALUES (?, ?, ?, ?, ?, ?)";
        jdbcTemplate.update(sql,
                course.getTitle(),
                course.getCover(),
                course.getDescription(),
                course.getCategoryId(),
                course.getStatus() != null ? course.getStatus() : 1,
                course.getSort() != null ? course.getSort() : 0);
    }

    @Override
    public void update(Course course) {
        String sql = "UPDATE ly_course SET title = ?, cover = ?, description = ?, category_id = ?, status = ?, sort = ? WHERE id = ? AND deleted = 0";
        jdbcTemplate.update(sql,
                course.getTitle(),
                course.getCover(),
                course.getDescription(),
                course.getCategoryId(),
                course.getStatus(),
                course.getSort(),
                course.getId());
    }

    @Override
    public void delete(Long id) {
        String sql = "UPDATE ly_course SET deleted = 1 WHERE id = ?";
        jdbcTemplate.update(sql, id);
    }

    @Override
    public List<Course> listRecommended(Integer limit) {
        String sql = "SELECT id, CONVERT(title USING utf8mb4) as title, cover, CONVERT(description USING utf8mb4) as description, category_id, status, sort, create_time, update_time, deleted " +
                "FROM ly_course WHERE deleted = 0 AND status = 1 ORDER BY sort ASC, id DESC LIMIT ?";
        return jdbcTemplate.query(sql, new Object[]{limit}, new CourseRowMapper());
    }

    private static class CourseRowMapper implements RowMapper<Course> {
        @Override
        public Course mapRow(ResultSet rs, int rowNum) throws SQLException {
            Course course = new Course();
            course.setId(rs.getLong("id"));
            course.setTitle(rs.getString("title"));
            course.setCover(rs.getString("cover"));
            course.setDescription(rs.getString("description"));
            Long categoryId = rs.getLong("category_id");
            if (!rs.wasNull()) {
                course.setCategoryId(categoryId);
            }
            course.setStatus(rs.getInt("status"));
            course.setSort(rs.getInt("sort"));
            return course;
        }
    }
}
