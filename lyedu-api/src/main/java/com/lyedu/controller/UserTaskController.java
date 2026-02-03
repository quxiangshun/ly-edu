package com.lyedu.controller;

import com.lyedu.annotation.NoAuth;
import com.lyedu.common.Result;
import com.lyedu.common.ResultCode;
import com.lyedu.common.TaskWithUserProgressDto;
import com.lyedu.entity.Task;
import com.lyedu.entity.UserTask;
import com.lyedu.service.UserTaskService;
import com.lyedu.util.JwtUtil;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/user-task")
@RequiredArgsConstructor
public class UserTaskController {

    private final UserTaskService userTaskService;
    private final JwtUtil jwtUtil;

    private Long getUserIdFromAuth(String authorization) {
        if (authorization == null || authorization.isBlank()) return null;
        String token = authorization.startsWith("Bearer ") ? authorization.substring(7) : authorization.trim();
        if (token.isEmpty()) return null;
        return jwtUtil.getUserIdFromToken(token);
    }

    /** 我的任务列表（含进度/完成状态） */
    @NoAuth
    @GetMapping("/my")
    public Result<List<TaskWithUserProgressDto>> myTasks(
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) return Result.error(ResultCode.UNAUTHORIZED);
        return Result.success(userTaskService.listMyTasks(userId));
    }

    /** 任务详情（含用户进度，仅可见任务） */
    @NoAuth
    @GetMapping("/task/{taskId}")
    public Result<Task> taskDetail(
            @PathVariable Long taskId,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) return Result.error(ResultCode.UNAUTHORIZED);
        Task t = userTaskService.getTaskDetail(taskId, userId);
        if (t == null) return Result.error(ResultCode.NOT_FOUND);
        return Result.success(t);
    }

    /** 获取或创建用户任务记录 */
    @NoAuth
    @GetMapping("/task/{taskId}/progress")
    public Result<UserTask> getOrCreateProgress(
            @PathVariable Long taskId,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) return Result.error(ResultCode.UNAUTHORIZED);
        UserTask ut = userTaskService.getOrCreateUserTask(taskId, userId);
        if (ut == null) return Result.error(ResultCode.NOT_FOUND);
        return Result.success(ut);
    }

    /** 更新进度（闯关项完成情况）；全部完成时自动颁发证书 */
    @NoAuth
    @PostMapping("/task/{taskId}/progress")
    public Result<UserTask> updateProgress(
            @PathVariable Long taskId,
            @RequestBody ProgressRequest body,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) return Result.error(ResultCode.UNAUTHORIZED);
        UserTask ut = userTaskService.updateProgress(taskId, userId, body != null ? body.getProgress() : null);
        if (ut == null) return Result.error(ResultCode.NOT_FOUND);
        return Result.success(ut);
    }

    @Data
    public static class ProgressRequest {
        private String progress;
    }
}
