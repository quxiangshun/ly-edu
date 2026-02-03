package com.lyedu.service;

import java.util.List;
import java.util.Map;

/**
 * 数据统计与导出服务
 */
public interface StatsService {

    /**
     * 概览数字：学员数、课程数、部门数、视频数
     */
    Map<String, Long> overview();

    /**
     * 学习排行：按已学课程数或总进度排序，返回前 limit 条（含用户名、部门、课程数、总进度等）
     */
    List<Map<String, Object>> learningRank(int limit);

    /**
     * 资源统计：课程数、视频数、章节数、附件数等
     */
    Map<String, Long> resourceStats();

    /**
     * 学员信息导出：返回表头 + 行数据（用于生成 CSV）
     */
    List<Map<String, Object>> exportLearners();

    /**
     * 学习记录导出：用户、课程、进度、状态等
     */
    List<Map<String, Object>> exportLearning();

    /**
     * 部门学习统计导出：部门、学习人数、完成人数等
     */
    List<Map<String, Object>> exportDepartmentLearning();
}
