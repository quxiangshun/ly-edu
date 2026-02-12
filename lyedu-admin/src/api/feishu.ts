import request from '@/utils/request'

export interface FeishuSyncRequest {
  sync_departments?: boolean
  sync_users?: boolean
  overwrite_existing?: boolean
}

export interface FeishuSyncResult {
  success: boolean
  message: string
  stats?: {
    departments_created: number
    departments_updated: number
    departments_skipped: number
    departments_failed: number
    users_created: number
    users_updated: number
    users_skipped: number
    users_failed: number
  }
  departments?: { created: number; updated: number; errors: string[] }
  users?: { created: number; updated: number; errors: string[] }
  errors?: string[]
}

/** 后台同步：立即返回 task_id，避免 30s 超时；需轮询 GET /feishu/sync/task/:taskId 获取结果 */
export const feishuSyncBackground = (body?: FeishuSyncRequest) =>
  request.post<{ task_id: string; status: string; message: string }>('/feishu/sync', body ?? {}, {
    params: { background: 1 },
    timeout: 10000
  })

/** 查询后台同步任务状态与结果 */
export const feishuSyncTaskStatus = (taskId: string) =>
  request.get<{ task_id: string; status: string; result?: FeishuSyncResult; error?: string }>(`/feishu/sync/task/${taskId}`)

/** 同步执行（易超时，建议用 feishuSyncBackground + 轮询） */
export const feishuSync = (body?: FeishuSyncRequest) =>
  request.post<FeishuSyncResult>('/feishu/sync', body ?? {}, { timeout: 120000 })
