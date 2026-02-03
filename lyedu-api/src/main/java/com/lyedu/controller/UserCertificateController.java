package com.lyedu.controller;

import com.lyedu.common.Result;
import com.lyedu.common.ResultCode;
import com.lyedu.entity.CertificateTemplate;
import com.lyedu.entity.UserCertificate;
import com.lyedu.service.CertificateTemplateService;
import com.lyedu.service.UserCertificateService;
import com.lyedu.util.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/** 用户证书记录：我的证书列表、详情（含模板用于打印） */
@RestController
@RequestMapping("/user-certificate")
@RequiredArgsConstructor
public class UserCertificateController {

    private final UserCertificateService userCertificateService;
    private final CertificateTemplateService certificateTemplateService;
    private final JwtUtil jwtUtil;

    private Long getUserIdFromAuth(String authorization) {
        if (authorization == null || authorization.isBlank()) return null;
        String token = authorization.startsWith("Bearer ") ? authorization.substring(7) : authorization.trim();
        if (token.isEmpty()) return null;
        return jwtUtil.getUserIdFromToken(token);
    }

    /** 当前用户的证书列表 */
    @GetMapping("/my")
    public Result<List<UserCertificate>> myList(@RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        if (userId == null) return Result.error(ResultCode.UNAUTHORIZED);
        return Result.success(userCertificateService.listByUserId(userId));
    }

    /** 证书详情（用于打印；需校验归属或管理员） */
    @NoAuth
    @GetMapping("/{id}")
    public Result<UserCertificateWithTemplate> getById(
            @PathVariable Long id,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        Long userId = getUserIdFromAuth(authorization);
        UserCertificate uc = userCertificateService.getById(id);
        if (uc == null) return Result.error(ResultCode.NOT_FOUND);
        if (userId == null) return Result.error(ResultCode.UNAUTHORIZED);
        if (!userId.equals(uc.getUserId())) return Result.error(ResultCode.FORBIDDEN);
        CertificateTemplate template = certificateTemplateService.getById(uc.getTemplateId());
        UserCertificateWithTemplate dto = new UserCertificateWithTemplate();
        dto.setUserCertificate(uc);
        dto.setTemplate(template);
        return Result.success(dto);
    }

    /** 管理端：按用户ID查证书记录 */
    @GetMapping("/admin/user/{userId}")
    public Result<List<UserCertificate>> listByUserId(@PathVariable Long userId) {
        return Result.success(userCertificateService.listByUserId(userId));
    }

    public static class UserCertificateWithTemplate {
        private UserCertificate userCertificate;
        private CertificateTemplate template;

        public UserCertificate getUserCertificate() { return userCertificate; }
        public void setUserCertificate(UserCertificate userCertificate) { this.userCertificate = userCertificate; }
        public CertificateTemplate getTemplate() { return template; }
        public void setTemplate(CertificateTemplate template) { this.template = template; }
    }
}
