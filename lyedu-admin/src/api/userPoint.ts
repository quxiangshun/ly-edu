import request from '@/utils/request'

export interface UserPointLog {
  id: number
  userId: number
  realName?: string
  username?: string
  points: number
  ruleKey?: string
  refType?: string
  refId?: number
  remark?: string
  createTime?: string
}

export interface PageResult<T> {
  records: T[]
  total: number
}

export const getUserPointLogPage = (params: {
  page: number
  size: number
  keyword?: string
  userId?: number
}) => {
  return request.get<PageResult<UserPointLog>>('/point/log/page', { params })
}
