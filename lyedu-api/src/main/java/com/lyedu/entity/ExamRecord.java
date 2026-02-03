package com.lyedu.entity;

import lombok.Data;

import java.time.LocalDateTime;

/**
 * 考试记录实体（用户交卷）
 *
 * @author LyEdu Team
 */
@Data
public class ExamRecord {

    private Long id;
    private Long examId;
    private Long userId;
    private Long paperId;
    /** 得分 */
    private Integer score;
    /** 是否及格：0-否，1-是 */
    private Integer passed;
    /** 用户答案 JSON */
    private String answers;
    private LocalDateTime submitTime;
    private LocalDateTime createTime;
}
