package com.lyedu.service.impl;

import com.lyedu.common.PageResult;
import com.lyedu.entity.Task;
import com.lyedu.entity.User;
import com.lyedu.service.DepartmentService;
import com.lyedu.service.TaskDepartmentService;
import com.lyedu.service.TaskService;
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
import java.util.ArrayList;
import java.util.List;

/**
 * 周期任务服务实现（可见性：无部门=全员，有部门=仅指定部门）
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class TaskServiceImpl implements TaskService {

    private static final String SELECT_COLS = "id, title, description, cycle_type, cycle_config, items, certificate_id, sort, status, start_time, end_time, create_time, update_time, deleted";

    private final JdbcTemplate jdbcTemplate;
    private final DepartmentService departmentService;
    private final UserService userService;
    private final TaskDepartmentService taskDepartmentService;

    @Override
    public PageResult<Task> page(Integer page, Integer size, String keyword, Long userId) {
        int offset = (page - 1) * size;
        StringBuilder where = new StringBuilder("WHERE ly_task.deleted = 0");
        List<Object> params = new ArrayList<>();
        appendVisibilityCondition(where, params, userId);
        if (keyword != null && !keyword.trim().isEmpty()) {
            where.append(" AND ly_task.title LIKE ?");
            params.add("%" + keyword.trim() + "%");
        }
        String countSql = "SELECT COUNT(*) FROM ly_task " + where;
        Integer totalInt = jdbcTemplate.queryForObject(countSql, params.toArray(), Integer.class);
        Long total = totalInt != null ? totalInt.longValue() : 0L;
        String querySql = "SELECT ly_task.id, ly_task.title, ly_task.description, ly_task.cycle_type, ly_task.cycle_config, ly_task.items, ly_task.certificate_id, ly_task.sort, ly_task.status, ly_task.start_time, ly_task.end_time, ly_task.create_time, ly_task.update_time, ly_task.deleted FROM ly_task " + where + " ORDER BY ly_task.sort ASC, ly_task.id DESC LIMIT ? OFFSET ?";
        List<Object> queryParams = new ArrayList<>(params);
        queryParams.add(size);
        queryParams.add(offset);
        List<Task> list = jdbcTemplate.query(querySql, queryParams.toArray(), new TaskRowMapper());
        for (Task t : list) fillDepartmentIds(t);
        return new PageResult<>(list, total, (long) page, (long) size);
    }

    @Override
    public Task getById(Long id, Long userId) {
        Task t = getByIdIgnoreVisibility(id);
        if (t == null) return null;
        if (!canUserSeeTask(t, userId)) return null;
        return t;
    }

    @Override
    public Task getByIdIgnoreVisibility(Long id) {
        if (id == null) return null;
        String sql = "SELECT " + SELECT_COLS + " FROM ly_task WHERE id = ? AND deleted = 0";
        List<Task> list = jdbcTemplate.query(sql, new TaskRowMapper(), id);
        Task t = list.isEmpty() ? null : list.get(0);
        if (t != null) fillDepartmentIds(t);
        return t;
    }

    @Override
    public long save(Task task) {
        String sql = "INSERT INTO ly_task (title, description, cycle_type, cycle_config, items, certificate_id, sort, status, start_time, end_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(con -> {
            PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            int i = 0;
            ps.setString(++i, task.getTitle());
            ps.setString(++i, task.getDescription());
            ps.setString(++i, task.getCycleType() != null ? task.getCycleType() : "once");
            ps.setString(++i, task.getCycleConfig());
            ps.setString(++i, task.getItems() != null ? task.getItems() : "[]");
            ps.setObject(++i, task.getCertificateId());
            ps.setObject(++i, task.getSort() != null ? task.getSort() : 0);
            ps.setObject(++i, task.getStatus() != null ? task.getStatus() : 1);
            ps.setObject(++i, task.getStartTime() != null ? Timestamp.valueOf(task.getStartTime()) : null);
            ps.setObject(++i, task.getEndTime() != null ? Timestamp.valueOf(task.getEndTime()) : null);
            return ps;
        }, keyHolder);
        Number key = keyHolder.getKey();
        long id = key != null ? key.longValue() : 0L;
        if (id > 0 && task.getDepartmentIds() != null && !task.getDepartmentIds().isEmpty()) {
            taskDepartmentService.setTaskDepartments(id, task.getDepartmentIds());
        }
        return id;
    }

    @Override
    public void update(Task task) {
        if (task.getId() == null) return;
        String sql = "UPDATE ly_task SET title = ?, description = ?, cycle_type = ?, cycle_config = ?, items = ?, certificate_id = ?, sort = ?, status = ?, start_time = ?, end_time = ? WHERE id = ? AND deleted = 0";
        jdbcTemplate.update(sql,
                task.getTitle(),
                task.getDescription(),
                task.getCycleType() != null ? task.getCycleType() : "once",
                task.getCycleConfig(),
                task.getItems() != null ? task.getItems() : "[]",
                task.getCertificateId(),
                task.getSort() != null ? task.getSort() : 0,
                task.getStatus() != null ? task.getStatus() : 1,
                task.getStartTime() != null ? Timestamp.valueOf(task.getStartTime()) : null,
                task.getEndTime() != null ? Timestamp.valueOf(task.getEndTime()) : null,
                task.getId());
        taskDepartmentService.setTaskDepartments(task.getId(), task.getDepartmentIds());
    }

    @Override
    public void delete(Long id) {
        if (id == null) return;
        jdbcTemplate.update("UPDATE ly_task SET deleted = 1 WHERE id = ?", id);
        taskDepartmentService.setTaskDepartments(id, null);
    }

    private void fillDepartmentIds(Task t) {
        if (t != null && t.getId() != null) {
            t.setDepartmentIds(taskDepartmentService.listDepartmentIdsByTaskId(t.getId()));
        }
    }

    private static final ObjectMapper JSON_MAPPER = new ObjectMapper();

    private boolean canUserSeeTask(Task t, Long userId) {
        if (userId == null) {
            if ("newcomer".equals(t.getCycleType())) return false;
            List<Long> deptIds = taskDepartmentService.listDepartmentIdsByTaskId(t.getId());
            return deptIds == null || deptIds.isEmpty();
        }
        User user = userService.getById(userId);
        if (user == null) return false;
        if ("admin".equals(user.getRole())) return true;
        if ("newcomer".equals(t.getCycleType())) {
            int withinDays = parseWithinDays(t.getCycleConfig());
            long daysSince = daysSinceEntry(user);
            if (daysSince > withinDays) return false;
        }
        List<Long> deptIds = taskDepartmentService.listDepartmentIdsByTaskId(t.getId());
        if (deptIds == null || deptIds.isEmpty()) return true;
        if (user.getDepartmentId() == null) return false;
        List<Long> allowedDeptIds = departmentService.getDepartmentIdAndDescendantIds(user.getDepartmentId());
        return taskDepartmentService.taskVisibleToDepartments(t.getId(), allowedDeptIds);
    }

    private int parseWithinDays(String cycleConfig) {
        if (cycleConfig == null || cycleConfig.isBlank()) return 9999;
        try {
            JsonNode node = JSON_MAPPER.readTree(cycleConfig);
            if (node != null && node.has("within_days")) return node.get("within_days").asInt(9999);
        } catch (Exception ignored) {}
        return 9999;
    }

    private long daysSinceEntry(User user) {
        java.time.LocalDate ref = user.getEntryDate() != null ? user.getEntryDate() : (user.getCreateTime() != null ? user.getCreateTime().toLocalDate() : null);
        if (ref == null) return 0;
        return ChronoUnit.DAYS.between(ref, java.time.LocalDate.now());
    }

    private void appendVisibilityCondition(StringBuilder where, List<Object> params, Long userId) {
        if (userId == null) {
            where.append(" AND (NOT EXISTS (SELECT 1 FROM ly_task_department td WHERE td.task_id = ly_task.id))");
            appendNewcomerCondition(where, params, null);
            return;
        }
        User user = userService.getById(userId);
        if (user == null) {
            where.append(" AND (NOT EXISTS (SELECT 1 FROM ly_task_department td WHERE td.task_id = ly_task.id))");
            appendNewcomerCondition(where, params, null);
            return;
        }
        if ("admin".equals(user.getRole())) return;
        if (user.getDepartmentId() == null) {
            where.append(" AND (NOT EXISTS (SELECT 1 FROM ly_task_department td WHERE td.task_id = ly_task.id))");
            appendNewcomerCondition(where, params, userId);
            return;
        }
        List<Long> allowedDeptIds = departmentService.getDepartmentIdAndDescendantIds(user.getDepartmentId());
        if (allowedDeptIds.isEmpty()) {
            where.append(" AND (NOT EXISTS (SELECT 1 FROM ly_task_department td WHERE td.task_id = ly_task.id))");
            appendNewcomerCondition(where, params, userId);
            return;
        }
        where.append(" AND (NOT EXISTS (SELECT 1 FROM ly_task_department td WHERE td.task_id = ly_task.id) OR EXISTS (SELECT 1 FROM ly_task_department td WHERE td.task_id = ly_task.id AND td.department_id IN (");
        for (int i = 0; i < allowedDeptIds.size(); i++) {
            if (i > 0) where.append(", ");
            where.append("?");
            params.add(allowedDeptIds.get(i));
        }
        where.append(")))");
        appendNewcomerCondition(where, params, userId);
    }

    /** 新员工任务：仅入职 within_days 天内的用户可见 */
    private void appendNewcomerCondition(StringBuilder where, List<Object> params, Long userId) {
        if (userId == null) {
            where.append(" AND (ly_task.cycle_type IS NULL OR ly_task.cycle_type <> 'newcomer')");
            return;
        }
        where.append(" AND (ly_task.cycle_type IS NULL OR ly_task.cycle_type <> 'newcomer' OR (SELECT DATEDIFF(CURDATE(), COALESCE(u.entry_date, u.create_time)) FROM ly_user u WHERE u.id = ? AND u.deleted = 0) <= CAST(COALESCE(JSON_UNQUOTE(JSON_EXTRACT(ly_task.cycle_config, '$.within_days')), '9999') AS UNSIGNED))");
        params.add(userId);
    }

    private static class TaskRowMapper implements RowMapper<Task> {
        @Override
        public Task mapRow(ResultSet rs, int rowNum) throws SQLException {
            Task t = new Task();
            t.setId(rs.getLong("id"));
            t.setTitle(rs.getString("title"));
            t.setDescription(rs.getString("description"));
            t.setCycleType(rs.getString("cycle_type"));
            t.setCycleConfig(rs.getString("cycle_config"));
            t.setItems(rs.getString("items"));
            t.setCertificateId(rs.getObject("certificate_id") != null ? rs.getLong("certificate_id") : null);
            t.setSort(rs.getObject("sort", Integer.class));
            t.setStatus(rs.getObject("status", Integer.class));
            Timestamp st = rs.getTimestamp("start_time");
            t.setStartTime(st != null ? st.toLocalDateTime() : null);
            Timestamp et = rs.getTimestamp("end_time");
            t.setEndTime(et != null ? et.toLocalDateTime() : null);
            t.setCreateTime(rs.getObject("create_time", LocalDateTime.class));
            t.setUpdateTime(rs.getObject("update_time", LocalDateTime.class));
            t.setDeleted(rs.getObject("deleted", Integer.class));
            return t;
        }
    }
}
