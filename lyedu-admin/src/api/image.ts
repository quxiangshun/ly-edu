import request from '@/utils/request'

export interface ImageItem {
  id: number
  name: string
  path: string
  url: string
  fileSize?: number
  createTime?: string
}

export interface ImagePageResult {
  records: ImageItem[]
  total: number
  current: number
  size: number
  pages: number
}

export const uploadImage = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return request.post<ImageItem>('/image/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const getImagePage = (params: { page: number; size: number; keyword?: string }) =>
  request.get<ImagePageResult>('/image/page', { params })

export const deleteImage = (id: number) => request.delete(`/image/${id}`)
