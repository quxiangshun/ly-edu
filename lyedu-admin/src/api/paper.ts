import request from '@/utils/request'

export interface Paper {
  id: number
  title: string
  totalScore: number
  passScore: number
  durationMinutes: number
  status: number
  createTime?: string
  updateTime?: string
}

export interface PaperQuestionItem {
  questionId?: number
  score?: number
  sort?: number
  /** 新建题目时使用，与试题管理字段一致 */
  type?: string
  title?: string
  options?: string
  answer?: string
  analysis?: string
}

export interface PaperQuestionDto {
  questionId: number
  score: number
  sort: number
  question?: import('@/api/question').Question
}

export interface PageResult<T> {
  records: T[]
  total: number
  current: number
  size: number
  pages: number
}

export const getPaperPage = (params: { page: number; size: number; keyword?: string }) => {
  return request.get<PageResult<Paper>>('/paper/page', { params })
}

export const getPaperById = (id: number) => {
  return request.get<Paper>(`/paper/${id}`)
}

export const getPaperQuestions = (id: number) => {
  return request.get<PaperQuestionDto[]>(`/paper/${id}/questions`)
}

export const createPaper = (data: {
  title: string
  totalScore?: number
  passScore?: number
  durationMinutes?: number
  status?: number
  questions?: PaperQuestionItem[]
}) => {
  return request.post<number>('/paper', data)
}

export const updatePaper = (id: number, data: {
  title: string
  totalScore?: number
  passScore?: number
  durationMinutes?: number
  status?: number
  questions?: PaperQuestionItem[]
}) => {
  return request.put(`/paper/${id}`, data)
}

export const deletePaper = (id: number) => {
  return request.delete(`/paper/${id}`)
}
