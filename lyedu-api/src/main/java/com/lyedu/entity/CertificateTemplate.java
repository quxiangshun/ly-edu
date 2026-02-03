package com.lyedu.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 证书模板实体
 *
 * @author LyEdu Team
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class CertificateTemplate extends BaseEntity {

    /** 模板名称 */
    private String name;
    /** 说明 */
    private String description;
    /** 模板配置 JSON（占位符、样式等） */
    private String config;
    /** 排序 */
    private Integer sort;
    /** 状态：0-禁用，1-启用 */
    private Integer status;
}
