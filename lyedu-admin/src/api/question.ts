import request from '@/utils/request'

export interface Question {
  id: number
  type: string
  title: string
  options?: string
  answer?: string
  score: number
  analysis?: string
  sort: number
  createTime?: string
  updateTime?: string
}

export interface PageResult<T> {
  records: T[]
  total: number
  current: number
  size: number
  pages: number
}

export const getQuestionPage = (params: {
  page: number
  size: number
  keyword?: string
  type?: string
}) => {
  return request.get<PageResult<Question>>('/question/page', { params })
}

export const getQuestionById = (id: number) => {
  return request.get<Question>(`/question/${id}`)
}

export const createQuestion = (data: Partial<Question>) => {
  return request.post<number>('/question', data)
}

export const updateQuestion = (id: number, data: Partial<Question>) => {
  return request.put(`/question/${id}`, data)
}

export const deleteQuestion = (id: number) => {
  return request.delete(`/question/${id}`)
}

/** 试题导入：上传 Excel/CSV/JSON 文件，返回成功数、失败数及错误信息 */
export const importQuestionsByFile = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return request.post<{ successCount: number; failCount: number; messages: string[] }>('/question/import', form)
}

/** 试题导入：直接提交 JSON 数组（粘贴在输入框），返回成功数、失败数及错误信息 */
export const importQuestionsByJson = (data: object[]) => {
  return request.post<{ successCount: number; failCount: number; messages: string[] }>('/question/import/json', data)
}
