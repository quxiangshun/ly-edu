package com.lyedu.controller;

import com.lyedu.annotation.NoAuth;
import com.lyedu.common.CourseCommentDto;
import com.lyedu.common.Result;
import com.lyedu.common.ResultCode;
import com.lyedu.entity.CourseComment;
import com.lyedu.service.CourseCommentService;
import com.lyedu.util.JwtUtil;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 课程评论控制器
 */
@RestController
@RequestMapping("/course")
@RequiredArgsConstructor
public class CourseCommentController {

    private final CourseCommentService courseCommentService;
    private final JwtUtil jwtUtil;

    private Long getUserIdFromAuth(String authorization) {
        if (authorization == null || authorization.isBlank()) return null;
        String token = authorization.startsWith("Bearer ") ? authorization.substring(7) : authorization.trim();
        if (token.isEmpty()) return null;
        return jwtUtil.getUserIdFromToken(token);
    }

    /**
     * 获取课程评论列表（可选章节维度）
     */
    @NoAuth
    @GetMapping("/{courseId}/comment")
    public Result<List<CourseCommentDto>> list(
            @PathVariable Long courseId,
            @RequestParam(required = false) Long chapterId) {
        List<CourseCommentDto> list = courseCommentService.listByCourse(courseId, chapterId);
        return Result.success(list);
    }

    /**
     * 发表评论或回复（需登录）
     */
    @PostMapping("/{courseId}/comment")
    public Result<CourseComment> add(
            @PathVariable Long courseId,
            @RequestBody CommentRequest body,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED.getCode(), "请先登录");
        }
        String content = body != null ? body.getContent() : null;
        if (content == null || content.trim().isEmpty()) {
            return Result.error(ResultCode.PARAM_ERROR.getCode(), "评论内容不能为空");
        }
        CourseComment comment = courseCommentService.add(
                courseId,
                body != null ? body.getChapterId() : null,
                userId,
                body != null ? body.getParentId() : null,
                content.trim());
        return Result.success(comment);
    }

    /**
     * 删除评论（需登录，本人或管理员）
     */
    @DeleteMapping("/comment/{id}")
    public Result<Void> delete(
            @PathVariable Long id,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) {
            return Result.error(ResultCode.UNAUTHORIZED.getCode(), "请先登录");
        }
        courseCommentService.delete(id);
        return Result.success(null);
    }

    @Data
    public static class CommentRequest {
        private Long chapterId;
        private Long parentId;
        private String content;
    }
}
