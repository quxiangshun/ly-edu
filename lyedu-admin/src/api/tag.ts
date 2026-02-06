import request from '@/utils/request'

export interface Tag {
  id: number
  name: string
  sort: number
  createTime?: string
}

export const getTagList = () => {
  return request.get<Tag[]>('/tag/list')
}

export const getTagById = (id: number) => {
  return request.get<Tag>(`/tag/${id}`)
}

export const createTag = (data: { name: string; sort?: number }) => {
  return request.post('/tag', data)
}

export const updateTag = (id: number, data: { name?: string; sort?: number }) => {
  return request.put(`/tag/${id}`, data)
}

export const deleteTag = (id: number) => {
  return request.delete(`/tag/${id}`)
}

export const getTagUsers = (tagId: number) => {
  return request.get<import('@/api/user').User[]>(`/tag/${tagId}/users`)
}

export const getTagDepartments = (tagId: number) => {
  return request.get<import('@/api/department').Department[]>(`/tag/${tagId}/departments`)
}

export const getTagCourses = (tagId: number) => {
  return request.get<import('@/api/course').Course[]>(`/tag/${tagId}/courses`)
}

export const setTagEntities = (
  tagId: number,
  data: { userIds?: number[]; departmentIds?: number[]; courseIds?: number[] }
) => {
  return request.put(`/tag/${tagId}/entities`, data)
}
