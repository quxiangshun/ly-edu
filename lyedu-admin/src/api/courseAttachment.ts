import request from '@/utils/request'

export interface CourseAttachment {
  id: number
  courseId: number
  name: string
  type?: string
  fileUrl: string
  sort: number
  createTime?: string
  updateTime?: string
}

export const getAttachmentsByCourseId = (courseId: number) => {
  return request.get<CourseAttachment[]>('/course-attachment', { params: { courseId } })
}

export const createAttachment = (data: {
  courseId: number
  name: string
  type?: string
  fileUrl: string
  sort?: number
}) => {
  return request.post('/course-attachment', data)
}

export const deleteAttachment = (id: number) => {
  return request.delete(`/course-attachment/${id}`)
}
