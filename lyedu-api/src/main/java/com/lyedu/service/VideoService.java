package com.lyedu.service;

import com.lyedu.common.PageResult;
import com.lyedu.entity.Video;

import java.util.List;

/**
 * 视频服务接口
 *
 * @author LyEdu Team
 */
public interface VideoService {

    /**
     * 分页查询视频
     *
     * @param page 页码（从1开始）
     * @param size 每页大小
     * @param courseId 课程ID（可选）
     * @param keyword 关键词（视频标题）
     * @return 分页结果
     */
    PageResult<Video> page(Integer page, Integer size, Long courseId, String keyword);

    /**
     * 根据课程ID获取视频列表
     * @param userId 当前用户ID（可选），用于设置 liked
     */
    List<Video> listByCourseId(Long courseId, Long userId);

    /**
     * 根据章节ID获取视频列表
     * @param userId 当前用户ID（可选），用于设置 liked
     */
    List<Video> listByChapterId(Long chapterId, Long userId);

    /**
     * 根据ID获取视频
     * @param userId 当前用户ID（可选），用于设置 liked
     */
    Video getById(Long id, Long userId);

    /**
     * 记录播放次数（每次播放+1）
     */
    void recordPlay(Long videoId);

    /**
     * 点赞（一人只能点一次）
     */
    void like(Long videoId, Long userId);

    /**
     * 取消点赞
     */
    void unlike(Long videoId, Long userId);

    /**
     * 保存视频
     */
    void save(Video video);

    /**
     * 更新视频
     */
    void update(Video video);

    /**
     * 删除视频
     */
    void delete(Long id);
}
