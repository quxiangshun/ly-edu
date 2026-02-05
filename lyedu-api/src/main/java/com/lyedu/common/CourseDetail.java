package com.lyedu.common;

import com.lyedu.entity.Course;
import com.lyedu.entity.CourseAttachment;
import com.lyedu.entity.Video;
import lombok.Data;

import java.io.Serializable;
import java.util.List;
import java.util.Map;

/**
 * 课程详情（包含章节/课时、视频列表、学习记录、进度）
 *
 * @author LyEdu Team
 */
@Data
public class CourseDetail implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 课程信息
     */
    private Course course;

    /**
     * 视频列表（扁平，兼容旧端）
     */
    private List<Video> videos;

    /**
     * 章节列表（每章节下为课时/视频）
     */
    private List<ChapterItem> chapters;

    /**
     * 学员课时学习记录：videoId -> { progress(秒), duration(秒) }
     */
    private Map<Long, LearnRecordItem> learnRecord;

    /**
     * 课程学习进度百分比（0-100），仅登录后有值
     */
    private Integer courseProgress;

    /**
     * 课程附件列表
     */
    private List<CourseAttachment> attachments;

    /**
     * 关联的考试ID，无关联时为 null（正常，一个课程可以不存在考试）
     */
    private Long examId;

    @Data
    public static class ChapterItem implements Serializable {
        private static final long serialVersionUID = 1L;
        private Long id;
        private String title;
        private Integer sort;
        private List<Video> hours;
    }

    @Data
    public static class LearnRecordItem implements Serializable {
        private static final long serialVersionUID = 1L;
        private Integer progress;
        private Integer duration;
    }
}
