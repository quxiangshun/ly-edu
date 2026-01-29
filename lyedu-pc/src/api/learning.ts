import request from '@/utils/request'

export interface UserCourse {
  id: number
  userId: number
  courseId: number
  progress: number
  status: number
  createTime?: string
  updateTime?: string
}

export const joinCourse = (courseId: number) => {
  return request.post('/learning/join', { courseId })
}

export const getMyCourses = () => {
  return request.get<UserCourse[]>('/learning/my-courses')
}

export const updateVideoProgress = (videoId: number, progress: number, duration: number) => {
  return request.post('/learning/video-progress', { videoId, progress, duration })
}

export const getVideoProgress = (videoId: number) => {
  return request.get(`/learning/video-progress/${videoId}`)
}

