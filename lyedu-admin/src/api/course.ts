import request from '@/utils/request'

export interface Course {
  id: number
  title: string
  cover?: string
  description?: string
  categoryId?: number
  status: number
  sort: number
  isRequired?: number
  /** 标签ID列表 */
  tagIds?: number[]
  /** 视频播放总和（v4 迁移后） */
  playCount?: number
  /** 视频点赞总和（v4 迁移后） */
  likeCount?: number
  /** 课程评论数（v4 迁移后） */
  commentCount?: number
}

export interface PageResult<T> {
  records: T[]
  total: number
  current: number
  size: number
  pages: number
}

export const getCoursePage = (params: { page: number; size: number; keyword?: string; categoryId?: number }) => {
  return request.get<PageResult<Course>>('/course/page', { params })
}

export const getCourseById = (id: number) => {
  return request.get<Course>(`/course/${id}`)
}

export const createCourse = (data: Partial<Course>) => {
  return request.post('/course', data)
}

export const updateCourse = (id: number, data: Partial<Course>) => {
  return request.put(`/course/${id}`, data)
}

export const deleteCourse = (id: number) => {
  return request.delete(`/course/${id}`)
}

export const getRecommendedCourses = (limit: number = 6) => {
  return request.get<Course[]>('/course/recommended', { params: { limit } })
}

/** 课程关联考试（单个）；无关联时返回 null，属正常不报错 */
export const getCourseExam = (id: number) => {
  return request
    .get<number | null>(`/course/${id}/exam`, { silentError: true } as any)
    .catch(() => null as number | null)
}

export const setCourseExam = (id: number, examId: number | null) => {
  return request.put(`/course/${id}/exam`, { examId })
}
