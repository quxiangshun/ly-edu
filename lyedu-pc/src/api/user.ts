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

/** 当前用户简要信息（GET /user/info） */
export interface CurrentUserInfo {
  id: number
  username: string
  realName: string
  nickname?: string
  role: string
}

/** 用户详情（GET /user/{id}，含邮箱、手机、头像等） */
export interface UserDetail {
  id: number
  username: string
  realName?: string
  nickname?: string
  email?: string
  mobile?: string
  avatar?: string
  role?: string
  real_name?: string
  create_time?: string
  createTime?: string
}

/** 更新用户资料请求体 */
export interface UserUpdateParams {
  realName?: string
  nickname?: string
  email?: string
  mobile?: string
  avatar?: string
}

export const login = (params: LoginParams) => {
  return request.post<LoginResult>('/auth/login', params)
}

/** 获取当前登录用户信息（供 Header、个人中心等使用） */
export const getCurrentUser = () => {
  return request.get<CurrentUserInfo>('/user/info')
}

/** 获取用户详情（含邮箱、手机、头像，用于个人中心编辑） */
export const getUserById = (id: number) => {
  return request.get<UserDetail>(`/user/${id}`)
}

/** 更新用户信息（后端接口使用 real_name） */
export const updateUser = (id: number, params: UserUpdateParams) => {
  const body: Record<string, string | undefined> = {}
  if (params.realName !== undefined) body.real_name = params.realName
  if (params.nickname !== undefined) body.nickname = params.nickname
  if (params.email !== undefined) body.email = params.email
  if (params.mobile !== undefined) body.mobile = params.mobile
  if (params.avatar !== undefined) body.avatar = params.avatar
  return request.put<void>(`/user/${id}`, body)
}

