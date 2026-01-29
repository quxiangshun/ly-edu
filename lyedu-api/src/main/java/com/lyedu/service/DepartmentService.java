package com.lyedu.service;

import com.lyedu.entity.Department;

import java.util.List;

/**
 * 部门服务接口
 *
 * @author LyEdu Team
 */
public interface DepartmentService {

    /**
     * 获取所有部门（树形结构）
     */
    List<Department> listTree();

    /**
     * 根据ID获取部门
     */
    Department getById(Long id);

    /**
     * 保存部门
     */
    void save(Department department);

    /**
     * 更新部门
     */
    void update(Department department);

    /**
     * 删除部门
     */
    void delete(Long id);
}
