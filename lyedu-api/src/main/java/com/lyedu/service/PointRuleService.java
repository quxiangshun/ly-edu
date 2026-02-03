package com.lyedu.service;

import com.lyedu.entity.PointRule;

import java.util.List;

/**
 * 积分规则服务
 *
 * @author LyEdu Team
 */
public interface PointRuleService {

    List<PointRule> listAll();

    PointRule getByKey(String ruleKey);

    void update(String ruleKey, String ruleName, Integer points, Integer enabled, String remark);
}
