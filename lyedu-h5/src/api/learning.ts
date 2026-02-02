import request from '@/utils/request'
import type { Course } from '@/api/course'

export const joinCourse = (courseId: number) => {
  return request.post('/learning/join', { courseId })
}

export const getMyCourses = () => {
  return request.get('/learning/my-courses')
}

export const updateVideoProgress = (videoId: number, progress: number, duration: number) => {
  return request.post('/learning/video-progress', { videoId, progress, duration })
}

/** 我的学习：仅返回看过的课程（有播放进度>0的课程） */
export const getWatchedCourses = () => {
  return request.get<Course[]>('/learning/watched-courses')
}

/** 播放心跳（防挂机）：播放过程中定时上报 */
export const playPing = (videoId: number) => {
  return request.post('/learning/play-ping', { videoId })
}
