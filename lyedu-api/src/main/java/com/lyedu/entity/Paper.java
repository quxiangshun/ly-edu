package com.lyedu.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

import java.util.List;

/**
 * 试卷实体
 *
 * @author LyEdu Team
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class Paper extends BaseEntity {

    private String title;
    /** 总分 */
    private Integer totalScore;
    /** 及格分 */
    private Integer passScore;
    /** 考试时长（分钟） */
    private Integer durationMinutes;
    /** 状态：0-禁用，1-启用 */
    private Integer status;
    /** 关联题目（含分值、顺序），不持久化到 ly_paper */
    private List<PaperQuestionItem> questions;
}
