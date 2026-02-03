package com.lyedu.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 考试任务实体
 *
 * @author LyEdu Team
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class Exam extends BaseEntity {

    private String title;
    private Long paperId;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    /** 考试时长（分钟），null 取试卷默认 */
    private Integer durationMinutes;
    /** 及格分，null 取试卷默认 */
    private Integer passScore;
    /** 可见性：1-公开，0-私有 */
    private Integer visibility;
    /** 状态：0-下架，1-上架 */
    private Integer status;
    /** 关联部门ID列表（私有时），来自 ly_exam_department */
    private List<Long> departmentIds;
}
