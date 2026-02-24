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
     * 分页查询课程
     * @param status 为 1 时仅返回上架课程（PC/uni 学员端）；为 null 时返回全部（管理端）
     */
    PageResult<Course> page(Integer page, Integer size, String keyword, Long categoryId, Integer status);

    /**
     * 根据ID获取课程详情（包含章节和视频）
     */
    Course getDetailById(Long id, Long userId);

    /**
     * 按ID获取课程（管理端用）
     */
    Course getByIdIgnoreVisibility(Long id);

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
     * 获取推荐课程列表（仅返回上架课程）
     */
    List<Course> listRecommended(Integer limit, Long userId);
}
