import request from '@/utils/request'

/** 飞书授权页 URL（后端用 app_id 等拼好） */
export function getFeishuAuthUrl(redirectUri: string, state?: string) {
  return request.get<{ url: string }>('/auth/feishu/url', {
    params: { redirect_uri: redirectUri, state: state || '' }
  })
}

/** 用 code 换 JWT（后端会查/建用户并返回 token） */
export function feishuCallback(code: string, redirectUri: string) {
  return request.post<{ token: string; userInfo: Record<string, unknown> }>('/auth/feishu/callback', {
    code,
    redirectUri
  })
}
