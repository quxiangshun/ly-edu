import request from '@/utils/request'

export interface AttachmentUploadResult {
  url: string
  path: string
  fileName: string
  fileSize: number
  fileType: string
  /** 是否已写入知识库，false 表示知识库表未初始化 */
  knowledgeSaved?: boolean
  /** 知识库记录 ID，用于课程附件关联 */
  knowledgeId?: number
}

export const uploadAttachment = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  // 复用知识库上传接口（同 file_service），避免代理对 course-attachment/upload 的 405
  return request.post<AttachmentUploadResult>('/knowledge/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export interface CourseAttachment {
  id: number
  courseId: number
  knowledgeId: number
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
  knowledgeId: number
  sort?: number
}) => {
  return request.post('/course-attachment', data)
}

export const deleteAttachment = (id: number) => {
  return request.delete(`/course-attachment/${id}`)
}
