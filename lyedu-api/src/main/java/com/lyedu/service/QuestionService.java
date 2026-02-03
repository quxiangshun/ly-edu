package com.lyedu.service;

import com.lyedu.common.PageResult;
import com.lyedu.entity.Question;

/**
 * 试题服务
 *
 * @author LyEdu Team
 */
public interface QuestionService {

    PageResult<Question> page(Integer page, Integer size, String keyword, String type);

    Question getById(Long id);

    long save(Question question);

    void update(Question question);

    void delete(Long id);
}
