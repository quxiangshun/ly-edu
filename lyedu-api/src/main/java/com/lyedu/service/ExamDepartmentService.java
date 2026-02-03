package com.lyedu.service;

import java.util.List;

/** 考试-部门多对多关联服务 */
public interface ExamDepartmentService {

    List<Long> listDepartmentIdsByExamId(Long examId);

    void setExamDepartments(Long examId, List<Long> departmentIds);

    boolean examVisibleToDepartments(Long examId, List<Long> allowedDeptIds);
}
