package com.lyedu.service.impl;

import com.lyedu.service.CourseExamService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 课程-考试关联服务实现。课程可以无关联考试，属正常数据。
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class CourseExamServiceImpl implements CourseExamService {

    private static final String TABLE = "ly_course_exam";

    private final JdbcTemplate jdbcTemplate;

    @Override
    public Long getExamIdByCourseId(Long courseId) {
        if (courseId == null) return null;
        String sql = "SELECT exam_id FROM " + TABLE + " WHERE course_id = ?";
        List<Long> list = jdbcTemplate.query(sql, (rs, rowNum) -> rs.getLong("exam_id"), courseId);
        return (list != null && !list.isEmpty()) ? list.get(0) : null;
    }

    @Override
    public void setCourseExam(Long courseId, Long examId) {
        if (courseId == null) return;
        jdbcTemplate.update("DELETE FROM " + TABLE + " WHERE course_id = ?", courseId);
        if (examId != null) {
            jdbcTemplate.update("INSERT INTO " + TABLE + " (course_id, exam_id) VALUES (?, ?)", courseId, examId);
        }
    }
}
