package com.lyedu.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

/**
 * 积分规则实体
 *
 * @author LyEdu Team
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class PointRule extends BaseEntity {

    /**
     * 规则键：course_finish, exam_pass, task_finish
     */
    private String ruleKey;

    /**
     * 规则名称
     */
    private String ruleName;

    /**
     * 奖励积分
     */
    private Integer points;

    /**
     * 是否启用：0-否，1-是
     */
    private Integer enabled;

    /**
     * 备注
     */
    private String remark;
}
