package com.lyedu.controller;

import com.lyedu.common.Result;
import com.lyedu.entity.PointRule;
import com.lyedu.service.PointRuleService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 积分规则管理（管理后台）
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/point-rule")
@RequiredArgsConstructor
public class PointRuleController {

    private final PointRuleService pointRuleService;

    @GetMapping("/list")
    public Result<List<PointRule>> list() {
        return Result.success(pointRuleService.listAll());
    }

    @PutMapping("/update")
    public Result<Void> update(@RequestBody PointRuleUpdateRequest body) {
        if (body == null || body.getRuleKey() == null || body.getRuleKey().isBlank()) {
            return Result.error(com.lyedu.common.ResultCode.PARAM_ERROR);
        }
        pointRuleService.update(body.getRuleKey(), body.getRuleName(), body.getPoints(), body.getEnabled(), body.getRemark());
        return Result.success();
    }

    @Data
    public static class PointRuleUpdateRequest {
        private String ruleKey;
        private String ruleName;
        private Integer points;
        private Integer enabled;
        private String remark;
    }
}
