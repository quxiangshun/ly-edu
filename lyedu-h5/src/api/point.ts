import request from '@/utils/request'

export interface PointLogItem {
  id: number
  userId: number
  points: number
  ruleKey?: string
  remark?: string
  createTime?: string
}

export const getMyTotal = () => request.get<number>('/point/my')
export const getMyLog = (params?: { page?: number; size?: number }) =>
  request.get<PointLogItem[]>('/point/log', { params: params ?? {} })
export const getRanking = (params?: { limit?: number }) =>
  request.get<{ userId: number; realName?: string; username?: string; totalPoints: number; rank: number }[]>('/point/ranking', { params: params ?? {} })
