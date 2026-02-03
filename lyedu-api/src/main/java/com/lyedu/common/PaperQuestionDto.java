package com.lyedu.common;

import com.lyedu.entity.Question;
import lombok.Data;

import java.io.Serializable;

/**
 * 试卷题目项 DTO（含题目详情、分值、顺序）
 *
 * @author LyEdu Team
 */
@Data
public class PaperQuestionDto implements Serializable {

    private static final long serialVersionUID = 1L;

    private Long questionId;
    private Integer score;
    private Integer sort;
    private Question question;
}
