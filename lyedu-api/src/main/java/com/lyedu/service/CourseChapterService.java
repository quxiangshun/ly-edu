package com.lyedu.service;

import com.lyedu.entity.CourseChapter;

import java.util.List;

/**
 * 课程章节服务
 *
 * @author LyEdu Team
 */
public interface CourseChapterService {

    /**
     * 按课程ID查询章节列表（按排序）
     */
    List<CourseChapter> listByCourseId(Long courseId);

    /**
     * 根据ID查询
     */
    CourseChapter getById(Long id);

    void save(CourseChapter chapter);

    void update(CourseChapter chapter);

    void delete(Long id);
}
