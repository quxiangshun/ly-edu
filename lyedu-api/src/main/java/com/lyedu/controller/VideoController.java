package com.lyedu.controller;

import com.lyedu.annotation.NoAuth;
import com.lyedu.common.Result;
import com.lyedu.entity.Video;
import com.lyedu.service.VideoService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 视频管理控制器
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/video")
@RequiredArgsConstructor
public class VideoController {

    private final VideoService videoService;

    /**
     * 根据课程ID获取视频列表
     */
    @NoAuth
    @GetMapping("/course/{courseId}")
    public Result<List<Video>> listByCourseId(@PathVariable Long courseId) {
        return Result.success(videoService.listByCourseId(courseId));
    }

    /**
     * 根据章节ID获取视频列表
     */
    @NoAuth
    @GetMapping("/chapter/{chapterId}")
    public Result<List<Video>> listByChapterId(@PathVariable Long chapterId) {
        return Result.success(videoService.listByChapterId(chapterId));
    }

    /**
     * 根据ID获取视频
     */
    @NoAuth
    @GetMapping("/{id}")
    public Result<Video> getById(@PathVariable Long id) {
        Video video = videoService.getById(id);
        if (video == null) {
            return Result.error(404, "视频不存在");
        }
        return Result.success(video);
    }

    /**
     * 创建视频
     */
    @PostMapping
    public Result<Void> create(@RequestBody VideoRequest request) {
        Video video = new Video();
        video.setCourseId(request.getCourseId());
        video.setChapterId(request.getChapterId());
        video.setTitle(request.getTitle());
        video.setUrl(request.getUrl());
        video.setDuration(request.getDuration());
        video.setSort(request.getSort());
        videoService.save(video);
        return Result.success();
    }

    /**
     * 更新视频
     */
    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody VideoRequest request) {
        Video video = videoService.getById(id);
        if (video == null) {
            return Result.error(404, "视频不存在");
        }
        video.setCourseId(request.getCourseId());
        video.setChapterId(request.getChapterId());
        video.setTitle(request.getTitle());
        video.setUrl(request.getUrl());
        video.setDuration(request.getDuration());
        video.setSort(request.getSort());
        videoService.update(video);
        return Result.success();
    }

    /**
     * 删除视频
     */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        videoService.delete(id);
        return Result.success();
    }

    @Data
    public static class VideoRequest {
        private Long courseId;
        private Long chapterId;
        private String title;
        private String url;
        private Integer duration;
        private Integer sort;
    }
}
