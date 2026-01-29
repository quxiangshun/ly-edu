package com.lyedu.controller;

import com.lyedu.annotation.NoAuth;
import com.lyedu.common.Result;
import com.lyedu.common.ResultCode;
import com.lyedu.entity.User;
import com.lyedu.service.UserService;
import com.lyedu.util.JwtUtil;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.HashMap;
import java.util.Map;

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

