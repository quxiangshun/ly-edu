package com.lyedu.entity;

import lombok.Data;

/**
 * 试卷-题目项（组卷用）
 *
 * @author LyEdu Team
 */
@Data
public class PaperQuestionItem {
    private Long questionId;
    private Integer score;
    private Integer sort;
}
