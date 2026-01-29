package com.lyedu.controller;

import com.lyedu.common.Result;
import com.lyedu.entity.UserCourse;
import com.lyedu.entity.UserVideoProgress;
import com.lyedu.service.UserCourseService;
import com.lyedu.service.UserVideoProgressService;
import com.lyedu.util.JwtUtil;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 学习相关控制器
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/learning")
@RequiredArgsConstructor
public class LearningController {

    private final UserCourseService userCourseService;
    private final UserVideoProgressService userVideoProgressService;
    private final JwtUtil jwtUtil;

    /**
     * 加入课程
     */
    @PostMapping("/join")
    public Result<Void> joinCourse(@RequestBody JoinCourseRequest request, @RequestHeader("Authorization") String token) {
        Long userId = jwtUtil.getUserIdFromToken(token.replace("Bearer ", ""));
        userCourseService.joinCourse(userId, request.getCourseId());
        return Result.success();
    }

    /**
     * 获取我的课程列表
     */
    @GetMapping("/my-courses")
    public Result<List<UserCourse>> myCourses(@RequestHeader("Authorization") String token) {
        Long userId = jwtUtil.getUserIdFromToken(token.replace("Bearer ", ""));
        return Result.success(userCourseService.listByUserId(userId));
    }

    /**
     * 更新视频学习进度
     */
    @PostMapping("/video-progress")
    public Result<Void> updateVideoProgress(@RequestBody VideoProgressRequest request, @RequestHeader("Authorization") String token) {
        Long userId = jwtUtil.getUserIdFromToken(token.replace("Bearer ", ""));
        userVideoProgressService.updateProgress(userId, request.getVideoId(), request.getProgress(), request.getDuration());
        return Result.success();
    }

    /**
     * 获取视频学习进度
     */
    @GetMapping("/video-progress/{videoId}")
    public Result<UserVideoProgress> getVideoProgress(@PathVariable Long videoId, @RequestHeader("Authorization") String token) {
        Long userId = jwtUtil.getUserIdFromToken(token.replace("Bearer ", ""));
        UserVideoProgress progress = userVideoProgressService.getByUserAndVideo(userId, videoId);
        return Result.success(progress);
    }

    @Data
    public static class JoinCourseRequest {
        private Long courseId;
    }

    @Data
    public static class VideoProgressRequest {
        private Long videoId;
        private Integer progress;
        private Integer duration;
    }
}
