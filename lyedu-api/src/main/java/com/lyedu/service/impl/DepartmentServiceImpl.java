package com.lyedu.service.impl;

import com.lyedu.entity.Department;
import com.lyedu.service.DepartmentService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Service;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 部门服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class DepartmentServiceImpl implements DepartmentService {

    private final JdbcTemplate jdbcTemplate;

    private static final String SELECT_ALL_SQL =
            "SELECT id, CONVERT(name USING utf8mb4) as name, parent_id, sort, status, create_time, update_time, deleted " +
            "FROM ly_department WHERE deleted = 0 ORDER BY sort ASC, id ASC";

    private static final String SELECT_BY_ID_SQL =
            "SELECT id, CONVERT(name USING utf8mb4) as name, parent_id, sort, status, create_time, update_time, deleted " +
            "FROM ly_department WHERE id = ? AND deleted = 0";

    private static final String INSERT_SQL =
            "INSERT INTO ly_department (name, parent_id, sort, status) VALUES (?, ?, ?, ?)";

    private static final String UPDATE_SQL =
            "UPDATE ly_department SET name = ?, parent_id = ?, sort = ?, status = ? WHERE id = ? AND deleted = 0";

    private static final String DELETE_SQL =
            "UPDATE ly_department SET deleted = 1 WHERE id = ?";

    @Override
    public List<Department> listTree() {
        List<Department> all = jdbcTemplate.query(SELECT_ALL_SQL, new DepartmentRowMapper());
        return buildTree(all, 0L);
    }

    @Override
    public Department getById(Long id) {
        List<Department> list = jdbcTemplate.query(SELECT_BY_ID_SQL, new Object[]{id}, new DepartmentRowMapper());
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    public void save(Department department) {
        jdbcTemplate.update(INSERT_SQL,
                department.getName(),
                department.getParentId() != null ? department.getParentId() : 0L,
                department.getSort() != null ? department.getSort() : 0,
                department.getStatus() != null ? department.getStatus() : 1);
    }

    @Override
    public void update(Department department) {
        jdbcTemplate.update(UPDATE_SQL,
                department.getName(),
                department.getParentId() != null ? department.getParentId() : 0L,
                department.getSort() != null ? department.getSort() : 0,
                department.getStatus() != null ? department.getStatus() : 1,
                department.getId());
    }

    @Override
    public void delete(Long id) {
        jdbcTemplate.update(DELETE_SQL, id);
    }

    @Override
    public List<Long> getDepartmentIdAndDescendantIds(Long departmentId) {
        if (departmentId == null) {
            return new ArrayList<>();
        }
        List<Department> all = jdbcTemplate.query(SELECT_ALL_SQL, new DepartmentRowMapper());
        List<Long> result = new ArrayList<>();
        result.add(departmentId);
        collectDescendantIds(all, departmentId, result);
        return result;
    }

    private void collectDescendantIds(List<Department> all, Long parentId, List<Long> result) {
        for (Department d : all) {
            if (parentId.equals(d.getParentId())) {
                result.add(d.getId());
                collectDescendantIds(all, d.getId(), result);
            }
        }
    }

    /**
     * 构建多级树形结构：递归挂载子部门到 children
     */
    private List<Department> buildTree(List<Department> all, Long parentId) {
        List<Department> list = all.stream()
                .filter(dept -> {
                    Long pid = dept.getParentId();
                    return (pid == null && parentId == 0L) || (pid != null && pid.equals(parentId));
                })
                .collect(Collectors.toList());
        for (Department dept : list) {
            List<Department> children = buildTree(all, dept.getId());
            dept.setChildren(children.isEmpty() ? null : children);
        }
        return list;
    }

    private static class DepartmentRowMapper implements RowMapper<Department> {
        @Override
        public Department mapRow(ResultSet rs, int rowNum) throws SQLException {
            Department dept = new Department();
            dept.setId(rs.getLong("id"));
            // 使用 getBytes 然后转换为 UTF-8 字符串，确保编码正确
            byte[] nameBytes = rs.getBytes("name");
            if (nameBytes != null) {
                dept.setName(new String(nameBytes, java.nio.charset.StandardCharsets.UTF_8));
            } else {
                dept.setName(rs.getString("name"));
            }
            dept.setParentId(rs.getLong("parent_id"));
            if (rs.wasNull()) {
                dept.setParentId(0L);
            }
            dept.setSort(rs.getInt("sort"));
            dept.setStatus(rs.getInt("status"));
            return dept;
        }
    }
}
