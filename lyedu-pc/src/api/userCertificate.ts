import request from '@/utils/request'

export interface UserCertificate {
  id: number
  userId: number
  certificateId: number
  templateId: number
  certificateNo: string
  title: string
  issuedAt?: string
  createTime?: string
}

export interface CertificateTemplate {
  id: number
  name: string
  description?: string
  config?: string
  sort?: number
  status: number
}

export interface UserCertificateWithTemplate {
  userCertificate: UserCertificate
  template: CertificateTemplate | null
}

export const getMyCertificates = () => {
  return request.get<UserCertificate[]>('/user-certificate/my')
}

export const getCertificateDetail = (id: number) => {
  return request.get<UserCertificateWithTemplate>(`/user-certificate/${id}`)
}
