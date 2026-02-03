package com.lyedu.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 证书颁发规则实体（关联考试/任务，合格后颁发）
 *
 * @author LyEdu Team
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class Certificate extends BaseEntity {

    /** 证书模板ID */
    private Long templateId;
    /** 证书名称（如：Java 考试合格证） */
    private String name;
    /** 来源类型：exam-考试，task-任务 */
    private String sourceType;
    /** 来源ID（考试ID或任务ID） */
    private Long sourceId;
    /** 排序 */
    private Integer sort;
    /** 状态：0-禁用，1-启用 */
    private Integer status;
}
