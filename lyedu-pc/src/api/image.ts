import request from '@/utils/request'

export interface ImageItem {
  id: number
  name: string
  path: string
  url: string
  fileSize?: number
  createTime?: string
}

/** 上传图片（如个人中心头像），返回含 url 的对象，url 为相对路径如 /uploads/images/xxx */
export const uploadImage = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return request.post<ImageItem>('/image/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
