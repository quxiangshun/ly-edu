package com.lyedu.controller;

import com.lyedu.common.Result;
import com.lyedu.common.ResultCode;
import com.lyedu.entity.Course;
import com.lyedu.entity.UserCourse;
import com.lyedu.entity.UserVideoProgress;
import com.lyedu.entity.Video;
import com.lyedu.service.CourseService;
import com.lyedu.service.UserCourseService;
import com.lyedu.service.UserVideoProgressService;
import com.lyedu.service.VideoService;
import com.lyedu.util.JwtUtil;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

/**
 * 学习相关控制器
 *
 * @author LyEdu Team
 */
@Slf4j
@RestController
@RequestMapping("/learning")
@RequiredArgsConstructor
public class LearningController {

    private final UserCourseService userCourseService;
    private final UserVideoProgressService userVideoProgressService;
    private final CourseService courseService;
    private final VideoService videoService;
    private final JwtUtil jwtUtil;

    private Long getUserIdFromAuth(String authorization) {
        if (authorization == null || authorization.isBlank()) return null;
        String token = authorization.startsWith("Bearer ") ? authorization.substring(7) : authorization.trim();
        if (token.isEmpty()) return null;
        return jwtUtil.getUserIdFromToken(token);
    }

    /**
     * 加入课程
     */
    @PostMapping("/join")
    public Result<Void> joinCourse(@RequestBody JoinCourseRequest request, @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) return Result.error(ResultCode.UNAUTHORIZED);
        userCourseService.joinCourse(userId, request.getCourseId());
        return Result.success();
    }

    /**
     * 获取我的课程列表
     */
    @GetMapping("/my-courses")
    public Result<List<UserCourse>> myCourses(@RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) return Result.error(ResultCode.UNAUTHORIZED);
        return Result.success(userCourseService.listByUserId(userId));
    }

    /**
     * 更新视频学习进度
     */
    @PostMapping("/video-progress")
    public Result<Void> updateVideoProgress(@RequestBody VideoProgressRequest request, @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) return Result.error(ResultCode.UNAUTHORIZED);
        userVideoProgressService.updateProgress(userId, request.getVideoId(), request.getProgress(), request.getDuration());

        // 同步更新课程学习进度：按该课程下所有课时的完成时长/总时长计算百分比
        Video video = videoService.getById(request.getVideoId());
        if (video != null && video.getCourseId() != null) {
            Long courseId = video.getCourseId();
            userCourseService.joinCourse(userId, courseId);
            java.util.List<Video> courseVideos = videoService.listByCourseId(courseId);
            java.util.List<Long> videoIds = courseVideos.stream().map(Video::getId).collect(java.util.stream.Collectors.toList());
            java.util.Map<Long, UserVideoProgress> progressMap = userVideoProgressService.getProgressMap(userId, videoIds);
            long totalDuration = 0;
            long finishedDuration = 0;
            for (Video v : courseVideos) {
                int d = v.getDuration() != null ? v.getDuration() : 0;
                if (d <= 0) continue;
                totalDuration += d;
                UserVideoProgress p = progressMap.get(v.getId());
                if (p != null && p.getProgress() != null) {
                    finishedDuration += Math.min(p.getProgress(), d);
                }
            }
            int percent = (totalDuration > 0) ? (int) (finishedDuration * 100 / totalDuration) : 0;
            userCourseService.updateProgress(userId, courseId, Math.min(100, percent));
        }

        return Result.success();
    }

    /**
     * 播放心跳（防挂机）：播放过程中定时上报，更新 last_play_ping_at
     */
    @PostMapping("/play-ping")
    public Result<Void> playPing(@RequestBody PlayPingRequest request, @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) return Result.error(ResultCode.UNAUTHORIZED);
        userVideoProgressService.updateLastPlayPing(userId, request.getVideoId());
        return Result.success();
    }

    /**
     * 获取视频学习进度
     */
    @GetMapping("/video-progress/{videoId}")
    public Result<UserVideoProgress> getVideoProgress(@PathVariable Long videoId, @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) return Result.error(ResultCode.UNAUTHORIZED);
        UserVideoProgress progress = userVideoProgressService.getByUserAndVideo(userId, videoId);
        return Result.success(progress);
    }

    /**
     * 我的学习：仅返回看过的课程（有视频观看记录的课程）
     * 无 Token 返回 401；其它异常不抛 500，返回空列表。
     */
    @GetMapping("/watched-courses")
    public Result<List<Course>> watchedCourses(@RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED);
        }
        try {
            List<Long> courseIds = userVideoProgressService.listWatchedCourseIds(userId);
            if (courseIds == null) {
                return Result.success(Collections.emptyList());
            }
            Set<Long> seen = new LinkedHashSet<>(courseIds);
            List<Course> list = new ArrayList<>();
            for (Long courseId : seen) {
                if (courseId == null || courseId <= 0) continue;
                try {
                    Course c = courseService.getDetailById(courseId);
                    if (c != null) {
                        list.add(c);
                    }
                } catch (Exception ignored) {
                }
            }
            return Result.success(list);
        } catch (Exception e) {
            log.warn("watched-courses error, userId={}", userId, e);
            return Result.success(Collections.emptyList());
        }
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

    @Data
    public static class PlayPingRequest {
        private Long videoId;
    }
}
