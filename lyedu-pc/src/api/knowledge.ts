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
  visibility: number
  createTime?: string
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

export const getKnowledgeById = (id: number) => {
  return request.get<Knowledge>(`/knowledge/${id}`)
}
