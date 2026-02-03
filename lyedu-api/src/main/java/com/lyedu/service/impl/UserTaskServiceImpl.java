package com.lyedu.service.impl;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.lyedu.common.TaskWithUserProgressDto;
import com.lyedu.entity.Task;
import com.lyedu.entity.UserTask;
import com.lyedu.service.TaskService;
import com.lyedu.service.UserCertificateService;
import com.lyedu.service.UserTaskService;
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
import java.util.Map;

/**
 * 用户任务进度服务实现（闯关进度、全部完成时颁发证书）
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class UserTaskServiceImpl implements UserTaskService {

    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
    private static final String SELECT_COLS = "id, user_id, task_id, progress, status, completed_at, create_time, update_time";

    private final JdbcTemplate jdbcTemplate;
    private final TaskService taskService;
    private final UserCertificateService userCertificateService;

    @Override
    public List<TaskWithUserProgressDto> listMyTasks(Long userId) {
        if (userId == null) return List.of();
        com.lyedu.common.PageResult<Task> page = taskService.page(1, 500, null, userId);
        List<Task> tasks = page.getRecords() != null ? page.getRecords() : List.of();
        List<TaskWithUserProgressDto> result = new ArrayList<>();
        for (Task task : tasks) {
            UserTask ut = getByUserAndTask(userId, task.getId());
            TaskWithUserProgressDto dto = new TaskWithUserProgressDto();
            dto.setTask(task);
            dto.setUserTask(ut);
            result.add(dto);
        }
        return result;
    }

    @Override
    public Task getTaskDetail(Long taskId, Long userId) {
        return taskService.getById(taskId, userId);
    }

    @Override
    public UserTask getOrCreateUserTask(Long taskId, Long userId) {
        if (taskId == null || userId == null) return null;
        Task task = taskService.getById(taskId, userId);
        if (task == null) return null;
        UserTask ut = getByUserAndTask(userId, taskId);
        if (ut != null) return ut;
        String sql = "INSERT INTO ly_user_task (user_id, task_id, progress, status) VALUES (?, ?, '{\"items\":[]}', 0)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(con -> {
            PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setLong(1, userId);
            ps.setLong(2, taskId);
            return ps;
        }, keyHolder);
        Number key = keyHolder.getKey();
        if (key == null) return null;
        return getById(key.longValue());
    }

    @Override
    public UserTask updateProgress(Long taskId, Long userId, String progressJson) {
        if (taskId == null || userId == null) return null;
        UserTask ut = getByUserAndTask(userId, taskId);
        if (ut == null) ut = getOrCreateUserTask(taskId, userId);
        if (ut == null) return null;
        if (ut.getStatus() != null && ut.getStatus() == 1) return ut;

        String sql = "UPDATE ly_user_task SET progress = ?, update_time = NOW() WHERE id = ?";
        jdbcTemplate.update(sql, progressJson != null ? progressJson : "{}", ut.getId());

        Task task = taskService.getByIdIgnoreVisibility(taskId);
        if (task != null && isAllItemsDone(task.getItems(), progressJson)) {
            LocalDateTime now = LocalDateTime.now();
            jdbcTemplate.update("UPDATE ly_user_task SET status = 1, completed_at = ?, update_time = ? WHERE id = ?",
                    Timestamp.valueOf(now), Timestamp.valueOf(now), ut.getId());
            if (task.getCertificateId() != null) {
                userCertificateService.issueIfEligible("task", taskId, userId);
            }
        }

        return getByUserAndTask(userId, taskId);
    }

    private UserTask getByUserAndTask(Long userId, Long taskId) {
        if (userId == null || taskId == null) return null;
        String sql = "SELECT " + SELECT_COLS + " FROM ly_user_task WHERE user_id = ? AND task_id = ?";
        List<UserTask> list = jdbcTemplate.query(sql, new UserTaskRowMapper(), userId, taskId);
        return list.isEmpty() ? null : list.get(0);
    }

    private UserTask getById(Long id) {
        if (id == null) return null;
        String sql = "SELECT " + SELECT_COLS + " FROM ly_user_task WHERE id = ?";
        List<UserTask> list = jdbcTemplate.query(sql, new UserTaskRowMapper(), id);
        return list.isEmpty() ? null : list.get(0);
    }

    /** 解析 task.items 与 progress，判断是否全部完成 */
    private boolean isAllItemsDone(String itemsJson, String progressJson) {
        if (itemsJson == null || itemsJson.isBlank()) return true;
        try {
            List<Map<String, Object>> items = OBJECT_MAPPER.readValue(itemsJson, new TypeReference<List<Map<String, Object>>>() {});
            if (items == null || items.isEmpty()) return true;
            List<Map<String, Object>> progressItems = new ArrayList<>();
            if (progressJson != null && !progressJson.isBlank()) {
                Map<String, Object> progress = OBJECT_MAPPER.readValue(progressJson, new TypeReference<Map<String, Object>>() {});
                if (progress != null && progress.get("items") != null) {
                    progressItems = OBJECT_MAPPER.convertValue(progress.get("items"), new TypeReference<List<Map<String, Object>>>() {});
                }
            }
            for (Map<String, Object> item : items) {
                String type = item.get("type") != null ? item.get("type").toString() : null;
                Object idObj = item.get("id");
                if (type == null || idObj == null) continue;
                long id = idObj instanceof Number ? ((Number) idObj).longValue() : Long.parseLong(idObj.toString());
                boolean done = false;
                for (Map<String, Object> p : progressItems) {
                    String pt = p.get("type") != null ? p.get("type").toString() : null;
                    Object pid = p.get("id");
                    Object pdone = p.get("done");
                    if (pt != null && pt.equals(type) && pid != null) {
                        long pidLong = pid instanceof Number ? ((Number) pid).longValue() : Long.parseLong(pid.toString());
                        if (pidLong == id) {
                            done = pdone != null && (pdone instanceof Number ? ((Number) pdone).intValue() == 1 : "1".equals(String.valueOf(pdone)));
                            break;
                        }
                    }
                }
                if (!done) return false;
            }
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    private static class UserTaskRowMapper implements RowMapper<UserTask> {
        @Override
        public UserTask mapRow(ResultSet rs, int rowNum) throws SQLException {
            UserTask ut = new UserTask();
            ut.setId(rs.getLong("id"));
            ut.setUserId(rs.getLong("user_id"));
            ut.setTaskId(rs.getLong("task_id"));
            ut.setProgress(rs.getString("progress"));
            ut.setStatus(rs.getObject("status", Integer.class));
            Timestamp ca = rs.getTimestamp("completed_at");
            ut.setCompletedAt(ca != null ? ca.toLocalDateTime() : null);
            ut.setCreateTime(rs.getObject("create_time", LocalDateTime.class));
            ut.setUpdateTime(rs.getObject("update_time", LocalDateTime.class));
            return ut;
        }
    }
}
