import request from '@/utils/request'

/** 获取单条配置（无需登录，用于播放器限制等） */
export const getConfigByKey = (key: string) =>
  request.get<string>(`/config/key/${encodeURIComponent(key)}`)
