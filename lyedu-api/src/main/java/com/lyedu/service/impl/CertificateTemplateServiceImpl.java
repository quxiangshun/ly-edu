package com.lyedu.service.impl;

import com.lyedu.entity.CertificateTemplate;
import com.lyedu.service.CertificateTemplateService;
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
import java.util.List;

/**
 * 证书模板服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class CertificateTemplateServiceImpl implements CertificateTemplateService {

    private static final String SELECT_COLS = "id, name, description, config, sort, status, create_time, update_time, deleted";

    private final JdbcTemplate jdbcTemplate;

    @Override
    public List<CertificateTemplate> listAll() {
        String sql = "SELECT " + SELECT_COLS + " FROM ly_certificate_template WHERE deleted = 0 ORDER BY sort ASC, id DESC";
        return jdbcTemplate.query(sql, new CertificateTemplateRowMapper());
    }

    @Override
    public CertificateTemplate getById(Long id) {
        if (id == null) return null;
        String sql = "SELECT " + SELECT_COLS + " FROM ly_certificate_template WHERE id = ? AND deleted = 0";
        List<CertificateTemplate> list = jdbcTemplate.query(sql, new CertificateTemplateRowMapper(), id);
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    public long save(CertificateTemplate entity) {
        String sql = "INSERT INTO ly_certificate_template (name, description, config, sort, status) VALUES (?, ?, ?, ?, ?)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(con -> {
            PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setString(1, entity.getName());
            ps.setString(2, entity.getDescription());
            ps.setString(3, entity.getConfig());
            ps.setInt(4, entity.getSort() != null ? entity.getSort() : 0);
            ps.setInt(5, entity.getStatus() != null ? entity.getStatus() : 1);
            return ps;
        }, keyHolder);
        Number key = keyHolder.getKey();
        return key != null ? key.longValue() : 0L;
    }

    @Override
    public void update(CertificateTemplate entity) {
        if (entity.getId() == null) return;
        String sql = "UPDATE ly_certificate_template SET name = ?, description = ?, config = ?, sort = ?, status = ? WHERE id = ? AND deleted = 0";
        jdbcTemplate.update(sql,
                entity.getName(),
                entity.getDescription(),
                entity.getConfig(),
                entity.getSort() != null ? entity.getSort() : 0,
                entity.getStatus() != null ? entity.getStatus() : 1,
                entity.getId());
    }

    @Override
    public void delete(Long id) {
        if (id == null) return;
        jdbcTemplate.update("UPDATE ly_certificate_template SET deleted = 1 WHERE id = ?", id);
    }

    private static class CertificateTemplateRowMapper implements RowMapper<CertificateTemplate> {
        @Override
        public CertificateTemplate mapRow(ResultSet rs, int rowNum) throws SQLException {
            CertificateTemplate t = new CertificateTemplate();
            t.setId(rs.getLong("id"));
            t.setName(rs.getString("name"));
            t.setDescription(rs.getString("description"));
            t.setConfig(rs.getString("config"));
            t.setSort(rs.getObject("sort", Integer.class));
            t.setStatus(rs.getObject("status", Integer.class));
            t.setCreateTime(rs.getObject("create_time", java.time.LocalDateTime.class));
            t.setUpdateTime(rs.getObject("update_time", java.time.LocalDateTime.class));
            t.setDeleted(rs.getObject("deleted", Integer.class));
            return t;
        }
    }
}
