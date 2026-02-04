import request from '@/utils/request'

// 用户登录
export interface LoginParams {
  username: string
  password: string
}

export interface LoginResult {
  token: string
  userInfo: {
    id: number
    username: string
    realName: string
    role: string
  }
}

export const login = (params: LoginParams) => {
  return request.post<LoginResult>('/auth/login', params)
}

// 获取用户信息
export const getUserInfo = () => {
  return request.get('/user/info')
}

// 员工管理
export interface User {
  id: number
  username: string
  /** 后端字段 real_name */
  real_name?: string
  email?: string
  mobile?: string
  avatar?: string
  departmentId?: number
  role: string
  status: number
}

export interface PageResult<T> {
  records: T[]
  total: number
  current: number
  size: number
  pages: number
}

export const getUserPage = (params: {
  page: number
  size: number
  keyword?: string
  departmentId?: number
  role?: string
  status?: number
}) => {
  return request.get<PageResult<User>>('/user/page', { params })
}

export const getUserById = (id: number) => {
  return request.get<User>(`/user/${id}`)
}

export const createUser = (data: Partial<User>) => {
  return request.post('/user', data)
}

export const updateUser = (id: number, data: Partial<User>) => {
  return request.put(`/user/${id}`, data)
}

export const deleteUser = (id: number) => {
  return request.delete(`/user/${id}`)
}

export const resetUserPassword = (id: number, password: string) => {
  return request.post(`/user/${id}/reset-password`, { password })
}

/** 员工导入：上传 Excel 文件，返回成功数、失败数及错误信息 */
export const importUsersByExcel = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return request.post<{ successCount: number; failCount: number; messages: string[] }>('/user/import', form)
}
