package com.lyedu.service;

import com.lyedu.common.PageResult;
import com.lyedu.entity.Knowledge;

/**
 * 知识库服务
 *
 * @author LyEdu Team
 */
public interface KnowledgeService {

    /**
     * 分页列表（带 Authorization 时按用户部门过滤可见性；管理员可见全部）
     */
    PageResult<Knowledge> page(Integer page, Integer size, String keyword, String category, Long userId);

    /**
     * 根据ID获取（带可见性校验）
     */
    Knowledge getById(Long id, Long userId);

    /**
     * 根据ID获取（忽略可见性，管理端用）
     */
    Knowledge getByIdIgnoreVisibility(Long id);

    /**
     * 新增
     */
    long save(Knowledge knowledge);

    /**
     * 更新
     */
    void update(Knowledge knowledge);

    /**
     * 删除（软删）
     */
    void delete(Long id);
}
