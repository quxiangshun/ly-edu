package com.lyedu.service.impl;

import com.lyedu.entity.Config;
import com.lyedu.service.ConfigService;
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
import java.time.LocalDateTime;
import java.util.List;

/**
 * 系统配置服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class ConfigServiceImpl implements ConfigService {

    private static final String SELECT_COLS = "id, config_key, config_value, category, remark, create_time, update_time";

    private final JdbcTemplate jdbcTemplate;

    @Override
    public String getByKey(String configKey) {
        if (configKey == null || configKey.isBlank()) return null;
        String sql = "SELECT config_value FROM ly_config WHERE config_key = ?";
        List<String> list = jdbcTemplate.query(sql, (rs, rowNum) -> rs.getString("config_value"), configKey);
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    public List<Config> listByCategory(String category) {
        String sql = "SELECT " + SELECT_COLS + " FROM ly_config WHERE 1=1" + (category != null && !category.isBlank() ? " AND category = ?" : "") + " ORDER BY category, config_key";
        if (category != null && !category.isBlank()) {
            return jdbcTemplate.query(sql, new ConfigRowMapper(), category);
        }
        return jdbcTemplate.query(sql, new ConfigRowMapper());
    }

    @Override
    public List<Config> listAll() {
        return listByCategory(null);
    }

    @Override
    public void set(String configKey, String configValue, String category, String remark) {
        if (configKey == null || configKey.isBlank()) return;
        Integer cnt = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM ly_config WHERE config_key = ?", Integer.class, configKey);
        if (cnt != null && cnt > 0) {
            jdbcTemplate.update("UPDATE ly_config SET config_value = ?, category = ?, remark = ? WHERE config_key = ?",
                    configValue, category != null ? category : "site", remark, configKey);
        } else {
            String sql = "INSERT INTO ly_config (config_key, config_value, category, remark) VALUES (?, ?, ?, ?)";
            jdbcTemplate.update(sql, configKey, configValue, category != null ? category : "site", remark);
        }
    }

    private static class ConfigRowMapper implements RowMapper<Config> {
        @Override
        public Config mapRow(ResultSet rs, int rowNum) throws SQLException {
            Config c = new Config();
            c.setId(rs.getLong("id"));
            c.setConfigKey(rs.getString("config_key"));
            c.setConfigValue(rs.getString("config_value"));
            c.setCategory(rs.getString("category"));
            c.setRemark(rs.getString("remark"));
            c.setCreateTime(rs.getObject("create_time", LocalDateTime.class));
            c.setUpdateTime(rs.getObject("update_time", LocalDateTime.class));
            return c;
        }
    }
}
