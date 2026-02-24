package com.lyedu.controller;

import com.lyedu.common.Result;
import com.lyedu.entity.Department;
import com.lyedu.service.DepartmentService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 部门管理控制器
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/department")
@RequiredArgsConstructor
public class DepartmentController {

    private final DepartmentService departmentService;

    /**
     * 获取部门树形列表
     */
    @GetMapping("/tree")
    public Result<List<Department>> tree() {
        return Result.success(departmentService.listTree());
    }

    /**
     * 根据ID获取部门
     */
    @GetMapping("/{id}")
    public Result<Department> getById(@PathVariable Long id) {
        Department department = departmentService.getById(id);
        if (department == null) {
            return Result.error(404, "部门不存在");
        }
        return Result.success(department);
    }

    /**
     * 创建部门
     */
    @PostMapping
    public Result<Void> create(@RequestBody DepartmentRequest request) {
        Department department = new Department();
        department.setName(request.getName());
        department.setParentId(request.getParentId());
        department.setSort(request.getSort());
        department.setStatus(request.getStatus());
        departmentService.save(department);
        return Result.success();
    }

    /**
     * 更新部门
     */
    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody DepartmentRequest request) {
        Department department = departmentService.getById(id);
        if (department == null) {
            return Result.error(404, "部门不存在");
        }
        department.setName(request.getName());
        department.setParentId(request.getParentId());
        department.setSort(request.getSort());
        department.setStatus(request.getStatus());
        departmentService.update(department);
        return Result.success();
    }

    /**
     * 删除部门
     */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        departmentService.delete(id);
        return Result.success();
    }

    @Data
    public static class DepartmentRequest {
        private String name;
        private Long parentId;
        private Integer sort;
        private Integer status;
    }
}
