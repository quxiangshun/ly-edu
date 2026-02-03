package com.lyedu.service.impl;

import com.lyedu.common.PageResult;
import com.lyedu.entity.Question;
import com.lyedu.service.QuestionService;
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
 * 试题服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class QuestionServiceImpl implements QuestionService {

    private static final String SELECT_COLS = "id, type, title, options, answer, score, analysis, sort, create_time, update_time, deleted";

    private final JdbcTemplate jdbcTemplate;

    @Override
    public PageResult<Question> page(Integer page, Integer size, String keyword, String type) {
        int offset = (page - 1) * size;
        StringBuilder where = new StringBuilder("WHERE deleted = 0");
        List<Object> params = new java.util.ArrayList<>();
        if (keyword != null && !keyword.trim().isEmpty()) {
            where.append(" AND title LIKE ?");
            params.add("%" + keyword.trim() + "%");
        }
        if (type != null && !type.trim().isEmpty()) {
            where.append(" AND type = ?");
            params.add(type.trim());
        }
        String countSql = "SELECT COUNT(*) FROM ly_question " + where;
        Integer totalInt = jdbcTemplate.queryForObject(countSql, params.toArray(), Integer.class);
        Long total = totalInt != null ? totalInt.longValue() : 0L;
        String querySql = "SELECT " + SELECT_COLS + " FROM ly_question " + where + " ORDER BY sort ASC, id DESC LIMIT ? OFFSET ?";
        List<Object> queryParams = new java.util.ArrayList<>(params);
        queryParams.add(size);
        queryParams.add(offset);
        List<Question> list = jdbcTemplate.query(querySql, queryParams.toArray(), new QuestionRowMapper());
        return new PageResult<>(list, total, (long) page, (long) size);
    }

    @Override
    public Question getById(Long id) {
        String sql = "SELECT " + SELECT_COLS + " FROM ly_question WHERE id = ? AND deleted = 0";
        List<Question> list = jdbcTemplate.query(sql, new Object[]{id}, new QuestionRowMapper());
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    public long save(Question question) {
        String sql = "INSERT INTO ly_question (type, title, options, answer, score, analysis, sort) VALUES (?, ?, ?, ?, ?, ?, ?)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(con -> {
            PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            int i = 0;
            ps.setString(++i, question.getType());
            ps.setString(++i, question.getTitle());
            ps.setString(++i, question.getOptions());
            ps.setString(++i, question.getAnswer());
            ps.setObject(++i, question.getScore() != null ? question.getScore() : 10);
            ps.setString(++i, question.getAnalysis());
            ps.setObject(++i, question.getSort() != null ? question.getSort() : 0);
            return ps;
        }, keyHolder);
        Number key = keyHolder.getKey();
        return key != null ? key.longValue() : 0L;
    }

    @Override
    public void update(Question question) {
        if (question.getId() == null) return;
        String sql = "UPDATE ly_question SET type = ?, title = ?, options = ?, answer = ?, score = ?, analysis = ?, sort = ? WHERE id = ? AND deleted = 0";
        jdbcTemplate.update(sql,
                question.getType(),
                question.getTitle(),
                question.getOptions(),
                question.getAnswer(),
                question.getScore() != null ? question.getScore() : 10,
                question.getAnalysis(),
                question.getSort() != null ? question.getSort() : 0,
                question.getId());
    }

    @Override
    public void delete(Long id) {
        if (id == null) return;
        jdbcTemplate.update("UPDATE ly_question SET deleted = 1 WHERE id = ?", id);
    }

    private static class QuestionRowMapper implements RowMapper<Question> {
        @Override
        public Question mapRow(ResultSet rs, int rowNum) throws SQLException {
            Question q = new Question();
            q.setId(rs.getLong("id"));
            q.setType(rs.getString("type"));
            q.setTitle(rs.getString("title"));
            q.setOptions(rs.getString("options"));
            q.setAnswer(rs.getString("answer"));
            q.setScore(rs.getObject("score", Integer.class));
            q.setAnalysis(rs.getString("analysis"));
            q.setSort(rs.getObject("sort", Integer.class));
            q.setCreateTime(rs.getObject("create_time", java.time.LocalDateTime.class));
            q.setUpdateTime(rs.getObject("update_time", java.time.LocalDateTime.class));
            q.setDeleted(rs.getObject("deleted", Integer.class));
            return q;
        }
    }
}
