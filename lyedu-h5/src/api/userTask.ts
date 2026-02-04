import request from '@/utils/request'

export interface UserTask {
  id: number
  userId: number
  taskId: number
  progress?: string
  status: number
  completedAt?: string
  createTime?: string
  updateTime?: string
}

export interface TaskWithUserProgress {
  task: { id: number; title?: string; [key: string]: unknown }
  userTask: UserTask | null
}

export const getMyTasks = () => request.get<TaskWithUserProgress[]>('/user-task/my')

export const getTaskDetail = (taskId: number) =>
  request.get<{ id: number; title?: string; description?: string; [key: string]: unknown }>(`/user-task/task/${taskId}`)
