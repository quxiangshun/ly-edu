package com.lyedu.service;

import com.lyedu.common.PageResult;
import com.lyedu.entity.Course;

import java.util.List;

/**
 * 课程服务接口
 *
 * @author LyEdu Team
 */
public interface CourseService {

    /**
     * 分页查询课程（可选按用户部门过滤可见性）
     * @param userId 当前用户ID，为 null 时仅返回公开课程
     */
    PageResult<Course> page(Integer page, Integer size, String keyword, Long categoryId, Long userId);

    /**
     * 根据ID获取课程详情（包含章节和视频）；若传 userId 则校验可见性
     */
    Course getDetailById(Long id, Long userId);

    /**
     * 保存课程
     */
    void save(Course course);

    /**
     * 更新课程
     */
    void update(Course course);

    /**
     * 删除课程
     */
    void delete(Long id);

    /**
     * 获取推荐课程列表（可选按用户部门过滤可见性）
     * @param userId 当前用户ID，为 null 时仅返回公开课程
     */
    List<Course> listRecommended(Integer limit, Long userId);
}
