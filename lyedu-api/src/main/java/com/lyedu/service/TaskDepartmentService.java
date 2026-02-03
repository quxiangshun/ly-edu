package com.lyedu.service;

import java.util.List;

/** 任务-部门多对多关联服务 */
public interface TaskDepartmentService {

    List<Long> listDepartmentIdsByTaskId(Long taskId);

    void setTaskDepartments(Long taskId, List<Long> departmentIds);

    boolean taskVisibleToDepartments(Long taskId, List<Long> allowedDeptIds);
}
