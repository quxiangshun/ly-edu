package com.lyedu.entity;

import lombok.Data;

import java.time.LocalDateTime;

/**
 * 用户视频学习进度实体
 *
 * @author LyEdu Team
 */
@Data
public class UserVideoProgress {

    /**
     * 主键ID
     */
    private Long id;

    /**
     * 用户ID
     */
    private Long userId;

    /**
     * 视频ID
     */
    private Long videoId;

    /**
     * 学习进度（秒）
     */
    private Integer progress;

    /**
     * 视频总时长（秒）
     */
    private Integer duration;

    /**
     * 是否完成（0-未完成，1-已完成）
     */
    private Integer isFinished;

    /**
     * 创建时间
     */
    private LocalDateTime createTime;

    /**
     * 更新时间
     */
    private LocalDateTime updateTime;

    /**
     * 最近播放心跳时间（防挂机）
     */
    private LocalDateTime lastPlayPingAt;
}
