import request from '@/utils/request'

export interface CertificateTemplate {
  id: number
  name: string
  description?: string
  config?: string
  sort?: number
  status: number
  createTime?: string
  updateTime?: string
}

export const getTemplateList = () => {
  return request.get<CertificateTemplate[]>('/certificate-template/list')
}

export const getTemplateById = (id: number) => {
  return request.get<CertificateTemplate>(`/certificate-template/${id}`)
}

export const createTemplate = (data: Partial<CertificateTemplate>) => {
  return request.post<number>('/certificate-template', data)
}

export const updateTemplate = (id: number, data: Partial<CertificateTemplate>) => {
  return request.put(`/certificate-template/${id}`, data)
}

export const deleteTemplate = (id: number) => {
  return request.delete(`/certificate-template/${id}`)
}
