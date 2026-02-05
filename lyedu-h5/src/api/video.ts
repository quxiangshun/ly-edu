import request from '@/utils/request'
import type { Video } from './course'
import type { PageResult } from './course'

export const getVideoById = (id: number) => {
  return request.get<Video>(`/video/${id}`)
}

/** 我点赞的视频，分页（滚动加载） */
export const getLikedVideos = (params: { page: number; size: number }) => {
  return request.get<PageResult<Video>>('/video/liked', { params })
}

/** 记录播放次数（开始播放时调用一次） */
export const recordPlay = (id: number) => {
  return request.post(`/video/${id}/play`)
}

/** 点赞 */
export const likeVideo = (id: number) => {
  return request.post(`/video/${id}/like`)
}

/** 取消点赞 */
export const unlikeVideo = (id: number) => {
  return request.delete(`/video/${id}/like`)
}
