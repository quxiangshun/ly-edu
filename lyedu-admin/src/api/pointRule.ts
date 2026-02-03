import request from '@/utils/request'

export interface PointRuleItem {
  id: number
  ruleKey: string
  ruleName?: string
  points: number
  enabled: number
  remark?: string
}

export const getPointRuleList = () => request.get<PointRuleItem[]>('/point-rule/list')
export const updatePointRule = (data: { ruleKey: string; ruleName?: string; points?: number; enabled?: number; remark?: string }) =>
  request.put('/point-rule/update', data)
