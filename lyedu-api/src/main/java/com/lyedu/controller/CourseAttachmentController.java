package com.lyedu.controller;

import com.lyedu.common.Result;
import com.lyedu.entity.CourseAttachment;
import com.lyedu.service.CourseAttachmentService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 课程附件管理（管理端）
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/course-attachment")
@RequiredArgsConstructor
public class CourseAttachmentController {

    private final CourseAttachmentService courseAttachmentService;

    @GetMapping
    public Result<List<CourseAttachment>> list(@RequestParam Long courseId) {
        return Result.success(courseAttachmentService.listByCourseId(courseId));
    }

    @PostMapping
    public Result<Void> create(@RequestBody AttachmentRequest request) {
        CourseAttachment attachment = new CourseAttachment();
        attachment.setCourseId(request.getCourseId());
        attachment.setName(request.getName());
        attachment.setType(request.getType());
        attachment.setFileUrl(request.getFileUrl());
        attachment.setSort(request.getSort() != null ? request.getSort() : 0);
        courseAttachmentService.save(attachment);
        return Result.success();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        courseAttachmentService.delete(id);
        return Result.success();
    }

    @Data
    public static class AttachmentRequest {
        private Long courseId;
        private String name;
        private String type;
        private String fileUrl;
        private Integer sort;
    }
}
