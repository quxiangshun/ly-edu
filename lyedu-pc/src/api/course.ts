import request from '@/utils/request'

export interface Course {
  id: number
  title: string
  cover?: string
  description?: string
  categoryId?: number
  status: number
  sort: number
  /** 是否必修：0-选修，1-必修 */
  isRequired?: number
}

export interface Video {
  id: number
  courseId: number
  chapterId?: number
  title: string
  url: string
  duration?: number
  sort: number
}

export interface ChapterItem {
  id: number | null
  title: string
  sort: number
  hours: Video[]
}

export interface LearnRecordItem {
  progress: number
  duration: number
}

export interface CourseAttachment {
  id: number
  courseId: number
  name: string
  type?: string
  fileUrl: string
  sort: number
}

export interface CourseDetail {
  course: Course
  videos: Video[]
  chapters?: ChapterItem[]
  learnRecord?: Record<string, LearnRecordItem>
  courseProgress?: number
  attachments?: CourseAttachment[]
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
  return request.get<CourseDetail>(`/course/${id}`)
}

export const getRecommendedCourses = (limit: number = 6) => {
  return request.get<Course[]>('/course/recommended', { params: { limit } })
}
