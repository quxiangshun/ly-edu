package com.lyedu.service;

import com.lyedu.common.PageResult;
import com.lyedu.entity.Exam;

/**
 * 考试任务服务
 *
 * @author LyEdu Team
 */
public interface ExamService {

    /** 分页列表（带用户部门可见性；管理员可见全部） */
    PageResult<Exam> page(Integer page, Integer size, String keyword, Long userId);

    Exam getById(Long id, Long userId);

    Exam getByIdIgnoreVisibility(Long id);

    long save(Exam exam);

    void update(Exam exam);

    void delete(Long id);
}
