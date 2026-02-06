import request from '@/utils/request'

export interface FeishuSyncResult {
  departments: { created: number; updated: number; errors: string[] }
  users: { created: number; updated: number; errors: string[] }
}

export const feishuSync = () => request.post<FeishuSyncResult>('/feishu/sync')
