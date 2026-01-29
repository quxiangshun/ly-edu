import request from '@/utils/request'
import type { Video } from './course'

export const getVideoById = (id: number) => {
  return request.get<Video>(`/video/${id}`)
}
