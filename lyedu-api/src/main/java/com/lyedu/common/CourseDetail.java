package com.lyedu.common;

import com.lyedu.entity.Course;
import com.lyedu.entity.Video;
import lombok.Data;

import java.io.Serializable;
import java.util.List;

/**
 * 课程详情（包含视频列表）
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
     * 视频列表
     */
    private List<Video> videos;
}
