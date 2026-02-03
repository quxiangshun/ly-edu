package com.lyedu.service;

import com.lyedu.entity.PointLog;

import java.util.List;
import java.util.Map;

/**
 * 积分服务：发放积分、查询我的积分与流水、排行
 *
 * @author LyEdu Team
 */
public interface PointService {

    /**
     * 按规则发放积分（同一 ref 只发一次）
     *
     * @param userId  用户ID
     * @param ruleKey 规则键：course_finish, exam_pass, task_finish
     * @param refType 关联类型：course, exam, task
     * @param refId   关联ID
     * @return 本次发放的积分，未发放返回 0
     */
    int addPoints(Long userId, String ruleKey, String refType, Long refId);

    /**
     * 用户当前总积分
     */
    int getTotalPoints(Long userId);

    /**
     * 我的积分流水（分页）
     */
    List<PointLog> listMyLog(Long userId, int page, int size);

    /**
     * 积分排行（按 total_points 降序，支持部门筛选）
     *
     * @param limit        返回条数
     * @param departmentId 可选部门ID，null 表示全站
     * @return 列表项含 userId, realName, username, totalPoints, rank
     */
    List<Map<String, Object>> listRanking(int limit, Long departmentId);
}
