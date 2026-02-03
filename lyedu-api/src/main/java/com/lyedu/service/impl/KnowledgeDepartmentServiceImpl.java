package com.lyedu.service.impl;

import com.lyedu.service.KnowledgeDepartmentService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * 知识库-部门多对多关联服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class KnowledgeDepartmentServiceImpl implements KnowledgeDepartmentService {

    private static final String TABLE = "ly_knowledge_department";

    private final JdbcTemplate jdbcTemplate;

    @Override
    public List<Long> listDepartmentIdsByKnowledgeId(Long knowledgeId) {
        if (knowledgeId == null) return Collections.emptyList();
        String sql = "SELECT department_id FROM " + TABLE + " WHERE knowledge_id = ?";
        List<Long> list = jdbcTemplate.query(sql, (rs, rowNum) -> rs.getLong("department_id"), knowledgeId);
        return list != null ? list : Collections.emptyList();
    }

    @Override
    public void setKnowledgeDepartments(Long knowledgeId, List<Long> departmentIds) {
        if (knowledgeId == null) return;
        jdbcTemplate.update("DELETE FROM " + TABLE + " WHERE knowledge_id = ?", knowledgeId);
        if (departmentIds != null && !departmentIds.isEmpty()) {
            for (Long deptId : departmentIds) {
                if (deptId != null) {
                    jdbcTemplate.update("INSERT INTO " + TABLE + " (knowledge_id, department_id) VALUES (?, ?)", knowledgeId, deptId);
                }
            }
        }
    }

    @Override
    public boolean knowledgeVisibleToDepartments(Long knowledgeId, List<Long> allowedDeptIds) {
        if (knowledgeId == null || allowedDeptIds == null || allowedDeptIds.isEmpty()) return false;
        String sql = "SELECT 1 FROM " + TABLE + " WHERE knowledge_id = ? AND department_id IN (" + placeholders(allowedDeptIds.size()) + ") LIMIT 1";
        List<Object> args = new ArrayList<>();
        args.add(knowledgeId);
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
