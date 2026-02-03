package com.lyedu.service.impl;

import com.lyedu.entity.PointRule;
import com.lyedu.service.PointRuleService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Service;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 积分规则服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class PointRuleServiceImpl implements PointRuleService {

    private static final String SELECT_COLS = "id, rule_key, rule_name, points, enabled, remark, create_time, update_time";

    private final JdbcTemplate jdbcTemplate;

    @Override
    public List<PointRule> listAll() {
        String sql = "SELECT " + SELECT_COLS + " FROM ly_point_rule ORDER BY id";
        return jdbcTemplate.query(sql, new PointRuleRowMapper());
    }

    @Override
    public PointRule getByKey(String ruleKey) {
        if (ruleKey == null || ruleKey.isBlank()) return null;
        String sql = "SELECT " + SELECT_COLS + " FROM ly_point_rule WHERE rule_key = ?";
        List<PointRule> list = jdbcTemplate.query(sql, new PointRuleRowMapper(), ruleKey);
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    public void update(String ruleKey, String ruleName, Integer points, Integer enabled, String remark) {
        if (ruleKey == null || ruleKey.isBlank()) return;
        jdbcTemplate.update(
                "UPDATE ly_point_rule SET rule_name = ?, points = ?, enabled = ?, remark = ? WHERE rule_key = ?",
                ruleName, points, enabled, remark, ruleKey);
    }

    private static class PointRuleRowMapper implements RowMapper<PointRule> {
        @Override
        public PointRule mapRow(ResultSet rs, int rowNum) throws SQLException {
            PointRule r = new PointRule();
            r.setId(rs.getLong("id"));
            r.setRuleKey(rs.getString("rule_key"));
            r.setRuleName(rs.getString("rule_name"));
            r.setPoints(rs.getObject("points", Integer.class));
            r.setEnabled(rs.getObject("enabled", Integer.class));
            r.setRemark(rs.getString("remark"));
            r.setCreateTime(rs.getObject("create_time", LocalDateTime.class));
            r.setUpdateTime(rs.getObject("update_time", LocalDateTime.class));
            return r;
        }
    }
}
