package com.lyedu.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

import java.util.List;

/**
 * 知识库实体
 *
 * @author LyEdu Team
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class Knowledge extends BaseEntity {

    /**
     * 标题/名称
     */
    private String title;

    /**
     * 分类（如：制度文档、技术文档）
     */
    private String category;

    /**
     * 文件名
     */
    private String fileName;

    /**
     * 文件地址
     */
    private String fileUrl;

    /**
     * 文件大小（字节）
     */
    private Long fileSize;

    /**
     * 文件类型/扩展名
     */
    private String fileType;

    /**
     * 排序
     */
    private Integer sort;

    /**
     * 可见性：1-公开，0-私有（按部门）
     */
    private Integer visibility;

    /**
     * 关联部门ID列表（私有时；不持久化到 ly_knowledge，来自 ly_knowledge_department）
     */
    private List<Long> departmentIds;
}
