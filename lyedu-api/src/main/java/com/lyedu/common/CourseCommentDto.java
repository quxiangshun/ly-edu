package com.lyedu.common;

import lombok.Data;

import java.time.LocalDateTime;

/**
 * 课程评论 DTO（含评论人姓名，供前端展示）
 */
@Data
public class CourseCommentDto {

    private Long id;
    private Long courseId;
    private Long chapterId;
    private Long userId;
    private String userRealName;
    private Long parentId;
    private String content;
    private Integer status;
    private LocalDateTime createTime;
}
