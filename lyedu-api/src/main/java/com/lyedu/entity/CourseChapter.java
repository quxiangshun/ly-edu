package com.lyedu.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 课程章节实体
 *
 * @author LyEdu Team
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class CourseChapter extends BaseEntity {

    /**
     * 课程ID
     */
    private Long courseId;

    /**
     * 章节标题
     */
    private String title;

    /**
     * 排序
     */
    private Integer sort;
}
