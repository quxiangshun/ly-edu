import request from '@/utils/request'

export function getFeishuAuthUrl(redirectUri: string, state?: string) {
  return request.get<{ url: string }>('/auth/feishu/url', {
    params: { redirect_uri: redirectUri, state: state || '' }
  })
}

export function feishuCallback(code: string, redirectUri: string) {
  return request.post<{ token: string; userInfo: Record<string, unknown> }>('/auth/feishu/callback', {
    code,
    redirectUri
  })
}
