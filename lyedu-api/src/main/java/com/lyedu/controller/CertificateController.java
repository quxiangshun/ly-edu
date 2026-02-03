package com.lyedu.controller;

import com.lyedu.common.Result;
import com.lyedu.common.ResultCode;
import com.lyedu.entity.Certificate;
import com.lyedu.service.CertificateService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/** 证书颁发规则管理（管理端 CRUD） */
@RestController
@RequestMapping("/certificate")
@RequiredArgsConstructor
public class CertificateController {

    private final CertificateService certificateService;

    @GetMapping("/list")
    public Result<List<Certificate>> list() {
        return Result.success(certificateService.listAll());
    }

    @GetMapping("/{id}")
    public Result<Certificate> getById(@PathVariable Long id) {
        Certificate c = certificateService.getById(id);
        if (c == null) return Result.error(ResultCode.NOT_FOUND);
        return Result.success(c);
    }

    @PostMapping
    public Result<Long> create(@RequestBody CertificateRequest request) {
        Certificate c = new Certificate();
        c.setTemplateId(request.getTemplateId());
        c.setName(request.getName());
        c.setSourceType(request.getSourceType());
        c.setSourceId(request.getSourceId());
        c.setSort(request.getSort() != null ? request.getSort() : 0);
        c.setStatus(request.getStatus() != null ? request.getStatus() : 1);
        long id = certificateService.save(c);
        return Result.success(id);
    }

    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody CertificateRequest request) {
        Certificate c = certificateService.getById(id);
        if (c == null) return Result.error(ResultCode.NOT_FOUND);
        c.setTemplateId(request.getTemplateId());
        c.setName(request.getName());
        c.setSourceType(request.getSourceType());
        c.setSourceId(request.getSourceId());
        c.setSort(request.getSort() != null ? request.getSort() : 0);
        c.setStatus(request.getStatus() != null ? request.getStatus() : 1);
        certificateService.update(c);
        return Result.success();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        Certificate c = certificateService.getById(id);
        if (c == null) return Result.error(ResultCode.NOT_FOUND);
        certificateService.delete(id);
        return Result.success();
    }

    @Data
    public static class CertificateRequest {
        private Long templateId;
        private String name;
        private String sourceType;
        private Long sourceId;
        private Integer sort;
        private Integer status;
    }
}
