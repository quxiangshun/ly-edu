package com.lyedu.service;

import java.util.List;

/** 课程-部门多对多关联服务 */
public interface CourseDepartmentService {

    List<Long> listDepartmentIdsByCourseId(Long courseId);

    void setCourseDepartments(Long courseId, List<Long> departmentIds);

    List<Long> listCourseIdsByDepartmentId(Long departmentId);

    void addCoursesToDepartment(Long departmentId, List<Long> courseIds);

    void removeCourseFromDepartment(Long departmentId, Long courseId);

    boolean courseVisibleToDepartments(Long courseId, List<Long> allowedDeptIds);
}
