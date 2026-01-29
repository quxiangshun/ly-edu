package com.lyedu.service;

import com.lyedu.entity.Video;

import java.util.List;

/**
 * 视频服务接口
 *
 * @author LyEdu Team
 */
public interface VideoService {

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
