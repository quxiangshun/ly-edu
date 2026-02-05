import request from '@/utils/request'

export interface UserCertificate {
  id: number
  userId: number
  realName?: string
  username?: string
  certificateId: number
  templateId: number
  certificateNo: string
  title: string
  issuedAt?: string
  createTime?: string
}

export interface PageResult<T> {
  records: T[]
  total: number
}

export const getUserCertificatePage = (params: {
  page: number
  size: number
  keyword?: string
  userId?: number
  certificateId?: number
}) => {
  return request.get<PageResult<UserCertificate>>('/user-certificate/page', { params })
}
