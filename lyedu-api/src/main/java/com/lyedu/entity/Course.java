package com.lyedu.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 课程实体
 *
 * @author LyEdu Team
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class Course extends BaseEntity {

    /**
     * 课程标题
     */
    private String title;

    /**
     * 课程封面
     */
    private String cover;

    /**
     * 课程描述
     */
    private String description;

    /**
     * 分类ID
     */
    private Long categoryId;

    /**
     * 状态（0-下架，1-上架）
     */
    private Integer status;

    /**
     * 排序
     */
    private Integer sort;

    /**
     * 是否必修（0-选修，1-必修）
     */
    private Integer isRequired;
}
