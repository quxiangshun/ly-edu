package com.lyedu.service.impl;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.lyedu.common.PaperQuestionDto;
import com.lyedu.entity.Exam;
import com.lyedu.entity.ExamRecord;
import com.lyedu.entity.Paper;
import com.lyedu.service.ExamRecordService;
import com.lyedu.service.ExamService;
import com.lyedu.service.PaperService;
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
import java.util.Map;

/**
 * 考试记录服务实现（交卷计分：单选/多选/判断按答案匹配，填空/简答暂不计分或按关键词）
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class ExamRecordServiceImpl implements ExamRecordService {

    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    private final JdbcTemplate jdbcTemplate;
    private final ExamService examService;
    private final PaperService paperService;

    @Override
    public ExamRecord submit(Long examId, Long userId, String answersJson) {
        Exam exam = examService.getByIdIgnoreVisibility(examId);
        if (exam == null) return null;
        Paper paper = paperService.getById(exam.getPaperId());
        if (paper == null) return null;
        List<PaperQuestionDto> items = paperService.listQuestionsByPaperId(exam.getPaperId());
        if (items == null || items.isEmpty()) return null;

        Map<String, String> userAnswers;
        try {
            userAnswers = answersJson != null && !answersJson.isBlank()
                    ? OBJECT_MAPPER.readValue(answersJson, new TypeReference<Map<String, String>>() {})
                    : Map.of();
        } catch (Exception e) {
            userAnswers = Map.of();
        }

        int totalScore = 0;
        int passScore = exam.getPassScore() != null ? exam.getPassScore() : (paper.getPassScore() != null ? paper.getPassScore() : 60);
        for (PaperQuestionDto dto : items) {
            if (dto.getScore() == null || dto.getQuestion() == null) continue;
            String correct = dto.getQuestion().getAnswer();
            String user = userAnswers.get(String.valueOf(dto.getQuestionId()));
            if (correct == null) correct = "";
            if (user == null) user = "";
            correct = correct.trim().toUpperCase();
            user = user.trim().toUpperCase();
            if (correct.equals(user)) totalScore += dto.getScore();
        }
        int passed = totalScore >= passScore ? 1 : 0;

        String sql = "INSERT INTO ly_exam_record (exam_id, user_id, paper_id, score, passed, answers, submit_time) VALUES (?, ?, ?, ?, ?, ?, ?)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(con -> {
            PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setLong(1, examId);
            ps.setLong(2, userId);
            ps.setLong(3, paper.getId());
            ps.setInt(4, totalScore);
            ps.setInt(5, passed);
            ps.setString(6, answersJson);
            ps.setTimestamp(7, Timestamp.valueOf(LocalDateTime.now()));
            return ps;
        }, keyHolder);
        Number key = keyHolder.getKey();
        if (key == null) return null;
        ExamRecord r = new ExamRecord();
        r.setId(key.longValue());
        r.setExamId(examId);
        r.setUserId(userId);
        r.setPaperId(paper.getId());
        r.setScore(totalScore);
        r.setPassed(passed);
        r.setAnswers(answersJson);
        r.setSubmitTime(LocalDateTime.now());
        if (passed == 1) {
            userCertificateService.issueIfEligible("exam", examId, userId);
        }
        return r;
    }

    @Override
    public List<ExamRecord> listByExamId(Long examId) {
        if (examId == null) return List.of();
        String sql = "SELECT id, exam_id, user_id, paper_id, score, passed, answers, submit_time, create_time FROM ly_exam_record WHERE exam_id = ? ORDER BY submit_time DESC";
        return jdbcTemplate.query(sql, new ExamRecordRowMapper(), examId);
    }

    @Override
    public List<ExamRecord> listByUserId(Long userId) {
        if (userId == null) return List.of();
        String sql = "SELECT id, exam_id, user_id, paper_id, score, passed, answers, submit_time, create_time FROM ly_exam_record WHERE user_id = ? ORDER BY submit_time DESC";
        return jdbcTemplate.query(sql, new ExamRecordRowMapper(), userId);
    }

    @Override
    public ExamRecord getByExamAndUser(Long examId, Long userId) {
        if (examId == null || userId == null) return null;
        String sql = "SELECT id, exam_id, user_id, paper_id, score, passed, answers, submit_time, create_time FROM ly_exam_record WHERE exam_id = ? AND user_id = ? ORDER BY id DESC LIMIT 1";
        List<ExamRecord> list = jdbcTemplate.query(sql, new ExamRecordRowMapper(), examId, userId);
        return list.isEmpty() ? null : list.get(0);
    }

    private static class ExamRecordRowMapper implements RowMapper<ExamRecord> {
        @Override
        public ExamRecord mapRow(ResultSet rs, int rowNum) throws SQLException {
            ExamRecord r = new ExamRecord();
            r.setId(rs.getLong("id"));
            r.setExamId(rs.getLong("exam_id"));
            r.setUserId(rs.getLong("user_id"));
            r.setPaperId(rs.getLong("paper_id"));
            r.setScore(rs.getObject("score", Integer.class));
            r.setPassed(rs.getObject("passed", Integer.class));
            r.setAnswers(rs.getString("answers"));
            Timestamp st = rs.getTimestamp("submit_time");
            r.setSubmitTime(st != null ? st.toLocalDateTime() : null);
            r.setCreateTime(rs.getObject("create_time", LocalDateTime.class));
            return r;
        }
    }
}
