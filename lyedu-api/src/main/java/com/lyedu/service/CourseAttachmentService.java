package com.lyedu.service;

import com.lyedu.entity.CourseAttachment;

import java.util.List;

/**
 * 课程附件服务
 *
 * @author LyEdu Team
 */
public interface CourseAttachmentService {

    /**
     * 按课程ID查询附件列表（按排序）
     */
    List<CourseAttachment> listByCourseId(Long courseId);

    void save(CourseAttachment attachment);

    void delete(Long id);
}
