package com.lyedu.service.impl;

import com.lyedu.service.StatsService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class StatsServiceImpl implements StatsService {

    private final JdbcTemplate jdbcTemplate;

    @Override
    public Map<String, Long> overview() {
        Map<String, Long> map = new HashMap<>();
        Long userCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM ly_user WHERE deleted = 0", Long.class);
        Long courseCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM ly_course WHERE deleted = 0", Long.class);
        Long departmentCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM ly_department WHERE deleted = 0", Long.class);
        Long videoCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM ly_video WHERE deleted = 0", Long.class);
        map.put("userCount", userCount != null ? userCount : 0L);
        map.put("courseCount", courseCount != null ? courseCount : 0L);
        map.put("departmentCount", departmentCount != null ? departmentCount : 0L);
        map.put("videoCount", videoCount != null ? videoCount : 0L);
        return map;
    }

    @Override
    public List<Map<String, Object>> learningRank(int limit) {
        String sql = "SELECT u.id AS userId, u.real_name AS realName, u.username, d.name AS departmentName, " +
                "COUNT(uc.course_id) AS courseCount, COALESCE(SUM(uc.progress), 0) / GREATEST(COUNT(uc.course_id), 1) AS avgProgress " +
                "FROM ly_user u " +
                "LEFT JOIN ly_department d ON u.department_id = d.id AND d.deleted = 0 " +
                "LEFT JOIN ly_user_course uc ON u.id = uc.user_id " +
                "WHERE u.deleted = 0 " +
                "GROUP BY u.id, u.real_name, u.username, d.name " +
                "ORDER BY courseCount DESC, avgProgress DESC " +
                "LIMIT ?";
        return jdbcTemplate.queryForList(sql, Math.max(1, Math.min(limit, 100)));
    }

    @Override
    public Map<String, Long> resourceStats() {
        Map<String, Long> map = new HashMap<>();
        map.put("courseCount", nullableLong(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM ly_course WHERE deleted = 0", Long.class)));
        map.put("videoCount", nullableLong(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM ly_video WHERE deleted = 0", Long.class)));
        map.put("chapterCount", nullableLong(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM ly_course_chapter WHERE deleted = 0", Long.class)));
        map.put("attachmentCount", nullableLong(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM ly_course_attachment WHERE deleted = 0", Long.class)));
        return map;
    }

    @Override
    public List<Map<String, Object>> exportLearners() {
        String sql = "SELECT u.id, u.username, u.real_name AS realName, u.email, u.mobile, u.role, u.status, " +
                "d.name AS departmentName, u.create_time AS createTime " +
                "FROM ly_user u LEFT JOIN ly_department d ON u.department_id = d.id AND d.deleted = 0 " +
                "WHERE u.deleted = 0 ORDER BY u.id";
        return jdbcTemplate.queryForList(sql);
    }

    @Override
    public List<Map<String, Object>> exportLearning() {
        String sql = "SELECT uc.user_id AS userId, u.real_name AS realName, u.username, uc.course_id AS courseId, " +
                "c.title AS courseTitle, uc.progress, uc.status AS completeStatus, uc.create_time AS joinTime, uc.update_time AS updateTime " +
                "FROM ly_user_course uc " +
                "JOIN ly_user u ON uc.user_id = u.id AND u.deleted = 0 " +
                "JOIN ly_course c ON uc.course_id = c.id AND c.deleted = 0 " +
                "ORDER BY uc.user_id, uc.course_id";
        return jdbcTemplate.queryForList(sql);
    }

    @Override
    public List<Map<String, Object>> exportDepartmentLearning() {
        String sql = "SELECT d.id AS departmentId, d.name AS departmentName, " +
                "COUNT(DISTINCT u.id) AS userCount, " +
                "COUNT(DISTINCT CASE WHEN uc.progress >= 100 THEN uc.user_id ELSE NULL END) AS completedUserCount, " +
                "COUNT(uc.id) AS learningRecordCount " +
                "FROM ly_department d " +
                "LEFT JOIN ly_user u ON u.department_id = d.id AND u.deleted = 0 " +
                "LEFT JOIN ly_user_course uc ON uc.user_id = u.id " +
                "WHERE d.deleted = 0 " +
                "GROUP BY d.id, d.name ORDER BY d.sort, d.id";
        return jdbcTemplate.queryForList(sql);
    }

    private static long nullableLong(Long v) {
        return v != null ? v : 0L;
    }
}
