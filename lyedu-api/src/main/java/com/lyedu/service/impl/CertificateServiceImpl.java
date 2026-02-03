package com.lyedu.service.impl;

import com.lyedu.entity.Certificate;
import com.lyedu.service.CertificateService;
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

/** 证书颁发规则服务实现 */
@Service
@RequiredArgsConstructor
public class CertificateServiceImpl implements CertificateService {

    private static final String SELECT_COLS = "id, template_id, name, source_type, source_id, sort, status, create_time, update_time, deleted";

    private final JdbcTemplate jdbcTemplate;

    @Override
    public List<Certificate> listAll() {
        String sql = "SELECT " + SELECT_COLS + " FROM ly_certificate WHERE deleted = 0 ORDER BY sort ASC, id DESC";
        return jdbcTemplate.query(sql, new CertificateRowMapper());
    }

    @Override
    public Certificate getById(Long id) {
        if (id == null) return null;
        String sql = "SELECT " + SELECT_COLS + " FROM ly_certificate WHERE id = ? AND deleted = 0";
        List<Certificate> list = jdbcTemplate.query(sql, new CertificateRowMapper(), id);
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    public Certificate getBySource(String sourceType, Long sourceId) {
        if (sourceType == null || sourceId == null) return null;
        String sql = "SELECT " + SELECT_COLS + " FROM ly_certificate WHERE source_type = ? AND source_id = ? AND status = 1 AND deleted = 0 LIMIT 1";
        List<Certificate> list = jdbcTemplate.query(sql, new CertificateRowMapper(), sourceType, sourceId);
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    public long save(Certificate entity) {
        String sql = "INSERT INTO ly_certificate (template_id, name, source_type, source_id, sort, status) VALUES (?, ?, ?, ?, ?, ?)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(con -> {
            PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setLong(1, entity.getTemplateId());
            ps.setString(2, entity.getName());
            ps.setString(3, entity.getSourceType());
            ps.setLong(4, entity.getSourceId());
            ps.setInt(5, entity.getSort() != null ? entity.getSort() : 0);
            ps.setInt(6, entity.getStatus() != null ? entity.getStatus() : 1);
            return ps;
        }, keyHolder);
        Number key = keyHolder.getKey();
        return key != null ? key.longValue() : 0L;
    }

    @Override
    public void update(Certificate entity) {
        if (entity.getId() == null) return;
        String sql = "UPDATE ly_certificate SET template_id = ?, name = ?, source_type = ?, source_id = ?, sort = ?, status = ? WHERE id = ? AND deleted = 0";
        jdbcTemplate.update(sql,
                entity.getTemplateId(),
                entity.getName(),
                entity.getSourceType(),
                entity.getSourceId(),
                entity.getSort() != null ? entity.getSort() : 0,
                entity.getStatus() != null ? entity.getStatus() : 1,
                entity.getId());
    }

    @Override
    public void delete(Long id) {
        if (id == null) return;
        jdbcTemplate.update("UPDATE ly_certificate SET deleted = 1 WHERE id = ?", id);
    }

    private static class CertificateRowMapper implements RowMapper<Certificate> {
        @Override
        public Certificate mapRow(ResultSet rs, int rowNum) throws SQLException {
            Certificate c = new Certificate();
            c.setId(rs.getLong("id"));
            c.setTemplateId(rs.getLong("template_id"));
            c.setName(rs.getString("name"));
            c.setSourceType(rs.getString("source_type"));
            c.setSourceId(rs.getLong("source_id"));
            c.setSort(rs.getObject("sort", Integer.class));
            c.setStatus(rs.getObject("status", Integer.class));
            c.setCreateTime(rs.getObject("create_time", java.time.LocalDateTime.class));
            c.setUpdateTime(rs.getObject("update_time", java.time.LocalDateTime.class));
            c.setDeleted(rs.getObject("deleted", Integer.class));
            return c;
        }
    }
}
