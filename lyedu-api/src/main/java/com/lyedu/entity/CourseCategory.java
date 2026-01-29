package com.lyedu.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 课程分类实体
 *
 * @author LyEdu Team
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class CourseCategory extends BaseEntity {

    /**
     * 分类名称
     */
    private String name;

    /**
     * 父分类ID
     */
    private Long parentId;

    /**
     * 排序
     */
    private Integer sort;

    /**
     * 状态（0-禁用，1-启用）
     */
    private Integer status;
}
