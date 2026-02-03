package com.lyedu.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 课程评论实体（支持多级回复）
 *
 * @author LyEdu Team
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class CourseComment extends BaseEntity {

    private Long courseId;
    private Long chapterId;
    private Long userId;
    private Long parentId;
    private String content;
    private Integer status;
}
