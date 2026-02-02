package com.lyedu.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

import java.util.List;

/**
 * 部门实体（支持多级树形）
 *
 * @author LyEdu Team
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class Department extends BaseEntity {

    /**
     * 部门名称
     */
    private String name;

    /**
     * 父部门ID（0 表示根级）
     */
    private Long parentId;

    /**
     * 排序
     */
    private Integer sort;

    /**
     * 状态（0-禁用，1-启用）
     */
    private Integer status;

    /**
     * 子部门列表（树形展示用，非表字段）
     */
    private List<Department> children;
}
