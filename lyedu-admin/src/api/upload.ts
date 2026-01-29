import request from '@/utils/request'

export interface InitUploadRequest {
  fileId?: string
  fileName: string
  fileSize: number
  fileType: string
  chunkSize?: number
}

export interface InitUploadResponse {
  fileId: string
  chunkSize: number
  totalChunks: number
  uploadedChunks: number[]
}

export interface UploadProgressResponse {
  fileId: string
  fileName: string
  fileSize: number
  totalChunks: number
  uploadedChunks: number
  uploadedChunkIndexes: number[]
  status: number
  progress: number
}

export interface MergeResponse {
  fileId: string
  filePath: string
  url: string
}

/**
 * 初始化文件上传
 */
export const initUpload = (data: InitUploadRequest) => {
  return request.post<InitUploadResponse>('/upload/init', data)
}

/**
 * 获取上传进度
 */
export const getUploadProgress = (fileId: string) => {
  return request.get<UploadProgressResponse>(`/upload/progress/${fileId}`)
}

/**
 * 上传分片
 */
export const uploadChunk = (fileId: string, chunkIndex: number, chunkSize: number, file: File) => {
  const formData = new FormData()
  formData.append('fileId', fileId)
  formData.append('chunkIndex', chunkIndex.toString())
  formData.append('chunkSize', chunkSize.toString())
  formData.append('file', file)
  
  return request.post('/upload/chunk', formData, {
    timeout: 300000 // 5分钟超时，用于大文件上传
  })
}

/**
 * 合并分片
 */
export const mergeChunks = (fileId: string) => {
  return request.post<MergeResponse>(`/upload/merge/${fileId}`)
}

/**
 * 取消上传
 */
export const cancelUpload = (fileId: string) => {
  return request.delete(`/upload/${fileId}`)
}
