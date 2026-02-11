import request from '@/utils/request'

export interface FeishuSyncRequest {
  sync_departments?: boolean
  sync_users?: boolean
  overwrite_existing?: boolean
}

export interface FeishuSyncResult {
  departments: { created: number; updated: number; errors: string[] }
  users: { created: number; updated: number; errors: string[] }
}

export const feishuSync = (body?: FeishuSyncRequest) =>
  request.post<FeishuSyncResult>('/feishu/sync', body ?? {})
