import request from '@/utils/request'

export const joinCourse = (courseId: number) => {
  return request.post('/learning/join', { courseId })
}

export const getMyCourses = () => {
  return request.get('/learning/my-courses')
}
