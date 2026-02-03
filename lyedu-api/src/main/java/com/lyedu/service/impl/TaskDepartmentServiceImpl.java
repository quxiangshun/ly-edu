package com.lyedu.service.impl;

import com.lyedu.service.TaskDepartmentService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * 任务-部门多对多关联服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class TaskDepartmentServiceImpl implements TaskDepartmentService {

    private static final String TABLE = "ly_task_department";

    private final JdbcTemplate jdbcTemplate;

    @Override
    public List<Long> listDepartmentIdsByTaskId(Long taskId) {
        if (taskId == null) return Collections.emptyList();
        String sql = "SELECT department_id FROM " + TABLE + " WHERE task_id = ?";
        List<Long> list = jdbcTemplate.query(sql, (rs, rowNum) -> rs.getLong("department_id"), taskId);
        return list != null ? list : Collections.emptyList();
    }

    @Override
    public void setTaskDepartments(Long taskId, List<Long> departmentIds) {
        if (taskId == null) return;
        jdbcTemplate.update("DELETE FROM " + TABLE + " WHERE task_id = ?", taskId);
        if (departmentIds != null && !departmentIds.isEmpty()) {
            for (Long deptId : departmentIds) {
                if (deptId != null) {
                    jdbcTemplate.update("INSERT INTO " + TABLE + " (task_id, department_id) VALUES (?, ?)", taskId, deptId);
                }
            }
        }
    }

    @Override
    public boolean taskVisibleToDepartments(Long taskId, List<Long> allowedDeptIds) {
        if (taskId == null || allowedDeptIds == null || allowedDeptIds.isEmpty()) return false;
        String sql = "SELECT 1 FROM " + TABLE + " WHERE task_id = ? AND department_id IN (" + placeholders(allowedDeptIds.size()) + ") LIMIT 1";
        List<Object> args = new ArrayList<>();
        args.add(taskId);
        args.addAll(allowedDeptIds);
        List<Integer> one = jdbcTemplate.query(sql, args.toArray(), (rs, rowNum) -> 1);
        return one != null && !one.isEmpty();
    }

    private static String placeholders(int n) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(", ");
            sb.append("?");
        }
        return sb.toString();
    }
}
