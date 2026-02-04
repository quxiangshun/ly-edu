import request from '@/utils/request'

export interface ConfigItem {
  id: number
  configKey: string
  configValue?: string
  category?: string
  remark?: string
}

export const getConfigAll = () => request.get<ConfigItem[]>('/config/all')
export const getConfigByKey = (key: string) => request.get<string>(`/config/key/${encodeURIComponent(key)}`)
export const batchSetConfig = (data: Record<string, string>) => request.post('/config/batch', data)
