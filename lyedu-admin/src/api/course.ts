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
  /** 可见性：1-公开，0-私有 */
  visibility?: number
  /** 关联部门ID列表（私有时必填，可多选） */
  departmentIds?: number[]
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
