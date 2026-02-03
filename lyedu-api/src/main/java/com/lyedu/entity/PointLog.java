package com.lyedu.entity;

import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 积分流水实体
 *
 * @author LyEdu Team
 */
@Data
public class PointLog implements Serializable {

    private static final long serialVersionUID = 1L;

    private Long id;
    private Long userId;
    private Integer points;
    private String ruleKey;
    private String refType;
    private Long refId;
    private String remark;
    private LocalDateTime createTime;
}
