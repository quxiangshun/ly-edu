import request from '@/utils/request'

export interface UserTask {
  id: number
  userId: number
  realName?: string
  username?: string
  taskId: number
  taskTitle?: string
  progress?: string
  status: number
  completedAt?: string
  createTime?: string
  updateTime?: string
}

export interface PageResult<T> {
  records: T[]
  total: number
}

export const getUserTaskPage = (params: {
  page: number
  size: number
  keyword?: string
  userId?: number
  taskId?: number
}) => {
  return request.get<PageResult<UserTask>>('/user-task/page', { params })
}
