import request from '@/utils/request'
import type { Task } from '@/api/task'

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
  task: Task
  userTask: UserTask | null
}

export const getMyTasks = () => {
  return request.get<TaskWithUserProgress[]>('/user-task/my')
}

export const getTaskDetail = (taskId: number) => {
  return request.get<Task>(`/user-task/task/${taskId}`)
}

export const getOrCreateProgress = (taskId: number) => {
  return request.get<UserTask>(`/user-task/task/${taskId}/progress`)
}

export const updateProgress = (taskId: number, progress: string) => {
  return request.post<UserTask>(`/user-task/task/${taskId}/progress`, { progress })
}
