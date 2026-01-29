package com.lyedu.controller;

import com.lyedu.common.PageResult;
import com.lyedu.common.Result;
import com.lyedu.entity.User;
import com.lyedu.service.UserService;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

/**
 * 用户管理控制器
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/user")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    /**
     * 分页查询用户
     */
    @GetMapping("/page")
    public Result<PageResult<User>> page(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) Long departmentId,
            @RequestParam(required = false) String role,
            @RequestParam(required = false) Integer status) {
        return Result.success(userService.page(page, size, keyword, departmentId, role, status));
    }

    /**
     * 根据ID获取用户
     */
    @GetMapping("/{id}")
    public Result<User> getById(@PathVariable Long id) {
        User user = userService.getById(id);
        if (user == null) {
            return Result.error(404, "用户不存在");
        }
        // 不返回密码
        user.setPassword(null);
        return Result.success(user);
    }

    /**
     * 创建用户
     */
    @PostMapping
    public Result<Void> create(@RequestBody @Validated UserRequest request) {
        // 检查用户名是否已存在
        User existing = userService.findByUsername(request.getUsername());
        if (existing != null) {
            return Result.error(400, "用户名已存在");
        }
        
        User user = new User();
        user.setUsername(request.getUsername());
        user.setPassword(request.getPassword()); // 如果提供，会在service中加密
        user.setRealName(request.getRealName());
        user.setEmail(request.getEmail());
        user.setMobile(request.getMobile());
        user.setAvatar(request.getAvatar());
        user.setDepartmentId(request.getDepartmentId());
        user.setRole(request.getRole() != null ? request.getRole() : "student");
        user.setStatus(request.getStatus() != null ? request.getStatus() : 1);
        
        userService.save(user);
        return Result.success();
    }

    /**
     * 更新用户
     */
    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody @Validated UserRequest request) {
        User user = userService.getById(id);
        if (user == null) {
            return Result.error(404, "用户不存在");
        }
        
        // 如果用户名改变，检查新用户名是否已存在
        if (request.getUsername() != null && !request.getUsername().equals(user.getUsername())) {
            User existing = userService.findByUsername(request.getUsername());
            if (existing != null) {
                return Result.error(400, "用户名已存在");
            }
            user.setUsername(request.getUsername());
        }
        
        if (request.getRealName() != null) {
            user.setRealName(request.getRealName());
        }
        if (request.getEmail() != null) {
            user.setEmail(request.getEmail());
        }
        if (request.getMobile() != null) {
            user.setMobile(request.getMobile());
        }
        if (request.getAvatar() != null) {
            user.setAvatar(request.getAvatar());
        }
        if (request.getDepartmentId() != null) {
            user.setDepartmentId(request.getDepartmentId());
        }
        if (request.getRole() != null) {
            user.setRole(request.getRole());
        }
        if (request.getStatus() != null) {
            user.setStatus(request.getStatus());
        }
        
        userService.update(user);
        return Result.success();
    }

    /**
     * 删除用户
     */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        User user = userService.getById(id);
        if (user == null) {
            return Result.error(404, "用户不存在");
        }
        userService.delete(id);
        return Result.success();
    }

    /**
     * 重置用户密码
     */
    @PostMapping("/{id}/reset-password")
    public Result<Void> resetPassword(@PathVariable Long id, @RequestBody ResetPasswordRequest request) {
        User user = userService.getById(id);
        if (user == null) {
            return Result.error(404, "用户不存在");
        }
        
        // 这里可以添加权限检查，只有管理员才能重置密码
        userService.updatePassword(id, request.getPassword());
        return Result.success();
    }

    @Data
    public static class UserRequest {
        private String username;
        private String password;
        private String realName;
        private String email;
        private String mobile;
        private String avatar;
        private Long departmentId;
        private String role;
        private Integer status;
    }

    @Data
    public static class ResetPasswordRequest {
        @NotBlank(message = "新密码不能为空")
        private String password;
    }
}
