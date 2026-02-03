package com.lyedu.controller;

import com.lyedu.common.Result;
import com.lyedu.common.ResultCode;
import com.lyedu.entity.ExamRecord;
import com.lyedu.service.ExamRecordService;
import com.lyedu.util.JwtUtil;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/exam-record")
@RequiredArgsConstructor
public class ExamRecordController {

    private final ExamRecordService examRecordService;
    private final JwtUtil jwtUtil;

    private Long getUserIdFromAuth(String authorization) {
        if (authorization == null || authorization.isBlank()) return null;
        String token = authorization.startsWith("Bearer ") ? authorization.substring(7) : authorization.trim();
        if (token.isEmpty()) return null;
        return jwtUtil.getUserIdFromToken(token);
    }

    @PostMapping("/submit")
    public Result<ExamRecord> submit(
            @RequestBody SubmitRequest request,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) return Result.error(ResultCode.UNAUTHORIZED);
        if (request.getExamId() == null) return Result.error(ResultCode.PARAM_ERROR);
        ExamRecord r = examRecordService.submit(request.getExamId(), userId, request.getAnswers());
        if (r == null) return Result.error(ResultCode.ERROR);
        return Result.success(r);
    }

    @GetMapping("/my")
    public Result<List<ExamRecord>> myRecords(@RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) return Result.error(ResultCode.UNAUTHORIZED);
        return Result.success(examRecordService.listByUserId(userId));
    }

    @GetMapping("/exam/{examId}")
    public Result<List<ExamRecord>> listByExam(@PathVariable Long examId) {
        return Result.success(examRecordService.listByExamId(examId));
    }

    @GetMapping("/exam/{examId}/user/{userId}")
    public Result<ExamRecord> getByExamAndUser(@PathVariable Long examId, @PathVariable Long userId) {
        ExamRecord r = examRecordService.getByExamAndUser(examId, userId);
        if (r == null) return Result.success(null);
        return Result.success(r);
    }

    @Data
    public static class SubmitRequest {
        private Long examId;
        private String answers;
    }
}
