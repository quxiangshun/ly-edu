package com.lyedu.common;

import com.lyedu.entity.Task;
import com.lyedu.entity.UserTask;
import lombok.Data;

import java.io.Serializable;

/**
 * 任务 + 用户进度（我的任务列表项）
 *
 * @author LyEdu Team
 */
@Data
public class TaskWithUserProgressDto implements Serializable {

    private static final long serialVersionUID = 1L;

    private Task task;
    private UserTask userTask;
}
