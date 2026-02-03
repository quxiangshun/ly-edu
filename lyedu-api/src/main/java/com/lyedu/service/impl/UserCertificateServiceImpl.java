package com.lyedu.service.impl;

import com.lyedu.entity.Certificate;
import com.lyedu.entity.CertificateTemplate;
import com.lyedu.entity.UserCertificate;
import com.lyedu.service.CertificateService;
import com.lyedu.service.CertificateTemplateService;
import com.lyedu.service.UserCertificateService;
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
import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

/**
 * 用户证书记录服务实现（含考试合格自动颁发）
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class UserCertificateServiceImpl implements UserCertificateService {

    private static final String SELECT_COLS = "id, user_id, certificate_id, template_id, certificate_no, title, issued_at, create_time";

    private final JdbcTemplate jdbcTemplate;
    private final CertificateService certificateService;
    private final CertificateTemplateService certificateTemplateService;

    @Override
    public List<UserCertificate> listByUserId(Long userId) {
        if (userId == null) return List.of();
        String sql = "SELECT " + SELECT_COLS + " FROM ly_user_certificate WHERE user_id = ? ORDER BY issued_at DESC";
        return jdbcTemplate.query(sql, new UserCertificateRowMapper(), userId);
    }

    @Override
    public UserCertificate getById(Long id) {
        if (id == null) return null;
        String sql = "SELECT " + SELECT_COLS + " FROM ly_user_certificate WHERE id = ?";
        List<UserCertificate> list = jdbcTemplate.query(sql, new UserCertificateRowMapper(), id);
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    public boolean hasCertificate(Long certificateId, Long userId) {
        if (certificateId == null || userId == null) return false;
        String sql = "SELECT 1 FROM ly_user_certificate WHERE certificate_id = ? AND user_id = ? LIMIT 1";
        List<Integer> list = jdbcTemplate.query(sql, (rs, rowNum) -> 1, certificateId, userId);
        return !list.isEmpty();
    }

    @Override
    public UserCertificate issueIfEligible(String sourceType, Long sourceId, Long userId) {
        if (sourceType == null || sourceId == null || userId == null) return null;
        Certificate rule = certificateService.getBySource(sourceType, sourceId);
        if (rule == null) return null;
        if (hasCertificate(rule.getId(), userId)) return null;
        CertificateTemplate template = certificateTemplateService.getById(rule.getTemplateId());
        if (template == null || (template.getStatus() != null && template.getStatus() != 1)) return null;

        String certificateNo = "CERT-" + System.currentTimeMillis() + "-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        String title = rule.getName();
        LocalDateTime issuedAt = LocalDateTime.now();

        String sql = "INSERT INTO ly_user_certificate (user_id, certificate_id, template_id, certificate_no, title, issued_at) VALUES (?, ?, ?, ?, ?, ?)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(con -> {
            PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setLong(1, userId);
            ps.setLong(2, rule.getId());
            ps.setLong(3, rule.getTemplateId());
            ps.setString(4, certificateNo);
            ps.setString(5, title);
            ps.setTimestamp(6, Timestamp.valueOf(issuedAt));
            return ps;
        }, keyHolder);
        Number key = keyHolder.getKey();
        if (key == null) return null;
        UserCertificate uc = new UserCertificate();
        uc.setId(key.longValue());
        uc.setUserId(userId);
        uc.setCertificateId(rule.getId());
        uc.setTemplateId(rule.getTemplateId());
        uc.setCertificateNo(certificateNo);
        uc.setTitle(title);
        uc.setIssuedAt(issuedAt);
        uc.setCreateTime(issuedAt);
        return uc;
    }

    private static class UserCertificateRowMapper implements RowMapper<UserCertificate> {
        @Override
        public UserCertificate mapRow(ResultSet rs, int rowNum) throws SQLException {
            UserCertificate uc = new UserCertificate();
            uc.setId(rs.getLong("id"));
            uc.setUserId(rs.getLong("user_id"));
            uc.setCertificateId(rs.getLong("certificate_id"));
            uc.setTemplateId(rs.getLong("template_id"));
            uc.setCertificateNo(rs.getString("certificate_no"));
            uc.setTitle(rs.getString("title"));
            Timestamp ia = rs.getTimestamp("issued_at");
            uc.setIssuedAt(ia != null ? ia.toLocalDateTime() : null);
            uc.setCreateTime(rs.getObject("create_time", LocalDateTime.class));
            return uc;
        }
    }
}
