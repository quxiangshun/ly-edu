package com.lyedu.service.impl;

import com.lyedu.service.CourseDepartmentService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * 课程-部门多对多关联服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class CourseDepartmentServiceImpl implements CourseDepartmentService {

    private static final String TABLE = "ly_course_department";

    private final JdbcTemplate jdbcTemplate;

    @Override
    public List<Long> listDepartmentIdsByCourseId(Long courseId) {
        if (courseId == null) return Collections.emptyList();
        String sql = "SELECT department_id FROM " + TABLE + " WHERE course_id = ?";
        List<Long> list = jdbcTemplate.query(sql, (rs, rowNum) -> rs.getLong("department_id"), courseId);
        return list != null ? list : Collections.emptyList();
    }

    @Override
    public void setCourseDepartments(Long courseId, List<Long> departmentIds) {
        if (courseId == null) return;
        jdbcTemplate.update("DELETE FROM " + TABLE + " WHERE course_id = ?", courseId);
        if (departmentIds != null && !departmentIds.isEmpty()) {
            for (Long deptId : departmentIds) {
                if (deptId != null) {
                    jdbcTemplate.update("INSERT INTO " + TABLE + " (course_id, department_id) VALUES (?, ?)", courseId, deptId);
                }
            }
        }
    }

    @Override
    public List<Long> listCourseIdsByDepartmentId(Long departmentId) {
        if (departmentId == null) return Collections.emptyList();
        String sql = "SELECT course_id FROM " + TABLE + " WHERE department_id = ?";
        List<Long> list = jdbcTemplate.query(sql, (rs, rowNum) -> rs.getLong("course_id"), departmentId);
        return list != null ? list : Collections.emptyList();
    }

    @Override
    public void addCoursesToDepartment(Long departmentId, List<Long> courseIds) {
        if (departmentId == null || courseIds == null || courseIds.isEmpty()) return;
        for (Long courseId : courseIds) {
            if (courseId != null) {
                jdbcTemplate.update("INSERT IGNORE INTO " + TABLE + " (course_id, department_id) VALUES (?, ?)", courseId, departmentId);
            }
        }
    }

    @Override
    public void removeCourseFromDepartment(Long departmentId, Long courseId) {
        if (departmentId == null || courseId == null) return;
        jdbcTemplate.update("DELETE FROM " + TABLE + " WHERE department_id = ? AND course_id = ?", departmentId, courseId);
    }

    @Override
    public boolean courseVisibleToDepartments(Long courseId, List<Long> allowedDeptIds) {
        if (courseId == null || allowedDeptIds == null || allowedDeptIds.isEmpty()) return false;
        String sql = "SELECT 1 FROM " + TABLE + " WHERE course_id = ? AND department_id IN (" + placeholders(allowedDeptIds.size()) + ") LIMIT 1";
        List<Object> args = new ArrayList<>();
        args.add(courseId);
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
