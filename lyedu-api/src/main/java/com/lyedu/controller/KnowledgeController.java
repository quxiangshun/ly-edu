package com.lyedu.controller;

import com.lyedu.annotation.NoAuth;
import com.lyedu.common.PageResult;
import com.lyedu.common.Result;
import com.lyedu.common.ResultCode;
import com.lyedu.entity.Knowledge;
import com.lyedu.service.KnowledgeService;
import com.lyedu.util.JwtUtil;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

/**
 * 知识库控制器（列表/详情对学员按部门可见；管理端增删改）
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/knowledge")
@RequiredArgsConstructor
public class KnowledgeController {

    private final KnowledgeService knowledgeService;
    private final JwtUtil jwtUtil;

    private Long getUserIdFromAuth(String authorization) {
        if (authorization == null || authorization.isBlank()) return null;
        String token = authorization.startsWith("Bearer ") ? authorization.substring(7) : authorization.trim();
        if (token.isEmpty()) return null;
        return jwtUtil.getUserIdFromToken(token);
    }

    /**
     * 分页列表（带 Authorization 时按用户部门过滤可见性）
     */
    @NoAuth
    @GetMapping("/page")
    public Result<PageResult<Knowledge>> page(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "20") Integer size,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String category,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        return Result.success(knowledgeService.page(page, size, keyword, category, userId));
    }

    /**
     * 根据ID获取（用于详情/下载链接；带可见性校验）
     */
    @NoAuth
    @GetMapping("/{id}")
    public Result<Knowledge> getById(
            @PathVariable Long id,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        Knowledge k = knowledgeService.getById(id, userId);
        if (k == null) {
            return Result.error(ResultCode.NOT_FOUND);
        }
        return Result.success(k);
    }

    /**
     * 新增（管理端）
     */
    @PostMapping
    public Result<Long> create(@RequestBody KnowledgeRequest request) {
        Knowledge k = new Knowledge();
        k.setTitle(request.getTitle());
        k.setCategory(request.getCategory());
        k.setFileName(request.getFileName());
        k.setFileUrl(request.getFileUrl());
        k.setFileSize(request.getFileSize());
        k.setFileType(request.getFileType());
        k.setSort(request.getSort() != null ? request.getSort() : 0);
        k.setVisibility(request.getVisibility() != null ? request.getVisibility() : 1);
        k.setDepartmentIds(request.getDepartmentIds());
        long id = knowledgeService.save(k);
        return Result.success(id);
    }

    /**
     * 更新（管理端）
     */
    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody KnowledgeRequest request) {
        Knowledge k = knowledgeService.getByIdIgnoreVisibility(id);
        if (k == null) return Result.error(ResultCode.NOT_FOUND);
        k.setTitle(request.getTitle());
        k.setCategory(request.getCategory());
        k.setFileName(request.getFileName());
        k.setFileUrl(request.getFileUrl());
        k.setFileSize(request.getFileSize());
        k.setFileType(request.getFileType());
        k.setSort(request.getSort() != null ? request.getSort() : 0);
        k.setVisibility(request.getVisibility() != null ? request.getVisibility() : 1);
        k.setDepartmentIds(request.getDepartmentIds());
        knowledgeService.update(k);
        return Result.success();
    }

    /**
     * 删除（管理端）
     */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        Knowledge k = knowledgeService.getByIdIgnoreVisibility(id);
        if (k == null) return Result.error(ResultCode.NOT_FOUND);
        knowledgeService.delete(id);
        return Result.success();
    }

    /**
     * 管理端：根据ID获取（忽略可见性）
     */
    @GetMapping("/admin/{id}")
    public Result<Knowledge> getByIdAdmin(@PathVariable Long id) {
        Knowledge k = knowledgeService.getByIdIgnoreVisibility(id);
        if (k == null) return Result.error(ResultCode.NOT_FOUND);
        return Result.success(k);
    }

    @Data
    public static class KnowledgeRequest {
        private String title;
        private String category;
        private String fileName;
        private String fileUrl;
        private Long fileSize;
        private String fileType;
        private Integer sort;
        private Integer visibility;
        private java.util.List<Long> departmentIds;
    }
}
