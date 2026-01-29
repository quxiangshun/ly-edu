package com.lyedu.entity;

import lombok.Data;

import java.time.LocalDateTime;

/**
 * 用户课程关联实体
 *
 * @author LyEdu Team
 */
@Data
public class UserCourse {

    /**
     * 主键ID
     */
    private Long id;

    /**
     * 用户ID
     */
    private Long userId;

    /**
     * 课程ID
     */
    private Long courseId;

    /**
     * 学习进度（百分比）
     */
    private Integer progress;

    /**
     * 状态（0-学习中，1-已完成）
     */
    private Integer status;

    /**
     * 创建时间
     */
    private LocalDateTime createTime;

    /**
     * 更新时间
     */
    private LocalDateTime updateTime;
}
