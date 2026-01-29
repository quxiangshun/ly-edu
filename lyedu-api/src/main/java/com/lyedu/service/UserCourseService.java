package com.lyedu.service;

import com.lyedu.entity.UserCourse;

import java.util.List;

/**
 * 用户课程服务接口
 *
 * @author LyEdu Team
 */
public interface UserCourseService {

    /**
     * 用户加入课程
     */
    void joinCourse(Long userId, Long courseId);

    /**
     * 获取用户的学习课程列表
     */
    List<UserCourse> listByUserId(Long userId);

    /**
     * 获取用户课程信息
     */
    UserCourse getByUserAndCourse(Long userId, Long courseId);

    /**
     * 更新学习进度
     */
    void updateProgress(Long userId, Long courseId, Integer progress);
}
