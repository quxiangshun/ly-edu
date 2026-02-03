package com.lyedu.service;

import com.lyedu.entity.ExamRecord;

import java.util.List;

/**
 * 考试记录服务
 *
 * @author LyEdu Team
 */
public interface ExamRecordService {

    /** 交卷：计算得分、是否及格，保存记录 */
    ExamRecord submit(Long examId, Long userId, String answersJson);

    /** 某考试下的所有记录（管理端） */
    List<ExamRecord> listByExamId(Long examId);

    /** 某用户的考试记录 */
    List<ExamRecord> listByUserId(Long userId);

    /** 某用户某考试的记录（是否已考过） */
    ExamRecord getByExamAndUser(Long examId, Long userId);
}
