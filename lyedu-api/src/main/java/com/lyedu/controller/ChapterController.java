package com.lyedu.controller;

import com.lyedu.common.Result;
import com.lyedu.entity.CourseChapter;
import com.lyedu.service.CourseChapterService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 课程章节管理（管理端）
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/chapter")
@RequiredArgsConstructor
public class ChapterController {

    private final CourseChapterService courseChapterService;

    @GetMapping
    public Result<List<CourseChapter>> list(@RequestParam Long courseId) {
        return Result.success(courseChapterService.listByCourseId(courseId));
    }

    @PostMapping
    public Result<Long> create(@RequestBody ChapterRequest request) {
        CourseChapter chapter = new CourseChapter();
        chapter.setCourseId(request.getCourseId());
        chapter.setTitle(request.getTitle());
        chapter.setSort(request.getSort() != null ? request.getSort() : 0);
        courseChapterService.save(chapter);
        return Result.success(chapter.getId());
    }

    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody ChapterRequest request) {
        CourseChapter chapter = courseChapterService.getById(id);
        if (chapter == null) {
            return Result.error(404, "章节不存在");
        }
        chapter.setTitle(request.getTitle());
        chapter.setSort(request.getSort() != null ? request.getSort() : 0);
        courseChapterService.update(chapter);
        return Result.success();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        courseChapterService.delete(id);
        return Result.success();
    }

    @Data
    public static class ChapterRequest {
        private Long courseId;
        private String title;
        private Integer sort;
    }
}
