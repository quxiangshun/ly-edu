package com.lyedu.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 周期任务实体
 *
 * @author LyEdu Team
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class Task extends BaseEntity {

    private String title;
    private String description;
    /** 周期：once/daily/weekly/monthly */
    private String cycleType;
    /** 周期配置 JSON */
    private String cycleConfig;
    /** 闯关项 JSON：[{"type":"course","id":1},{"type":"exam","id":2}] */
    private String items;
    /** 完成后颁发证书规则ID */
    private Long certificateId;
    private Integer sort;
    /** 状态：0-禁用，1-启用 */
    private Integer status;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    /** 关联部门ID列表，来自 ly_task_department */
    private List<Long> departmentIds;
}
