import request from '@/utils/request'

export interface PointLogItem {
  id: number
  userId: number
  points: number
  ruleKey: string
  refType?: string
  refId?: number
  remark?: string
  createTime?: string
}

export interface RankingItem {
  userId: number
  realName?: string
  username?: string
  totalPoints: number
  rank: number
}

export const getMyTotal = () => request.get<number>('/point/my')
export const getMyLog = (params: { page?: number; size?: number }) =>
  request.get<PointLogItem[]>('/point/log', { params })
export const getRanking = (params?: { limit?: number; departmentId?: number }) =>
  request.get<RankingItem[]>('/point/ranking', { params })
