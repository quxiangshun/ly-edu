package com.lyedu.controller;

import com.lyedu.common.Result;
import com.lyedu.common.ResultCode;
import com.lyedu.entity.CertificateTemplate;
import com.lyedu.service.CertificateTemplateService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/** 证书模板管理（管理端 CRUD） */
@RestController
@RequestMapping("/certificate-template")
@RequiredArgsConstructor
public class CertificateTemplateController {

    private final CertificateTemplateService certificateTemplateService;

    @GetMapping("/list")
    public Result<List<CertificateTemplate>> list() {
        return Result.success(certificateTemplateService.listAll());
    }

    @GetMapping("/{id}")
    public Result<CertificateTemplate> getById(@PathVariable Long id) {
        CertificateTemplate t = certificateTemplateService.getById(id);
        if (t == null) return Result.error(ResultCode.NOT_FOUND);
        return Result.success(t);
    }

    @PostMapping
    public Result<Long> create(@RequestBody CertificateTemplateRequest request) {
        CertificateTemplate t = new CertificateTemplate();
        t.setName(request.getName());
        t.setDescription(request.getDescription());
        t.setConfig(request.getConfig());
        t.setSort(request.getSort() != null ? request.getSort() : 0);
        t.setStatus(request.getStatus() != null ? request.getStatus() : 1);
        long id = certificateTemplateService.save(t);
        return Result.success(id);
    }

    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody CertificateTemplateRequest request) {
        CertificateTemplate t = certificateTemplateService.getById(id);
        if (t == null) return Result.error(ResultCode.NOT_FOUND);
        t.setName(request.getName());
        t.setDescription(request.getDescription());
        t.setConfig(request.getConfig());
        t.setSort(request.getSort() != null ? request.getSort() : 0);
        t.setStatus(request.getStatus() != null ? request.getStatus() : 1);
        certificateTemplateService.update(t);
        return Result.success();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        CertificateTemplate t = certificateTemplateService.getById(id);
        if (t == null) return Result.error(ResultCode.NOT_FOUND);
        certificateTemplateService.delete(id);
        return Result.success();
    }

    @Data
    public static class CertificateTemplateRequest {
        private String name;
        private String description;
        private String config;
        private Integer sort;
        private Integer status;
    }
}
