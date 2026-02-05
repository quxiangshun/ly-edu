import request from '@/utils/request'

export interface CourseComment {
  id: number
  courseId: number
  courseTitle?: string
  chapterId?: number
  userId: number
  userRealName?: string
  username?: string
  parentId?: number
  content: string
  status: number
  deleted: number
  createTime?: string
}

export interface PageResult<T> {
  records: T[]
  total: number
}

export const getCommentPage = (params: {
  page: number
  size: number
  keyword?: string
  courseId?: number
  status?: number
}) => {
  return request.get<PageResult<CourseComment>>('/course-comment/page', { params })
}

export const getCommentById = (id: number) => {
  return request.get<CourseComment>(`/course-comment/${id}`)
}

export const deleteComment = (id: number) => {
  return request.delete(`/course-comment/${id}`)
}

export const updateCommentStatus = (id: number, status: number) => {
  return request.put(`/course-comment/${id}/status?status=${status}`)
}
