package com.lyedu.service.impl;

import com.lyedu.common.PageResult;
import com.lyedu.entity.Knowledge;
import com.lyedu.entity.User;
import com.lyedu.service.DepartmentService;
import com.lyedu.service.KnowledgeDepartmentService;
import com.lyedu.service.KnowledgeService;
import com.lyedu.service.UserService;
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
 * 知识库服务实现（可见性规则同课程：公开或私有且部门在 ly_knowledge_department）
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class KnowledgeServiceImpl implements KnowledgeService {

    private static final String SELECT_COLS = "id, title, category, file_name, file_url, file_size, file_type, sort, visibility, create_time, update_time, deleted";

    private final JdbcTemplate jdbcTemplate;
    private final DepartmentService departmentService;
    private final UserService userService;
    private final KnowledgeDepartmentService knowledgeDepartmentService;

    @Override
    public PageResult<Knowledge> page(Integer page, Integer size, String keyword, String category, Long userId) {
        int offset = (page - 1) * size;
        StringBuilder where = new StringBuilder("WHERE deleted = 0");
        List<Object> params = new java.util.ArrayList<>();
        appendVisibilityCondition(where, params, userId);
        if (keyword != null && !keyword.trim().isEmpty()) {
            where.append(" AND (title LIKE ? OR category LIKE ?)");
            String like = "%" + keyword + "%";
            params.add(like);
            params.add(like);
        }
        if (category != null && !category.trim().isEmpty()) {
            where.append(" AND category = ?");
            params.add(category.trim());
        }
        String countSql = "SELECT COUNT(*) FROM ly_knowledge " + where;
        Integer totalInt = jdbcTemplate.queryForObject(countSql, params.toArray(), Integer.class);
        Long total = totalInt != null ? totalInt.longValue() : 0L;
        String querySql = "SELECT " + SELECT_COLS + " FROM ly_knowledge " + where + " ORDER BY sort ASC, id DESC LIMIT ? OFFSET ?";
        List<Object> queryParams = new java.util.ArrayList<>(params);
        queryParams.add(size);
        queryParams.add(offset);
        List<Knowledge> list = jdbcTemplate.query(querySql, queryParams.toArray(), new KnowledgeRowMapper());
        for (Knowledge k : list) {
            fillDepartmentIds(k);
        }
        return new PageResult<>(list, total, (long) page, (long) size);
    }

    @Override
    public Knowledge getById(Long id, Long userId) {
        Knowledge k = getByIdIgnoreVisibility(id);
        if (k == null) return null;
        if (!canUserSeeKnowledge(k, userId)) return null;
        return k;
    }

    @Override
    public Knowledge getByIdIgnoreVisibility(Long id) {
        String sql = "SELECT " + SELECT_COLS + " FROM ly_knowledge WHERE id = ? AND deleted = 0";
        List<Knowledge> list = jdbcTemplate.query(sql, new Object[]{id}, new KnowledgeRowMapper());
        Knowledge k = list.isEmpty() ? null : list.get(0);
        if (k != null) fillDepartmentIds(k);
        return k;
    }

    @Override
    public long save(Knowledge knowledge) {
        String sql = "INSERT INTO ly_knowledge (title, category, file_name, file_url, file_size, file_type, sort, visibility) VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(con -> {
            PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            int i = 0;
            ps.setString(++i, knowledge.getTitle());
            ps.setString(++i, knowledge.getCategory());
            ps.setString(++i, knowledge.getFileName());
            ps.setString(++i, knowledge.getFileUrl());
            ps.setObject(++i, knowledge.getFileSize());
            ps.setString(++i, knowledge.getFileType());
            ps.setInt(++i, knowledge.getSort() != null ? knowledge.getSort() : 0);
            ps.setInt(++i, knowledge.getVisibility() != null ? knowledge.getVisibility() : 1);
            return ps;
        }, keyHolder);
        Number key = keyHolder.getKey();
        long id = key != null ? key.longValue() : 0L;
        if (id > 0 && knowledge.getDepartmentIds() != null && !knowledge.getDepartmentIds().isEmpty()) {
            knowledgeDepartmentService.setKnowledgeDepartments(id, knowledge.getDepartmentIds());
        }
        return id;
    }

    @Override
    public void update(Knowledge knowledge) {
        if (knowledge.getId() == null) return;
        String sql = "UPDATE ly_knowledge SET title = ?, category = ?, file_name = ?, file_url = ?, file_size = ?, file_type = ?, sort = ?, visibility = ? WHERE id = ? AND deleted = 0";
        jdbcTemplate.update(sql,
                knowledge.getTitle(),
                knowledge.getCategory(),
                knowledge.getFileName(),
                knowledge.getFileUrl(),
                knowledge.getFileSize(),
                knowledge.getFileType(),
                knowledge.getSort() != null ? knowledge.getSort() : 0,
                knowledge.getVisibility() != null ? knowledge.getVisibility() : 1,
                knowledge.getId());
        knowledgeDepartmentService.setKnowledgeDepartments(knowledge.getId(), knowledge.getDepartmentIds());
    }

    @Override
    public void delete(Long id) {
        if (id == null) return;
        jdbcTemplate.update("UPDATE ly_knowledge SET deleted = 1 WHERE id = ?", id);
        knowledgeDepartmentService.setKnowledgeDepartments(id, null);
    }

    private void fillDepartmentIds(Knowledge k) {
        if (k != null && k.getId() != null) {
            k.setDepartmentIds(knowledgeDepartmentService.listDepartmentIdsByKnowledgeId(k.getId()));
        }
    }

    private boolean canUserSeeKnowledge(Knowledge k, Long userId) {
        if (k.getVisibility() != null && k.getVisibility() == 1) return true;
        if (userId == null) return false;
        User user = userService.getById(userId);
        if (user == null) return false;
        if ("admin".equals(user.getRole())) return true;
        if (user.getDepartmentId() == null) return false;
        List<Long> allowedDeptIds = departmentService.getDepartmentIdAndDescendantIds(user.getDepartmentId());
        return knowledgeDepartmentService.knowledgeVisibleToDepartments(k.getId(), allowedDeptIds);
    }

    private void appendVisibilityCondition(StringBuilder where, List<Object> params, Long userId) {
        if (userId == null) {
            where.append(" AND visibility = 1");
            return;
        }
        User user = userService.getById(userId);
        if (user == null) {
            where.append(" AND visibility = 1");
            return;
        }
        if ("admin".equals(user.getRole())) return;
        if (user.getDepartmentId() == null) {
            where.append(" AND visibility = 1");
            return;
        }
        List<Long> allowedDeptIds = departmentService.getDepartmentIdAndDescendantIds(user.getDepartmentId());
        if (allowedDeptIds.isEmpty()) {
            where.append(" AND visibility = 1");
            return;
        }
        where.append(" AND (visibility = 1 OR (visibility = 0 AND EXISTS (SELECT 1 FROM ly_knowledge_department kd WHERE kd.knowledge_id = ly_knowledge.id AND kd.department_id IN (");
        for (int i = 0; i < allowedDeptIds.size(); i++) {
            if (i > 0) where.append(", ");
            where.append("?");
            params.add(allowedDeptIds.get(i));
        }
        where.append("))))");
    }

    private static class KnowledgeRowMapper implements RowMapper<Knowledge> {
        @Override
        public Knowledge mapRow(ResultSet rs, int rowNum) throws SQLException {
            Knowledge k = new Knowledge();
            k.setId(rs.getLong("id"));
            k.setTitle(rs.getString("title"));
            k.setCategory(rs.getString("category"));
            k.setFileName(rs.getString("file_name"));
            k.setFileUrl(rs.getString("file_url"));
            long fileSize = rs.getLong("file_size");
            if (!rs.wasNull()) k.setFileSize(fileSize);
            k.setFileType(rs.getString("file_type"));
            k.setSort(rs.getInt("sort"));
            int vis = rs.getInt("visibility");
            if (!rs.wasNull()) k.setVisibility(vis);
            k.setCreateTime(rs.getObject("create_time", java.time.LocalDateTime.class));
            k.setUpdateTime(rs.getObject("update_time", java.time.LocalDateTime.class));
            k.setDeleted(rs.getObject("deleted", Integer.class));
            return k;
        }
    }
}
