import request from '@/utils/request'

export interface ExamRecord {
  id: number
  examId: number
  examTitle?: string
  userId: number
  realName?: string
  username?: string
  paperId: number
  score: number
  passed: number
  answers?: string
  submitTime?: string
  createTime?: string
}

export interface PageResult<T> {
  records: T[]
  total: number
}

export const getExamRecordPage = (params: {
  page: number
  size: number
  keyword?: string
  examId?: number
  userId?: number
}) => {
  return request.get<PageResult<ExamRecord>>('/exam-record/page', { params })
}
