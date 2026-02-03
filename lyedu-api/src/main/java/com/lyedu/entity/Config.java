package com.lyedu.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
public class Config extends BaseEntity {

    private String configKey;
    private String configValue;
    private String category;
    private String remark;
}
