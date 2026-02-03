package com.lyedu.service.impl;

import com.lyedu.entity.PointLog;
import com.lyedu.entity.PointRule;
import com.lyedu.service.PointRuleService;
import com.lyedu.service.PointService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 积分服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class PointServiceImpl implements PointService {

    private final JdbcTemplate jdbcTemplate;
    private final PointRuleService pointRuleService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public int addPoints(Long userId, String ruleKey, String refType, Long refId) {
        if (userId == null || ruleKey == null || ruleKey.isBlank()) return 0;
        PointRule rule = pointRuleService.getByKey(ruleKey);
        if (rule == null || rule.getEnabled() == null || rule.getEnabled() != 1 || rule.getPoints() == null || rule.getPoints() <= 0) {
            return 0;
        }
        if (refType != null && refId != null) {
            String existSql = "SELECT 1 FROM ly_point_log WHERE user_id = ? AND ref_type = ? AND ref_id = ? LIMIT 1";
            Integer exist = jdbcTemplate.queryForObject(existSql, Integer.class, userId, refType, refId);
            if (exist != null && exist > 0) return 0;
        }
        int points = rule.getPoints();
        String remark = rule.getRuleName() != null ? rule.getRuleName() : ruleKey;
        jdbcTemplate.update(
                "INSERT INTO ly_point_log (user_id, points, rule_key, ref_type, ref_id, remark) VALUES (?, ?, ?, ?, ?, ?)",
                userId, points, ruleKey, refType, refId, remark);
        jdbcTemplate.update("UPDATE ly_user SET total_points = COALESCE(total_points, 0) + ? WHERE id = ?", points, userId);
        return points;
    }

    @Override
    public int getTotalPoints(Long userId) {
        if (userId == null) return 0;
        Integer v = jdbcTemplate.queryForObject("SELECT COALESCE(total_points, 0) FROM ly_user WHERE id = ?", Integer.class, userId);
        return v != null ? v : 0;
    }

    @Override
    public List<PointLog> listMyLog(Long userId, int page, int size) {
        if (userId == null) return List.of();
        int offset = (page - 1) * size;
        String sql = "SELECT id, user_id, points, rule_key, ref_type, ref_id, remark, create_time FROM ly_point_log WHERE user_id = ? ORDER BY create_time DESC LIMIT ? OFFSET ?";
        return jdbcTemplate.query(sql, new PointLogRowMapper(), userId, size, offset);
    }

    @Override
    public List<Map<String, Object>> listRanking(int limit, Long departmentId) {
        StringBuilder sql = new StringBuilder(
                "SELECT u.id AS userId, u.real_name AS realName, u.username, COALESCE(u.total_points, 0) AS totalPoints FROM ly_user u WHERE u.deleted = 0 ");
        if (departmentId != null) {
            sql.append(" AND u.department_id = ? ");
        }
        sql.append(" ORDER BY totalPoints DESC, u.id ASC LIMIT ?");
        if (departmentId != null) {
            return jdbcTemplate.query(sql.toString(), (rs, rowNum) -> {
                Map<String, Object> m = new HashMap<>();
                m.put("userId", rs.getLong("userId"));
                m.put("realName", rs.getString("realName"));
                m.put("username", rs.getString("username"));
                m.put("totalPoints", rs.getObject("totalPoints", Integer.class));
                m.put("rank", rowNum + 1);
                return m;
            }, departmentId, limit);
        }
        return jdbcTemplate.query(sql.toString(), (rs, rowNum) -> {
            Map<String, Object> m = new HashMap<>();
            m.put("userId", rs.getLong("userId"));
            m.put("realName", rs.getString("realName"));
            m.put("username", rs.getString("username"));
            m.put("totalPoints", rs.getObject("totalPoints", Integer.class));
            m.put("rank", rowNum + 1);
            return m;
        }, limit);
    }

    private static class PointLogRowMapper implements RowMapper<PointLog> {
        @Override
        public PointLog mapRow(ResultSet rs, int rowNum) throws SQLException {
            PointLog log = new PointLog();
            log.setId(rs.getLong("id"));
            log.setUserId(rs.getLong("user_id"));
            log.setPoints(rs.getInt("points"));
            log.setRuleKey(rs.getString("rule_key"));
            log.setRefType(rs.getString("ref_type"));
            log.setRefId(rs.getObject("ref_id", Long.class));
            log.setRemark(rs.getString("remark"));
            Timestamp t = rs.getTimestamp("create_time");
            log.setCreateTime(t != null ? t.toLocalDateTime() : null);
            return log;
        }
    }
}
