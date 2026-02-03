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
  departmentIds?: number[]
  createTime?: string
  updateTime?: string
}

export interface PageResult<T> {
  records: T[]
  total: number
  current: number
  size: number
  pages: number
}

export const getTaskPage = (params: { page: number; size: number; keyword?: string }) => {
  return request.get<PageResult<Task>>('/task/page', { params })
}

export const getTaskById = (id: number) => {
  return request.get<Task>(`/task/${id}`)
}

export const getTaskByIdAdmin = (id: number) => {
  return request.get<Task>(`/task/admin/${id}`)
}

export const createTask = (data: Partial<Task>) => {
  return request.post<number>('/task', data)
}

export const updateTask = (id: number, data: Partial<Task>) => {
  return request.put(`/task/${id}`, data)
}

export const deleteTask = (id: number) => {
  return request.delete(`/task/${id}`)
}
