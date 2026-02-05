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
}

export interface PaperQuestionDto {
  questionId: number
  score: number
  sort: number
  question?: {
    id: number
    type: string
    title: string
    options?: string
    score?: number
    sort?: number
  }
}

export interface ExamRecord {
  id: number
  examId: number
  userId: number
  paperId: number
  score?: number
  passed?: number
  submitTime?: string
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

export const getExamStatus = (id: number) => {
  return request.get<{
    examId: number
    canStart: boolean
    status: string
    message: string
    startTime?: string
    endTime?: string
    durationMinutes?: number
    unlimited: boolean
  }>(`/exam-status/${id}`)
}

export const getPaperQuestions = (paperId: number) => {
  return request.get<PaperQuestionDto[]>(`/paper/${paperId}/questions`)
}

export const submitExam = (examId: number, answers: string) => {
  return request.post<ExamRecord>('/exam-record/submit', { examId, answers })
}

export const getMyRecords = () => {
  return request.get<ExamRecord[]>('/exam-record/my')
}
