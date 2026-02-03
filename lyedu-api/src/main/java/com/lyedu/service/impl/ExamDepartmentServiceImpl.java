package com.lyedu.service.impl;

import com.lyedu.service.ExamDepartmentService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * 考试-部门多对多关联服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class ExamDepartmentServiceImpl implements ExamDepartmentService {

    private static final String TABLE = "ly_exam_department";

    private final JdbcTemplate jdbcTemplate;

    @Override
    public List<Long> listDepartmentIdsByExamId(Long examId) {
        if (examId == null) return Collections.emptyList();
        String sql = "SELECT department_id FROM " + TABLE + " WHERE exam_id = ?";
        List<Long> list = jdbcTemplate.query(sql, (rs, rowNum) -> rs.getLong("department_id"), examId);
        return list != null ? list : Collections.emptyList();
    }

    @Override
    public void setExamDepartments(Long examId, List<Long> departmentIds) {
        if (examId == null) return;
        jdbcTemplate.update("DELETE FROM " + TABLE + " WHERE exam_id = ?", examId);
        if (departmentIds != null && !departmentIds.isEmpty()) {
            for (Long deptId : departmentIds) {
                if (deptId != null) {
                    jdbcTemplate.update("INSERT INTO " + TABLE + " (exam_id, department_id) VALUES (?, ?)", examId, deptId);
                }
            }
        }
    }

    @Override
    public boolean examVisibleToDepartments(Long examId, List<Long> allowedDeptIds) {
        if (examId == null || allowedDeptIds == null || allowedDeptIds.isEmpty()) return false;
        String sql = "SELECT 1 FROM " + TABLE + " WHERE exam_id = ? AND department_id IN (" + placeholders(allowedDeptIds.size()) + ") LIMIT 1";
        List<Object> args = new ArrayList<>();
        args.add(examId);
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
