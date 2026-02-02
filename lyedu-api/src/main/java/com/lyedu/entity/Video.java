package com.lyedu.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 视频实体
 *
 * @author LyEdu Team
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class Video extends BaseEntity {

    /**
     * 课程ID
     */
    private Long courseId;

    /**
     * 章节ID
     */
    private Long chapterId;

    /**
     * 课程名称（展示用，非表字段）
     */
    private String courseName;

    /**
     * 章节名称（展示用，非表字段）
     */
    private String chapterName;

    /**
     * 视频标题
     */
    private String title;

    /**
     * 视频地址
     */
    private String url;

    /**
     * 视频时长（秒）
     */
    private Integer duration;

    /**
     * 排序
     */
    private Integer sort;
}
