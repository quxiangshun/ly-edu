package com.lyedu.entity;

import lombok.Data;

import java.time.LocalDateTime;

/**
 * 用户任务进度实体
 *
 * @author LyEdu Team
 */
@Data
public class UserTask {

    private Long id;
    private Long userId;
    private Long taskId;
    /** 进度 JSON：{"items":[{"type":"course","id":1,"done":1},...]} */
    private String progress;
    /** 状态：0-进行中，1-已完成 */
    private Integer status;
    private LocalDateTime completedAt;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
