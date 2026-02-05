import request from '@/utils/request'

export interface UserLearningRecord {
  userId: number
  realName?: string
  username?: string
  courseId: number
  courseTitle?: string
  progress: number
  completeStatus: number
  joinTime?: string
  updateTime?: string
}

export interface PageResult<T> {
  records: T[]
  total: number
}

export const getUserLearningPage = (params: {
  page: number
  size: number
  keyword?: string
  userId?: number
  courseId?: number
}) => {
  return request.get<PageResult<UserLearningRecord>>('/stats/learning/page', { params })
}

export const getUserLearningList = (params?: {
  userId?: number
  courseId?: number
}) => {
  return request.get<UserLearningRecord[]>('/stats/export/learning', { params })
}
