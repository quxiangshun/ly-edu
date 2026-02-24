import request from '@/utils/request'

export interface Department {
  id: number
  name: string
  parentId: number
  sort: number
  status: number
  children?: Department[]
  /** 标签ID列表 */
  tagIds?: number[]
  /** 祖籍路径：从根到自身的ID链，如 "1.2.3"（类 ltree） */
  path?: string
  /** 祖籍ID列表：从根到父级，不含自身，便于查询 */
  ancestorIds?: number[]
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
