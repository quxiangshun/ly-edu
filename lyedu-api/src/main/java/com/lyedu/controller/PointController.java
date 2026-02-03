package com.lyedu.controller;

import com.lyedu.annotation.NoAuth;
import com.lyedu.common.Result;
import com.lyedu.common.ResultCode;
import com.lyedu.entity.PointLog;
import com.lyedu.service.PointService;
import com.lyedu.util.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 积分：我的积分、流水、排行（学员端）
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/point")
@RequiredArgsConstructor
public class PointController {

    private final PointService pointService;
    private final JwtUtil jwtUtil;

    private Long getUserIdFromAuth(String authorization) {
        if (authorization == null || authorization.isBlank()) return null;
        String token = authorization.startsWith("Bearer ") ? authorization.substring(7) : authorization.trim();
        if (token.isEmpty()) return null;
        return jwtUtil.getUserIdFromToken(token);
    }

    /** 我的总积分 */
    @GetMapping("/my")
    public Result<Integer> myTotal(@RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) return Result.error(ResultCode.UNAUTHORIZED);
        return Result.success(pointService.getTotalPoints(userId));
    }

    /** 我的积分流水（分页） */
    @GetMapping("/log")
    public Result<List<PointLog>> myLog(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) return Result.error(ResultCode.UNAUTHORIZED);
        return Result.success(pointService.listMyLog(userId, page, size));
    }

    /** 积分排行（可公开；可选部门） */
    @NoAuth
    @GetMapping("/ranking")
    public Result<List<Map<String, Object>>> ranking(
            @RequestParam(defaultValue = "50") int limit,
            @RequestParam(required = false) Long departmentId) {
        return Result.success(pointService.listRanking(limit, departmentId));
    }
}
