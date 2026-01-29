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
     */
    List<Video> listByCourseId(Long courseId);

    /**
     * 根据章节ID获取视频列表
     */
    List<Video> listByChapterId(Long chapterId);

    /**
     * 根据ID获取视频
     */
    Video getById(Long id);

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
