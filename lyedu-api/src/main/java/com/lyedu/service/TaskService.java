package com.lyedu.service;

import com.lyedu.common.PageResult;
import com.lyedu.entity.Task;

/**
 * 周期任务服务
 *
 * @author LyEdu Team
 */
public interface TaskService {

    /** 分页列表（带用户部门可见性；管理员可见全部） */
    PageResult<Task> page(Integer page, Integer size, String keyword, Long userId);

    Task getById(Long id, Long userId);

    Task getByIdIgnoreVisibility(Long id);

    long save(Task task);

    void update(Task task);

    void delete(Long id);
}
