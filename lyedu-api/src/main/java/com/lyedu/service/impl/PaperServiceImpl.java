package com.lyedu.service.impl;

import com.lyedu.common.PageResult;
import com.lyedu.common.PaperQuestionDto;
import com.lyedu.entity.Paper;
import com.lyedu.entity.PaperQuestionItem;
import com.lyedu.entity.Question;
import com.lyedu.service.PaperService;
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
import java.util.ArrayList;
import java.util.List;

/**
 * 试卷服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class PaperServiceImpl implements PaperService {

    private static final String PAPER_COLS = "id, title, total_score, pass_score, duration_minutes, status, create_time, update_time, deleted";

    private final JdbcTemplate jdbcTemplate;
    private final QuestionService questionService;

    @Override
    public PageResult<Paper> page(Integer page, Integer size, String keyword) {
        int offset = (page - 1) * size;
        StringBuilder where = new StringBuilder("WHERE deleted = 0");
        List<Object> params = new ArrayList<>();
        if (keyword != null && !keyword.trim().isEmpty()) {
            where.append(" AND title LIKE ?");
            params.add("%" + keyword.trim() + "%");
        }
        String countSql = "SELECT COUNT(*) FROM ly_paper " + where;
        Integer totalInt = jdbcTemplate.queryForObject(countSql, params.toArray(), Integer.class);
        Long total = totalInt != null ? totalInt.longValue() : 0L;
        String querySql = "SELECT " + PAPER_COLS + " FROM ly_paper " + where + " ORDER BY id DESC LIMIT ? OFFSET ?";
        List<Object> queryParams = new ArrayList<>(params);
        queryParams.add(size);
        queryParams.add(offset);
        List<Paper> list = jdbcTemplate.query(querySql, queryParams.toArray(), new PaperRowMapper());
        return new PageResult<>(list, total, (long) page, (long) size);
    }

    @Override
    public Paper getById(Long id) {
        String sql = "SELECT " + PAPER_COLS + " FROM ly_paper WHERE id = ? AND deleted = 0";
        List<Paper> list = jdbcTemplate.query(sql, new Object[]{id}, new PaperRowMapper());
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    public List<PaperQuestionDto> listQuestionsByPaperId(Long paperId) {
        if (paperId == null) return List.of();
        String sql = "SELECT pq.question_id, pq.score, pq.sort FROM ly_paper_question pq WHERE pq.paper_id = ? ORDER BY pq.sort ASC, pq.question_id ASC";
        List<PaperQuestionDto> result = new ArrayList<>();
        jdbcTemplate.query(sql, (rs, rowNum) -> {
            PaperQuestionDto dto = new PaperQuestionDto();
            dto.setQuestionId(rs.getLong("question_id"));
            dto.setScore(rs.getObject("score", Integer.class));
            dto.setSort(rs.getObject("sort", Integer.class));
            Question q = questionService.getById(dto.getQuestionId());
            dto.setQuestion(q);
            result.add(dto);
            return null;
        }, paperId);
        return result;
    }

    @Override
    public long save(Paper paper) {
        String sql = "INSERT INTO ly_paper (title, total_score, pass_score, duration_minutes, status) VALUES (?, ?, ?, ?, ?)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(con -> {
            PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            int i = 0;
            ps.setString(++i, paper.getTitle());
            ps.setObject(++i, paper.getTotalScore() != null ? paper.getTotalScore() : 100);
            ps.setObject(++i, paper.getPassScore() != null ? paper.getPassScore() : 60);
            ps.setObject(++i, paper.getDurationMinutes() != null ? paper.getDurationMinutes() : 60);
            ps.setObject(++i, paper.getStatus() != null ? paper.getStatus() : 1);
            return ps;
        }, keyHolder);
        Number key = keyHolder.getKey();
        long id = key != null ? key.longValue() : 0L;
        if (id > 0 && paper.getQuestions() != null && !paper.getQuestions().isEmpty()) {
            for (PaperQuestionItem item : paper.getQuestions()) {
                if (item.getQuestionId() != null) {
                    jdbcTemplate.update("INSERT INTO ly_paper_question (paper_id, question_id, score, sort) VALUES (?, ?, ?, ?)",
                            id, item.getQuestionId(), item.getScore() != null ? item.getScore() : 10, item.getSort() != null ? item.getSort() : 0);
                }
            }
        }
        return id;
    }

    @Override
    public void update(Paper paper) {
        if (paper.getId() == null) return;
        String sql = "UPDATE ly_paper SET title = ?, total_score = ?, pass_score = ?, duration_minutes = ?, status = ? WHERE id = ? AND deleted = 0";
        jdbcTemplate.update(sql,
                paper.getTitle(),
                paper.getTotalScore() != null ? paper.getTotalScore() : 100,
                paper.getPassScore() != null ? paper.getPassScore() : 60,
                paper.getDurationMinutes() != null ? paper.getDurationMinutes() : 60,
                paper.getStatus() != null ? paper.getStatus() : 1,
                paper.getId());
        jdbcTemplate.update("DELETE FROM ly_paper_question WHERE paper_id = ?", paper.getId());
        if (paper.getQuestions() != null && !paper.getQuestions().isEmpty()) {
            for (PaperQuestionItem item : paper.getQuestions()) {
                if (item.getQuestionId() != null) {
                    jdbcTemplate.update("INSERT INTO ly_paper_question (paper_id, question_id, score, sort) VALUES (?, ?, ?, ?)",
                            paper.getId(), item.getQuestionId(), item.getScore() != null ? item.getScore() : 10, item.getSort() != null ? item.getSort() : 0);
                }
            }
        }
    }

    @Override
    public void delete(Long id) {
        if (id == null) return;
        jdbcTemplate.update("UPDATE ly_paper SET deleted = 1 WHERE id = ?", id);
        jdbcTemplate.update("DELETE FROM ly_paper_question WHERE paper_id = ?", id);
    }

    private static class PaperRowMapper implements RowMapper<Paper> {
        @Override
        public Paper mapRow(ResultSet rs, int rowNum) throws SQLException {
            Paper p = new Paper();
            p.setId(rs.getLong("id"));
            p.setTitle(rs.getString("title"));
            p.setTotalScore(rs.getObject("total_score", Integer.class));
            p.setPassScore(rs.getObject("pass_score", Integer.class));
            p.setDurationMinutes(rs.getObject("duration_minutes", Integer.class));
            p.setStatus(rs.getObject("status", Integer.class));
            p.setCreateTime(rs.getObject("create_time", java.time.LocalDateTime.class));
            p.setUpdateTime(rs.getObject("update_time", java.time.LocalDateTime.class));
            p.setDeleted(rs.getObject("deleted", Integer.class));
            return p;
        }
    }
}
