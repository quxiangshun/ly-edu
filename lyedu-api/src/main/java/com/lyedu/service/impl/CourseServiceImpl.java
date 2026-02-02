package com.lyedu.service.impl;

import com.lyedu.common.PageResult;
import com.lyedu.entity.Course;
import com.lyedu.entity.User;
import com.lyedu.service.CourseService;
import com.lyedu.service.DepartmentService;
import com.lyedu.service.UserService;
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

    private static final String SELECT_COLS = "id, CONVERT(title USING utf8mb4) as title, cover, CONVERT(description USING utf8mb4) as description, category_id, status, sort, is_required, visibility, department_id, create_time, update_time, deleted";

    private final JdbcTemplate jdbcTemplate;
    private final DepartmentService departmentService;
    private final UserService userService;

    @Override
    public PageResult<Course> page(Integer page, Integer size, String keyword, Long categoryId, Long userId) {
        int offset = (page - 1) * size;

        StringBuilder whereClause = new StringBuilder("WHERE deleted = 0");
        List<Object> params = new java.util.ArrayList<>();

        appendVisibilityCondition(whereClause, params, userId);

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

        String querySql = "SELECT " + SELECT_COLS + " FROM ly_course " + whereClause + " ORDER BY sort ASC, id DESC LIMIT ? OFFSET ?";
        List<Object> queryParams = new java.util.ArrayList<>(params);
        queryParams.add(size);
        queryParams.add(offset);

        List<Course> list = jdbcTemplate.query(querySql, queryParams.toArray(), new CourseRowMapper());

        return new PageResult<Course>(list, total, (long) page, (long) size);
    }

    @Override
    public Course getDetailById(Long id, Long userId) {
        String sql = "SELECT " + SELECT_COLS + " FROM ly_course WHERE id = ? AND deleted = 0";
        List<Course> list = jdbcTemplate.query(sql, new Object[]{id}, new CourseRowMapper());
        Course course = list.isEmpty() ? null : list.get(0);
        if (course == null) return null;
        if (!canUserSeeCourse(course, userId)) return null;
        return course;
    }

    @Override
    public void save(Course course) {
        String sql = "INSERT INTO ly_course (title, cover, description, category_id, status, sort, is_required, visibility, department_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)";
        jdbcTemplate.update(sql,
                course.getTitle(),
                course.getCover(),
                course.getDescription(),
                course.getCategoryId(),
                course.getStatus() != null ? course.getStatus() : 1,
                course.getSort() != null ? course.getSort() : 0,
                course.getIsRequired() != null ? course.getIsRequired() : 0,
                course.getVisibility() != null ? course.getVisibility() : 1,
                course.getDepartmentId());
    }

    @Override
    public void update(Course course) {
        String sql = "UPDATE ly_course SET title = ?, cover = ?, description = ?, category_id = ?, status = ?, sort = ?, is_required = ?, visibility = ?, department_id = ? WHERE id = ? AND deleted = 0";
        jdbcTemplate.update(sql,
                course.getTitle(),
                course.getCover(),
                course.getDescription(),
                course.getCategoryId(),
                course.getStatus(),
                course.getSort(),
                course.getIsRequired() != null ? course.getIsRequired() : 0,
                course.getVisibility() != null ? course.getVisibility() : 1,
                course.getDepartmentId(),
                course.getId());
    }

    @Override
    public void delete(Long id) {
        String sql = "UPDATE ly_course SET deleted = 1 WHERE id = ?";
        jdbcTemplate.update(sql, id);
    }

    @Override
    public List<Course> listRecommended(Integer limit, Long userId) {
        StringBuilder where = new StringBuilder("WHERE deleted = 0 AND status = 1");
        List<Object> params = new java.util.ArrayList<>();
        appendVisibilityCondition(where, params, userId);
        String sql = "SELECT " + SELECT_COLS + " FROM ly_course " + where + " ORDER BY sort ASC, id DESC LIMIT ?";
        params.add(limit);
        return jdbcTemplate.query(sql, params.toArray(), new CourseRowMapper());
    }

    /** 公开课程 或 私有且 course.department_id 在用户部门及子部门内；管理员可见全部 */
    private boolean canUserSeeCourse(Course course, Long userId) {
        if (course.getVisibility() != null && course.getVisibility() == 1) return true;
        if (userId == null) return false;
        User user = userService.getById(userId);
        if (user == null) return false;
        if ("admin".equals(user.getRole())) return true;
        if (user.getDepartmentId() == null) return false;
        List<Long> allowedDeptIds = departmentService.getDepartmentIdAndDescendantIds(user.getDepartmentId());
        return course.getDepartmentId() != null && allowedDeptIds.contains(course.getDepartmentId());
    }

    private void appendVisibilityCondition(StringBuilder where, List<Object> params, Long userId) {
        if (userId == null) {
            where.append(" AND visibility = 1");
            return;
        }
        User user = userService.getById(userId);
        if (user == null) {
            where.append(" AND visibility = 1");
            return;
        }
        if ("admin".equals(user.getRole())) return; // 管理员看全部
        if (user.getDepartmentId() == null) {
            where.append(" AND visibility = 1");
            return;
        }
        List<Long> allowedDeptIds = departmentService.getDepartmentIdAndDescendantIds(user.getDepartmentId());
        if (allowedDeptIds.isEmpty()) {
            where.append(" AND visibility = 1");
            return;
        }
        where.append(" AND (visibility = 1 OR (visibility = 0 AND department_id IN (");
        for (int i = 0; i < allowedDeptIds.size(); i++) {
            if (i > 0) where.append(", ");
            where.append("?");
            params.add(allowedDeptIds.get(i));
        }
        where.append(")))");
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
            if (!rs.wasNull()) course.setCategoryId(categoryId);
            course.setStatus(rs.getInt("status"));
            course.setSort(rs.getInt("sort"));
            try {
                int ir = rs.getInt("is_required");
                if (!rs.wasNull()) course.setIsRequired(ir);
            } catch (SQLException ignored) { }
            try {
                int vis = rs.getInt("visibility");
                if (!rs.wasNull()) course.setVisibility(vis);
            } catch (SQLException ignored) { }
            try {
                long deptId = rs.getLong("department_id");
                if (!rs.wasNull()) course.setDepartmentId(deptId);
            } catch (SQLException ignored) { }
            return course;
        }
    }
}
