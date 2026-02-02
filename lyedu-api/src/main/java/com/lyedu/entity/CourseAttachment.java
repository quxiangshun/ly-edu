package com.lyedu.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 课程附件实体
 *
 * @author LyEdu Team
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class CourseAttachment extends BaseEntity {

    /**
     * 课程ID
     */
    private Long courseId;

    /**
     * 附件名称
     */
    private String name;

    /**
     * 附件类型/扩展名
     */
    private String type;

    /**
     * 文件地址
     */
    private String fileUrl;

    /**
     * 排序
     */
    private Integer sort;
}
