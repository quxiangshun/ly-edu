import request from '@/utils/request'

export interface Knowledge {
  id: number
  title: string
  category?: string
  fileName?: string
  fileUrl: string
  fileSize?: number
  fileType?: string
  sort: number
  /** 可见性：1-公开，0-私有 */
  visibility: number
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

export const getKnowledgePage = (params: {
  page: number
  size: number
  keyword?: string
  category?: string
}) => {
  return request.get<PageResult<Knowledge>>('/knowledge/page', { params })
}

export const getKnowledgeByIdAdmin = (id: number) => {
  return request.get<Knowledge>(`/knowledge/admin/${id}`)
}

export const createKnowledge = (data: {
  title: string
  category?: string
  fileName?: string
  fileUrl: string
  fileSize?: number
  fileType?: string
  sort?: number
  visibility?: number
  departmentIds?: number[]
}) => {
  return request.post<number>('/knowledge', data)
}

export const updateKnowledge = (id: number, data: {
  title: string
  category?: string
  fileName?: string
  fileUrl: string
  fileSize?: number
  fileType?: string
  sort?: number
  visibility?: number
  departmentIds?: number[]
}) => {
  return request.put(`/knowledge/${id}`, data)
}

export const deleteKnowledge = (id: number) => {
  return request.delete(`/knowledge/${id}`)
}
