import request from '@/utils/request'

export interface Chapter {
  id: number
  courseId: number
  title: string
  sort: number
  createTime?: string
  updateTime?: string
}

export const getChaptersByCourseId = (courseId: number) => {
  return request.get<Chapter[]>('/chapter', { params: { courseId } })
}

export const createChapter = (data: { courseId: number; title: string; sort?: number }) => {
  return request.post<number>('/chapter', data)
}

export const updateChapter = (id: number, data: { title: string; sort?: number }) => {
  return request.put(`/chapter/${id}`, data)
}

export const deleteChapter = (id: number) => {
  return request.delete(`/chapter/${id}`)
}
