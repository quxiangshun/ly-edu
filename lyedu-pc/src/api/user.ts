import request from '@/utils/request'

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

