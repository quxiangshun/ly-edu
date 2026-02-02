import request from '@/utils/request'

export interface Department {
  id: number
  name: string
  parentId: number
  sort: number
  status: number
  children?: Department[]
}

export const getDepartmentTree = () => {
  return request.get<Department[]>('/department/tree')
}

export const getDepartmentById = (id: number) => {
  return request.get<Department>(`/department/${id}`)
}

export const createDepartment = (data: Partial<Department>) => {
  return request.post('/department', data)
}

export const updateDepartment = (id: number, data: Partial<Department>) => {
  return request.put(`/department/${id}`, data)
}

export const deleteDepartment = (id: number) => {
  return request.delete(`/department/${id}`)
}
