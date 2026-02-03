import request from '@/utils/request'

export interface Exam {
  id: number
  title: string
  paperId: number
  startTime?: string
  endTime?: string
  durationMinutes?: number
  passScore?: number
  visibility: number
  status: number
  departmentIds?: number[]
  createTime?: string
  updateTime?: string
}

export interface ExamRecord {
  id: number
  examId: number
  userId: number
  paperId: number
  score?: number
  passed?: number
  answers?: string
  submitTime?: string
  createTime?: string
}

export interface PageResult<T> {
  records: T[]
  total: number
  current: number
  size: number
  pages: number
}

export const getExamPage = (params: { page: number; size: number; keyword?: string }) => {
  return request.get<PageResult<Exam>>('/exam/page', { params })
}

export const getExamById = (id: number) => {
  return request.get<Exam>(`/exam/${id}`)
}

export const getExamByIdAdmin = (id: number) => {
  return request.get<Exam>(`/exam/admin/${id}`)
}

export const createExam = (data: Partial<Exam> & { paperId: number }) => {
  return request.post<number>('/exam', data)
}

export const updateExam = (id: number, data: Partial<Exam> & { paperId: number }) => {
  return request.put(`/exam/${id}`, data)
}

export const deleteExam = (id: number) => {
  return request.delete(`/exam/${id}`)
}

export const getExamRecords = (examId: number) => {
  return request.get<ExamRecord[]>(`/exam-record/exam/${examId}`)
}
