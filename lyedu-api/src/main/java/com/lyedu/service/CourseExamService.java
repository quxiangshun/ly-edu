package com.lyedu.service;

/**
 * 课程-考试关联：一门课关联一场考试，一场考试可被多门课引用。
 * 课程可以不存在关联考试（正常数据，不报错）。
 */
public interface CourseExamService {

    /**
     * 根据课程ID查询关联的考试ID，无关联时返回 null。
     */
    Long getExamIdByCourseId(Long courseId);

    /**
     * 设置课程关联的考试；examId 为 null 时表示取消关联。
     */
    void setCourseExam(Long courseId, Long examId);
}
