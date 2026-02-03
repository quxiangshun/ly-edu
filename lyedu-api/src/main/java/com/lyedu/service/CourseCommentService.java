package com.lyedu.service;

import com.lyedu.common.CourseCommentDto;
import com.lyedu.entity.CourseComment;

import java.util.List;

/**
 * 课程评论服务
 */
public interface CourseCommentService {

    /**
     * 按课程（及可选章节）查询评论列表，按时间正序；含评论人姓名
     */
    List<CourseCommentDto> listByCourse(Long courseId, Long chapterId);

    /**
     * 发表评论或回复
     */
    CourseComment add(Long courseId, Long chapterId, Long userId, Long parentId, String content);

    /**
     * 软删除（管理员或本人）
     */
    void delete(Long id);
}
