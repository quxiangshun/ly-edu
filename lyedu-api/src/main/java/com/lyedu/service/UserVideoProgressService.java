package com.lyedu.service;

import com.lyedu.entity.UserVideoProgress;

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
}
