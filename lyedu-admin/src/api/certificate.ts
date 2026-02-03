import request from '@/utils/request'

export interface CertificateRule {
  id: number
  templateId: number
  name: string
  sourceType: string
  sourceId: number
  sort?: number
  status: number
  createTime?: string
  updateTime?: string
}

export const getCertificateList = () => {
  return request.get<CertificateRule[]>('/certificate/list')
}

export const getCertificateById = (id: number) => {
  return request.get<CertificateRule>(`/certificate/${id}`)
}

export const createCertificate = (data: Partial<CertificateRule> & { templateId: number; sourceType: string; sourceId: number }) => {
  return request.post<number>('/certificate', data)
}

export const updateCertificate = (id: number, data: Partial<CertificateRule>) => {
  return request.put(`/certificate/${id}`, data)
}

export const deleteCertificate = (id: number) => {
  return request.delete(`/certificate/${id}`)
}
