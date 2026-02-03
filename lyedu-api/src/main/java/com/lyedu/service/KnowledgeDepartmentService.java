package com.lyedu.service;

import java.util.List;

/** 知识库-部门多对多关联服务 */
public interface KnowledgeDepartmentService {

    List<Long> listDepartmentIdsByKnowledgeId(Long knowledgeId);

    void setKnowledgeDepartments(Long knowledgeId, List<Long> departmentIds);

    boolean knowledgeVisibleToDepartments(Long knowledgeId, List<Long> allowedDeptIds);
}
