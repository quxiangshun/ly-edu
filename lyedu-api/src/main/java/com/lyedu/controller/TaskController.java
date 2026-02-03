package com.lyedu.controller;

import com.lyedu.annotation.NoAuth;
import com.lyedu.common.PageResult;
import com.lyedu.common.Result;
import com.lyedu.common.ResultCode;
import com.lyedu.entity.Task;
import com.lyedu.service.TaskService;
import com.lyedu.util.JwtUtil;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/task")
@RequiredArgsConstructor
public class TaskController {

    private final TaskService taskService;
    private final JwtUtil jwtUtil;

    private Long getUserIdFromAuth(String authorization) {
        if (authorization == null || authorization.isBlank()) return null;
        String token = authorization.startsWith("Bearer ") ? authorization.substring(7) : authorization.trim();
        if (token.isEmpty()) return null;
        return jwtUtil.getUserIdFromToken(token);
    }

    @NoAuth
    @GetMapping("/page")
    public Result<PageResult<Task>> page(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "20") Integer size,
            @RequestParam(required = false) String keyword,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        return Result.success(taskService.page(page, size, keyword, userId));
    }

    @NoAuth
    @GetMapping("/{id}")
    public Result<Task> getById(
            @PathVariable Long id,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        Task t = taskService.getById(id, userId);
        if (t == null) return Result.error(ResultCode.NOT_FOUND);
        return Result.success(t);
    }

    @PostMapping
    public Result<Long> create(@RequestBody TaskRequest request) {
        Task t = new Task();
        t.setTitle(request.getTitle());
        t.setDescription(request.getDescription());
        t.setCycleType(request.getCycleType() != null ? request.getCycleType() : "once");
        t.setCycleConfig(request.getCycleConfig());
        t.setItems(request.getItems() != null ? request.getItems() : "[]");
        t.setCertificateId(request.getCertificateId());
        t.setSort(request.getSort() != null ? request.getSort() : 0);
        t.setStatus(request.getStatus() != null ? request.getStatus() : 1);
        t.setStartTime(request.getStartTime());
        t.setEndTime(request.getEndTime());
        t.setDepartmentIds(request.getDepartmentIds());
        long id = taskService.save(t);
        return Result.success(id);
    }

    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody TaskRequest request) {
        Task t = taskService.getByIdIgnoreVisibility(id);
        if (t == null) return Result.error(ResultCode.NOT_FOUND);
        t.setTitle(request.getTitle());
        t.setDescription(request.getDescription());
        t.setCycleType(request.getCycleType() != null ? request.getCycleType() : "once");
        t.setCycleConfig(request.getCycleConfig());
        t.setItems(request.getItems() != null ? request.getItems() : "[]");
        t.setCertificateId(request.getCertificateId());
        t.setSort(request.getSort() != null ? request.getSort() : 0);
        t.setStatus(request.getStatus() != null ? request.getStatus() : 1);
        t.setStartTime(request.getStartTime());
        t.setEndTime(request.getEndTime());
        t.setDepartmentIds(request.getDepartmentIds());
        taskService.update(t);
        return Result.success();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        Task t = taskService.getByIdIgnoreVisibility(id);
        if (t == null) return Result.error(ResultCode.NOT_FOUND);
        taskService.delete(id);
        return Result.success();
    }

    @GetMapping("/admin/{id}")
    public Result<Task> getByIdAdmin(@PathVariable Long id) {
        Task t = taskService.getByIdIgnoreVisibility(id);
        if (t == null) return Result.error(ResultCode.NOT_FOUND);
        return Result.success(t);
    }

    @Data
    public static class TaskRequest {
        private String title;
        private String description;
        private String cycleType;
        private String cycleConfig;
        private String items;
        private Long certificateId;
        private Integer sort;
        private Integer status;
        private java.time.LocalDateTime startTime;
        private java.time.LocalDateTime endTime;
        private java.util.List<Long> departmentIds;
    }
}
