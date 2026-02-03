package com.lyedu.controller;

import com.lyedu.annotation.NoAuth;
import com.lyedu.common.PageResult;
import com.lyedu.common.Result;
import com.lyedu.common.ResultCode;
import com.lyedu.entity.Exam;
import com.lyedu.service.ExamService;
import com.lyedu.util.JwtUtil;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/exam")
@RequiredArgsConstructor
public class ExamController {

    private final ExamService examService;
    private final JwtUtil jwtUtil;

    private Long getUserIdFromAuth(String authorization) {
        if (authorization == null || authorization.isBlank()) return null;
        String token = authorization.startsWith("Bearer ") ? authorization.substring(7) : authorization.trim();
        if (token.isEmpty()) return null;
        return jwtUtil.getUserIdFromToken(token);
    }

    @NoAuth
    @GetMapping("/page")
    public Result<PageResult<Exam>> page(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "20") Integer size,
            @RequestParam(required = false) String keyword,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        return Result.success(examService.page(page, size, keyword, userId));
    }

    @NoAuth
    @GetMapping("/{id}")
    public Result<Exam> getById(
            @PathVariable Long id,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        Exam e = examService.getById(id, userId);
        if (e == null) return Result.error(ResultCode.NOT_FOUND);
        return Result.success(e);
    }

    @PostMapping
    public Result<Long> create(@RequestBody ExamRequest request) {
        Exam e = new Exam();
        e.setTitle(request.getTitle());
        e.setPaperId(request.getPaperId());
        e.setStartTime(request.getStartTime());
        e.setEndTime(request.getEndTime());
        e.setDurationMinutes(request.getDurationMinutes());
        e.setPassScore(request.getPassScore());
        e.setVisibility(request.getVisibility() != null ? request.getVisibility() : 1);
        e.setStatus(request.getStatus() != null ? request.getStatus() : 1);
        e.setDepartmentIds(request.getDepartmentIds());
        long id = examService.save(e);
        return Result.success(id);
    }

    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody ExamRequest request) {
        Exam e = examService.getByIdIgnoreVisibility(id);
        if (e == null) return Result.error(ResultCode.NOT_FOUND);
        e.setTitle(request.getTitle());
        e.setPaperId(request.getPaperId());
        e.setStartTime(request.getStartTime());
        e.setEndTime(request.getEndTime());
        e.setDurationMinutes(request.getDurationMinutes());
        e.setPassScore(request.getPassScore());
        e.setVisibility(request.getVisibility() != null ? request.getVisibility() : 1);
        e.setStatus(request.getStatus() != null ? request.getStatus() : 1);
        e.setDepartmentIds(request.getDepartmentIds());
        examService.update(e);
        return Result.success();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        Exam e = examService.getByIdIgnoreVisibility(id);
        if (e == null) return Result.error(ResultCode.NOT_FOUND);
        examService.delete(id);
        return Result.success();
    }

    @GetMapping("/admin/{id}")
    public Result<Exam> getByIdAdmin(@PathVariable Long id) {
        Exam e = examService.getByIdIgnoreVisibility(id);
        if (e == null) return Result.error(ResultCode.NOT_FOUND);
        return Result.success(e);
    }

    @Data
    public static class ExamRequest {
        private String title;
        private Long paperId;
        private java.time.LocalDateTime startTime;
        private java.time.LocalDateTime endTime;
        private Integer durationMinutes;
        private Integer passScore;
        private Integer visibility;
        private Integer status;
        private java.util.List<Long> departmentIds;
    }
}
