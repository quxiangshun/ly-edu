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
