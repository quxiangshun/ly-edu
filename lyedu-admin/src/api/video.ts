import request from '@/utils/request'

export interface Video {
  id: number
  courseId: number
  chapterId?: number
  courseName?: string
  chapterName?: string
  title: string
  url: string
  cover?: string
  duration?: number
  sort: number
  playCount?: number
  likeCount?: number
}

export interface PageResult<T> {
  records: T[]
  total: number
  current: number
  size: number
  pages: number
}

export const getVideoPage = (params: {
  page: number
  size: number
  courseId?: number
  keyword?: string
}) => {
  return request.get<PageResult<Video>>('/video/page', { params })
}

export const getVideoById = (id: number) => {
  return request.get<Video>(`/video/${id}`)
}

export const createVideo = (data: Partial<Video>) => {
  return request.post('/video', data)
}

export const updateVideo = (id: number, data: Partial<Video>) => {
  return request.put(`/video/${id}`, data)
}

export const deleteVideo = (id: number) => {
  return request.delete(`/video/${id}`)
}

export const getVideosByCourseId = (courseId: number) => {
  return request.get<Video[]>(`/video/course/${courseId}`)
}

export const getVideosByChapterId = (chapterId: number) => {
  return request.get<Video[]>(`/video/chapter/${chapterId}`)
}

