package com.lyedu.service;

import com.lyedu.entity.UserVideoProgress;

import java.util.List;
import java.util.Map;

/**
 * 用户视频学习进度服务接口
 *
 * @author LyEdu Team
 */
public interface UserVideoProgressService {

    /**
     * 更新视频学习进度
     */
    void updateProgress(Long userId, Long videoId, Integer progress, Integer duration);

    /**
     * 获取用户视频学习进度
     */
    UserVideoProgress getByUserAndVideo(Long userId, Long videoId);

    /**
     * 获取用户看过视频所属的课程ID列表（去重，按最近观看排序）
     */
    List<Long> listWatchedCourseIds(Long userId);

    /**
     * 批量获取用户对多个视频的学习进度（videoId -> UserVideoProgress）
     */
    Map<Long, UserVideoProgress> getProgressMap(Long userId, List<Long> videoIds);

    /**
     * 更新播放心跳时间（防挂机）
     */
    void updateLastPlayPing(Long userId, Long videoId);
}
