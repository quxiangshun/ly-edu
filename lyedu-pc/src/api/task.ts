import request from '@/utils/request'

export interface Task {
  id: number
  title: string
  description?: string
  cycleType: string
  cycleConfig?: string
  items: string
  certificateId?: number
  sort: number
  status: number
  startTime?: string
  endTime?: string
}

export const getTaskPage = (params: { page: number; size: number; keyword?: string }) => {
  return request.get('/task/page', { params })
}

export const getTaskById = (id: number) => {
  return request.get<Task>('/task/' + id)
}
