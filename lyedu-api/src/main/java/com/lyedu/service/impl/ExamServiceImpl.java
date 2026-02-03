package com.lyedu.service.impl;

import com.lyedu.common.PageResult;
import com.lyedu.entity.Exam;
import com.lyedu.entity.User;
import com.lyedu.service.DepartmentService;
import com.lyedu.service.ExamDepartmentService;
import com.lyedu.service.ExamService;
import com.lyedu.service.UserService;
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
import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 考试任务服务实现（可见性规则同知识库：公开或私有且部门在 ly_exam_department）
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class ExamServiceImpl implements ExamService {

    private static final String SELECT_COLS = "id, title, paper_id, start_time, end_time, duration_minutes, pass_score, visibility, status, create_time, update_time, deleted";

    private final JdbcTemplate jdbcTemplate;
    private final DepartmentService departmentService;
    private final UserService userService;
    private final ExamDepartmentService examDepartmentService;

    @Override
    public PageResult<Exam> page(Integer page, Integer size, String keyword, Long userId) {
        int offset = (page - 1) * size;
        StringBuilder where = new StringBuilder("WHERE deleted = 0");
        List<Object> params = new java.util.ArrayList<>();
        appendVisibilityCondition(where, params, userId);
        if (keyword != null && !keyword.trim().isEmpty()) {
            where.append(" AND title LIKE ?");
            params.add("%" + keyword.trim() + "%");
        }
        String countSql = "SELECT COUNT(*) FROM ly_exam " + where;
        Integer totalInt = jdbcTemplate.queryForObject(countSql, params.toArray(), Integer.class);
        Long total = totalInt != null ? totalInt.longValue() : 0L;
        String querySql = "SELECT " + SELECT_COLS + " FROM ly_exam " + where + " ORDER BY id DESC LIMIT ? OFFSET ?";
        List<Object> queryParams = new java.util.ArrayList<>(params);
        queryParams.add(size);
        queryParams.add(offset);
        List<Exam> list = jdbcTemplate.query(querySql, queryParams.toArray(), new ExamRowMapper());
        for (Exam e : list) fillDepartmentIds(e);
        return new PageResult<>(list, total, (long) page, (long) size);
    }

    @Override
    public Exam getById(Long id, Long userId) {
        Exam e = getByIdIgnoreVisibility(id);
        if (e == null) return null;
        if (!canUserSeeExam(e, userId)) return null;
        return e;
    }

    @Override
    public Exam getByIdIgnoreVisibility(Long id) {
        String sql = "SELECT " + SELECT_COLS + " FROM ly_exam WHERE id = ? AND deleted = 0";
        List<Exam> list = jdbcTemplate.query(sql, new Object[]{id}, new ExamRowMapper());
        Exam e = list.isEmpty() ? null : list.get(0);
        if (e != null) fillDepartmentIds(e);
        return e;
    }

    @Override
    public long save(Exam exam) {
        String sql = "INSERT INTO ly_exam (title, paper_id, start_time, end_time, duration_minutes, pass_score, visibility, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(con -> {
            PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            int i = 0;
            ps.setString(++i, exam.getTitle());
            ps.setLong(++i, exam.getPaperId());
            ps.setObject(++i, exam.getStartTime() != null ? Timestamp.valueOf(exam.getStartTime()) : null);
            ps.setObject(++i, exam.getEndTime() != null ? Timestamp.valueOf(exam.getEndTime()) : null);
            ps.setObject(++i, exam.getDurationMinutes());
            ps.setObject(++i, exam.getPassScore());
            ps.setObject(++i, exam.getVisibility() != null ? exam.getVisibility() : 1);
            ps.setObject(++i, exam.getStatus() != null ? exam.getStatus() : 1);
            return ps;
        }, keyHolder);
        Number key = keyHolder.getKey();
        long id = key != null ? key.longValue() : 0L;
        if (id > 0 && exam.getDepartmentIds() != null && !exam.getDepartmentIds().isEmpty()) {
            examDepartmentService.setExamDepartments(id, exam.getDepartmentIds());
        }
        return id;
    }

    @Override
    public void update(Exam exam) {
        if (exam.getId() == null) return;
        String sql = "UPDATE ly_exam SET title = ?, paper_id = ?, start_time = ?, end_time = ?, duration_minutes = ?, pass_score = ?, visibility = ?, status = ? WHERE id = ? AND deleted = 0";
        jdbcTemplate.update(sql,
                exam.getTitle(),
                exam.getPaperId(),
                exam.getStartTime() != null ? Timestamp.valueOf(exam.getStartTime()) : null,
                exam.getEndTime() != null ? Timestamp.valueOf(exam.getEndTime()) : null,
                exam.getDurationMinutes(),
                exam.getPassScore(),
                exam.getVisibility() != null ? exam.getVisibility() : 1,
                exam.getStatus() != null ? exam.getStatus() : 1,
                exam.getId());
        examDepartmentService.setExamDepartments(exam.getId(), exam.getDepartmentIds());
    }

    @Override
    public void delete(Long id) {
        if (id == null) return;
        jdbcTemplate.update("UPDATE ly_exam SET deleted = 1 WHERE id = ?", id);
        examDepartmentService.setExamDepartments(id, null);
    }

    private void fillDepartmentIds(Exam e) {
        if (e != null && e.getId() != null) {
            e.setDepartmentIds(examDepartmentService.listDepartmentIdsByExamId(e.getId()));
        }
    }

    private boolean canUserSeeExam(Exam e, Long userId) {
        if (e.getVisibility() != null && e.getVisibility() == 1) return true;
        if (userId == null) return false;
        User user = userService.getById(userId);
        if (user == null) return false;
        if ("admin".equals(user.getRole())) return true;
        if (user.getDepartmentId() == null) return false;
        List<Long> allowedDeptIds = departmentService.getDepartmentIdAndDescendantIds(user.getDepartmentId());
        return examDepartmentService.examVisibleToDepartments(e.getId(), allowedDeptIds);
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
        if ("admin".equals(user.getRole())) return;
        if (user.getDepartmentId() == null) {
            where.append(" AND visibility = 1");
            return;
        }
        List<Long> allowedDeptIds = departmentService.getDepartmentIdAndDescendantIds(user.getDepartmentId());
        if (allowedDeptIds.isEmpty()) {
            where.append(" AND visibility = 1");
            return;
        }
        where.append(" AND (visibility = 1 OR (visibility = 0 AND EXISTS (SELECT 1 FROM ly_exam_department ed WHERE ed.exam_id = ly_exam.id AND ed.department_id IN (");
        for (int i = 0; i < allowedDeptIds.size(); i++) {
            if (i > 0) where.append(", ");
            where.append("?");
            params.add(allowedDeptIds.get(i));
        }
        where.append("))))");
    }

    private static class ExamRowMapper implements RowMapper<Exam> {
        @Override
        public Exam mapRow(ResultSet rs, int rowNum) throws SQLException {
            Exam e = new Exam();
            e.setId(rs.getLong("id"));
            e.setTitle(rs.getString("title"));
            e.setPaperId(rs.getLong("paper_id"));
            java.sql.Timestamp st = rs.getTimestamp("start_time");
            e.setStartTime(st != null ? st.toLocalDateTime() : null);
            java.sql.Timestamp et = rs.getTimestamp("end_time");
            e.setEndTime(et != null ? et.toLocalDateTime() : null);
            e.setDurationMinutes(rs.getObject("duration_minutes", Integer.class));
            e.setPassScore(rs.getObject("pass_score", Integer.class));
            e.setVisibility(rs.getObject("visibility", Integer.class));
            e.setStatus(rs.getObject("status", Integer.class));
            e.setCreateTime(rs.getObject("create_time", LocalDateTime.class));
            e.setUpdateTime(rs.getObject("update_time", LocalDateTime.class));
            e.setDeleted(rs.getObject("deleted", Integer.class));
            return e;
        }
    }
}
