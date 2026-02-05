package com.lyedu.controller;

import com.lyedu.annotation.NoAuth;
import com.lyedu.common.CourseDetail;
import com.lyedu.common.PageResult;
import com.lyedu.common.Result;
import com.lyedu.entity.Course;
import com.lyedu.entity.CourseAttachment;
import com.lyedu.entity.CourseChapter;
import com.lyedu.entity.UserCourse;
import com.lyedu.entity.UserVideoProgress;
import com.lyedu.entity.Video;
import com.lyedu.service.CourseAttachmentService;
import com.lyedu.service.CourseChapterService;
import com.lyedu.service.CourseExamService;
import com.lyedu.service.CourseService;
import com.lyedu.service.UserCourseService;
import com.lyedu.service.UserVideoProgressService;
import com.lyedu.service.VideoService;
import com.lyedu.util.JwtUtil;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

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
    private final CourseChapterService courseChapterService;
    private final CourseAttachmentService courseAttachmentService;
    private final CourseExamService courseExamService;
    private final UserVideoProgressService userVideoProgressService;
    private final UserCourseService userCourseService;
    private final JwtUtil jwtUtil;

    private Long getUserIdFromAuth(String authorization) {
        if (authorization == null || authorization.isBlank()) return null;
        String token = authorization.startsWith("Bearer ") ? authorization.substring(7) : authorization.trim();
        if (token.isEmpty()) return null;
        return jwtUtil.getUserIdFromToken(token);
    }

    /**
     * 分页查询课程（带 Authorization 时按用户部门过滤可见性）
     */
    @NoAuth
    @GetMapping("/page")
    public Result<PageResult<Course>> page(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) Long categoryId,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        return Result.success(courseService.page(page, size, keyword, categoryId, userId));
    }

    /**
     * 获取课程详情（包含章节/课时、视频列表、学习记录与进度）
     * 带 Authorization 时返回 learnRecord、courseProgress
     */
    @NoAuth
    @GetMapping("/{id}")
    public Result<CourseDetail> getById(
            @PathVariable Long id,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        Course course = courseService.getDetailById(id, userId);
        if (course == null) {
            return Result.error(404, "课程不存在");
        }

        List<CourseChapter> chapterList = courseChapterService.listByCourseId(id);
        List<Video> videos = videoService.listByCourseId(id);

        // 按章节组装：每章节下 hours = 该章节的课时（视频）
        List<CourseDetail.ChapterItem> chapterItems = new ArrayList<>();
        for (CourseChapter ch : chapterList) {
            CourseDetail.ChapterItem item = new CourseDetail.ChapterItem();
            item.setId(ch.getId());
            item.setTitle(ch.getTitle());
            item.setSort(ch.getSort());
            List<Video> hours = videos.stream()
                    .filter(v -> ch.getId().equals(v.getChapterId()))
                    .collect(Collectors.toList());
            item.setHours(hours);
            chapterItems.add(item);
        }
        // 未分类课时（无 chapterId）
        List<Video> uncategorized = videos.stream().filter(v -> v.getChapterId() == null).collect(Collectors.toList());
        if (!uncategorized.isEmpty()) {
            CourseDetail.ChapterItem uncat = new CourseDetail.ChapterItem();
            uncat.setId(null);
            uncat.setTitle("未分类");
            uncat.setSort(Integer.MAX_VALUE);
            uncat.setHours(uncategorized);
            chapterItems.add(uncat);
        }

        List<CourseAttachment> attachments = courseAttachmentService.listByCourseId(id);

        CourseDetail detail = new CourseDetail();
        detail.setCourse(course);
        detail.setVideos(videos);
        detail.setChapters(chapterItems);
        detail.setAttachments(attachments);
        Long examId = courseExamService.getExamIdByCourseId(id);
        detail.setExamId(examId);

        if (userId != null && !videos.isEmpty()) {
            List<Long> videoIds = videos.stream().map(Video::getId).collect(Collectors.toList());
            Map<Long, UserVideoProgress> progressMap = userVideoProgressService.getProgressMap(userId, videoIds);
            Map<Long, CourseDetail.LearnRecordItem> learnRecord = new HashMap<>();
            for (Map.Entry<Long, UserVideoProgress> e : progressMap.entrySet()) {
                UserVideoProgress p = e.getValue();
                CourseDetail.LearnRecordItem lr = new CourseDetail.LearnRecordItem();
                lr.setProgress(p.getProgress());
                lr.setDuration(p.getDuration());
                learnRecord.put(e.getKey(), lr);
            }
            detail.setLearnRecord(learnRecord);

            long totalDuration = 0;
            long finishedDuration = 0;
            for (Video v : videos) {
                int d = v.getDuration() != null ? v.getDuration() : 0;
                if (d <= 0) continue;
                totalDuration += d;
                UserVideoProgress p = progressMap.get(v.getId());
                if (p != null && p.getProgress() != null) {
                    finishedDuration += Math.min(p.getProgress(), d);
                }
            }
            int courseProgressPercent = (totalDuration > 0)
                    ? (int) (finishedDuration * 100 / totalDuration)
                    : 0;
            detail.setCourseProgress(Math.min(100, courseProgressPercent));

            UserCourse uc = userCourseService.getByUserAndCourse(userId, id);
            if (uc != null && uc.getProgress() != null && uc.getProgress() > courseProgressPercent) {
                detail.setCourseProgress(uc.getProgress());
            }
        }

        return Result.success(detail);
    }

    /**
     * 获取推荐课程（带 Authorization 时按用户部门过滤可见性）
     */
    @NoAuth
    @GetMapping("/recommended")
    public Result<List<Course>> recommended(
            @RequestParam(defaultValue = "6") Integer limit,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        return Result.success(courseService.listRecommended(limit, userId));
    }

    /**
     * 创建课程（关联部门可为多个）
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
        course.setIsRequired(request.getIsRequired());
        course.setVisibility(request.getVisibility() != null ? request.getVisibility() : 1);
        course.setDepartmentIds(request.getDepartmentIds());
        courseService.save(course);
        return Result.success();
    }

    /**
     * 更新课程（关联部门可为多个）
     */
    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody CourseRequest request) {
        Course course = courseService.getByIdIgnoreVisibility(id);
        if (course == null) {
            return Result.error(404, "课程不存在");
        }
        course.setTitle(request.getTitle());
        course.setCover(request.getCover());
        course.setDescription(request.getDescription());
        course.setCategoryId(request.getCategoryId());
        course.setStatus(request.getStatus());
        course.setSort(request.getSort());
        course.setIsRequired(request.getIsRequired());
        course.setVisibility(request.getVisibility() != null ? request.getVisibility() : 1);
        course.setDepartmentIds(request.getDepartmentIds());
        courseService.update(course);
        return Result.success();
    }

    /**
     * 获取课程关联的考试ID，无关联时返回 200 且 data 为 null（正常，不报错）。
     */
    @GetMapping("/{id}/exam")
    public Result<Long> getCourseExam(@PathVariable Long id) {
        if (courseService.getByIdIgnoreVisibility(id) == null) {
            return Result.error(404, "课程不存在");
        }
        Long examId = courseExamService.getExamIdByCourseId(id);
        return Result.success(examId);
    }

    /**
     * 设置课程关联的考试；examId 为 null 表示取消关联。
     */
    @PutMapping("/{id}/exam")
    public Result<Void> setCourseExam(@PathVariable Long id, @RequestBody CourseExamRequest body) {
        if (courseService.getByIdIgnoreVisibility(id) == null) {
            return Result.error(404, "课程不存在");
        }
        courseExamService.setCourseExam(id, body.getExamId());
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
    public static class CourseExamRequest {
        private Long examId;
    }

    @Data
    public static class CourseRequest {
        private String title;
        private String cover;
        private String description;
        private Long categoryId;
        private Integer status;
        private Integer sort;
        /** 是否必修：0-选修，1-必修 */
        private Integer isRequired;
        /** 可见性：1-公开，0-私有 */
        private Integer visibility;
        /** 关联部门ID列表（私有时必填，可多选） */
        private List<Long> departmentIds;
    }
}
