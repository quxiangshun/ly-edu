package com.lyedu.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 试题实体
 *
 * @author LyEdu Team
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class Question extends BaseEntity {

    /** 题型：single-单选，multi-多选，judge-判断，fill-填空，short-简答 */
    private String type;
    /** 题目标题/题干 */
    private String title;
    /** 选项 JSON 数组 */
    private String options;
    /** 参考答案 */
    private String answer;
    /** 默认分值 */
    private Integer score;
    /** 解析 */
    private String analysis;
    /** 排序 */
    private Integer sort;
}
