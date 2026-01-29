package com.lyedu.controller;

import com.lyedu.annotation.NoAuth;
import com.lyedu.common.CourseDetail;
import com.lyedu.common.PageResult;
import com.lyedu.common.Result;
import com.lyedu.entity.Course;
import com.lyedu.entity.Video;
import com.lyedu.service.CourseService;
import com.lyedu.service.VideoService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 课程管理控制器
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/course")
@RequiredArgsConstructor
public class CourseController {

    private final CourseService courseService;
    private final VideoService videoService;

    /**
     * 分页查询课程
     */
    @NoAuth
    @GetMapping("/page")
    public Result<PageResult<Course>> page(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) Long categoryId) {
        return Result.success(courseService.page(page, size, keyword, categoryId));
    }

    /**
     * 获取课程详情（包含视频列表）
     */
    @NoAuth
    @GetMapping("/{id}")
    public Result<CourseDetail> getById(@PathVariable Long id) {
        Course course = courseService.getDetailById(id);
        if (course == null) {
            return Result.error(404, "课程不存在");
        }
        
        // 获取课程相关的视频列表
        List<Video> videos = videoService.listByCourseId(id);
        
        CourseDetail detail = new CourseDetail();
        detail.setCourse(course);
        detail.setVideos(videos);
        
        return Result.success(detail);
    }

    /**
     * 获取推荐课程
     */
    @NoAuth
    @GetMapping("/recommended")
    public Result<List<Course>> recommended(@RequestParam(defaultValue = "6") Integer limit) {
        return Result.success(courseService.listRecommended(limit));
    }

    /**
     * 创建课程
     */
    @PostMapping
    public Result<Void> create(@RequestBody CourseRequest request) {
        Course course = new Course();
        course.setTitle(request.getTitle());
        course.setCover(request.getCover());
        course.setDescription(request.getDescription());
        course.setCategoryId(request.getCategoryId());
        course.setStatus(request.getStatus());
        course.setSort(request.getSort());
        courseService.save(course);
        return Result.success();
    }

    /**
     * 更新课程
     */
    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody CourseRequest request) {
        Course course = courseService.getDetailById(id);
        if (course == null) {
            return Result.error(404, "课程不存在");
        }
        course.setTitle(request.getTitle());
        course.setCover(request.getCover());
        course.setDescription(request.getDescription());
        course.setCategoryId(request.getCategoryId());
        course.setStatus(request.getStatus());
        course.setSort(request.getSort());
        courseService.update(course);
        return Result.success();
    }

    /**
     * 删除课程
     */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        courseService.delete(id);
        return Result.success();
    }

    @Data
    public static class CourseRequest {
        private String title;
        private String cover;
        private String description;
        private Long categoryId;
        private Integer status;
        private Integer sort;
    }
}
