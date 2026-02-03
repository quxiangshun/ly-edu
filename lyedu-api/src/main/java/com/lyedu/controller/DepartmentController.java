package com.lyedu.controller;

import com.lyedu.common.Result;
import com.lyedu.entity.Course;
import com.lyedu.entity.Department;
import com.lyedu.service.CourseDepartmentService;
import com.lyedu.service.CourseService;
import com.lyedu.service.DepartmentService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 部门管理控制器（部门可关联多个课程）
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/department")
@RequiredArgsConstructor
public class DepartmentController {

    private final DepartmentService departmentService;
    private final CourseDepartmentService courseDepartmentService;
    private final CourseService courseService;

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

    /**
     * 获取部门关联的课程列表
     */
    @GetMapping("/{id}/courses")
    public Result<List<Course>> listCoursesByDepartmentId(@PathVariable Long id) {
        Department department = departmentService.getById(id);
        if (department == null) {
            return Result.error(404, "部门不存在");
        }
        List<Long> courseIds = courseDepartmentService.listCourseIdsByDepartmentId(id);
        if (courseIds == null || courseIds.isEmpty()) {
            return Result.success(Collections.emptyList());
        }
        List<Course> list = courseIds.stream()
                .map(cid -> courseService.getByIdIgnoreVisibility(cid))
                .filter(c -> c != null)
                .collect(Collectors.toList());
        return Result.success(list);
    }

    /**
     * 为部门批量添加课程关联
     */
    @PostMapping("/{id}/courses")
    public Result<Void> addCoursesToDepartment(@PathVariable Long id, @RequestBody DepartmentCoursesRequest request) {
        Department department = departmentService.getById(id);
        if (department == null) {
            return Result.error(404, "部门不存在");
        }
        if (request.getCourseIds() != null && !request.getCourseIds().isEmpty()) {
            courseDepartmentService.addCoursesToDepartment(id, request.getCourseIds());
        }
        return Result.success();
    }

    /**
     * 移除部门与课程的关联
     */
    @DeleteMapping("/{id}/courses/{courseId}")
    public Result<Void> removeCourseFromDepartment(@PathVariable Long id, @PathVariable Long courseId) {
        Department department = departmentService.getById(id);
        if (department == null) {
            return Result.error(404, "部门不存在");
        }
        courseDepartmentService.removeCourseFromDepartment(id, courseId);
        return Result.success();
    }

    @Data
    public static class DepartmentCoursesRequest {
        private List<Long> courseIds;
    }

    @Data
    public static class DepartmentRequest {
        private String name;
        private Long parentId;
        private Integer sort;
        private Integer status;
    }
}
