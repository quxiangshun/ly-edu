package com.lyedu.service;

import com.lyedu.common.PageResult;
import com.lyedu.common.PaperQuestionDto;
import com.lyedu.entity.Paper;

import java.util.List;

/**
 * 试卷服务
 *
 * @author LyEdu Team
 */
public interface PaperService {

    PageResult<Paper> page(Integer page, Integer size, String keyword);

    Paper getById(Long id);

    /** 根据试卷ID获取题目列表（含题目详情、分值、顺序，用于考试作答） */
    List<PaperQuestionDto> listQuestionsByPaperId(Long paperId);

    long save(Paper paper);

    void update(Paper paper);

    void delete(Long id);
}
