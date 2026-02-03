package com.lyedu.controller;

import com.lyedu.annotation.NoAuth;
import com.lyedu.common.Result;
import com.lyedu.common.ResultCode;
import com.lyedu.entity.User;
import com.lyedu.service.FeishuApiService;
import com.lyedu.service.UserService;
import com.lyedu.util.JwtUtil;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * 认证控制器
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final UserService userService;
    private final FeishuApiService feishuApiService;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    /**
     * 用户登录（获取 JWT）
     */
    @NoAuth
    @PostMapping("/login")
    public Result<Map<String, Object>> login(@RequestBody @Validated LoginRequest request) {
        // 根据用户名查询用户
        User user = userService.findByUsername(request.getUsername());
        if (user == null) {
            return Result.error(ResultCode.USER_NOT_FOUND);
        }
        if (user.getStatus() != null && user.getStatus() == 0) {
            return Result.error(ResultCode.FORBIDDEN.getCode(), "账号已被禁用");
        }

        // 校验密码（BCrypt）
        String storedPassword = user.getPassword();
        if (storedPassword != null) {
            storedPassword = storedPassword.trim();
        }
        
        if (storedPassword == null || storedPassword.isEmpty() || 
            !passwordEncoder.matches(request.getPassword(), storedPassword)) {
            return Result.error(ResultCode.LOGIN_ERROR);
        }

        // 生成 Token
        String token = jwtUtil.generateToken(user.getId(), user.getUsername());

        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("userInfo", new UserInfo(user.getId(), user.getUsername(), user.getRealName(), user.getRole()));

        return Result.success(data);
    }

    /**
     * 获取飞书授权页 URL（前端跳转后用户扫码登录，飞书回调到 redirect_uri?code=xxx）
     */
    @NoAuth
    @GetMapping("/feishu/url")
    public Result<Map<String, String>> feishuUrl(
            @RequestParam(value = "redirect_uri") String redirectUri,
            @RequestParam(value = "state", required = false) String state) {
        String url = feishuApiService.buildAuthorizeUrl(redirectUri, state);
        return Result.success(Map.of("url", url));
    }

    /**
     * 飞书授权回调：用 code 换用户信息，查找或创建用户，返回 JWT
     */
    @NoAuth
    @PostMapping("/feishu/callback")
    public Result<Map<String, Object>> feishuCallback(@RequestBody FeishuCallbackRequest request) {
        if (request.getCode() == null || request.getCode().isEmpty()) {
            return Result.error(400, "缺少 code");
        }
        Map<String, Object> feishuUser = feishuApiService.getUserInfoByCode(request.getCode(), request.getRedirectUri());
        if (feishuUser == null) {
            return Result.error(400, "飞书授权失败或未配置飞书应用");
        }
        String openId = feishuUser.get("open_id") != null ? feishuUser.get("open_id").toString() : null;
        if (openId == null || openId.isEmpty()) {
            return Result.error(400, "飞书用户信息异常");
        }
        String name = feishuUser.get("name") != null ? feishuUser.get("name").toString() : null;
        if (name == null) name = "飞书用户";
        String avatarUrl = feishuUser.get("avatar_url") != null ? feishuUser.get("avatar_url").toString() : null;

        User user = userService.findByFeishuOpenId(openId);
        if (user == null) {
            user = new User();
            user.setUsername("feishu_" + openId);
            user.setPassword(UUID.randomUUID().toString());
            user.setRealName(name);
            user.setAvatar(avatarUrl);
            user.setFeishuOpenId(openId);
            user.setRole("student");
            user.setStatus(1);
            userService.save(user);
            user = userService.findByFeishuOpenId(openId);
        }
        if (user == null) {
            return Result.error(500, "用户创建失败");
        }
        if (user.getStatus() != null && user.getStatus() == 0) {
            return Result.error(ResultCode.FORBIDDEN.getCode(), "账号已被禁用");
        }
        String token = jwtUtil.generateToken(user.getId(), user.getUsername());
        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("userInfo", new UserInfo(user.getId(), user.getUsername(), user.getRealName(), user.getRole()));
        return Result.success(data);
    }

    @Data
    public static class FeishuCallbackRequest {
        private String code;
        private String redirectUri;
    }

    /**
     * 登录请求体
     */
    @Data
    public static class LoginRequest {

        @NotBlank(message = "用户名不能为空")
        private String username;

        @NotBlank(message = "密码不能为空")
        private String password;
    }

    /**
     * 返回给前端的基础用户信息
     */
    @Data
    public static class UserInfo {
        private final Long id;
        private final String username;
        private final String realName;
        private final String role;
    }
}

