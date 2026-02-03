package com.lyedu.service;

import com.lyedu.common.TaskWithUserProgressDto;
import com.lyedu.entity.Task;
import com.lyedu.entity.UserTask;

import java.util.List;

/**
 * 用户任务进度服务（闯关进度、完成时颁发证书）
 *
 * @author LyEdu Team
 */
public interface UserTaskService {

    /** 当前用户可见的任务列表（含进度/完成状态） */
    List<TaskWithUserProgressDto> listMyTasks(Long userId);

    /** 获取任务详情（含用户进度，仅可见任务） */
    Task getTaskDetail(Long taskId, Long userId);

    /** 获取或创建用户任务记录，返回用户任务进度 */
    UserTask getOrCreateUserTask(Long taskId, Long userId);

    /** 更新进度；若全部完成则标记完成并颁发证书 */
    UserTask updateProgress(Long taskId, Long userId, String progressJson);
}
