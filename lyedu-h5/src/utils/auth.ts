/**
 * 登录方式扩展点：飞书 / 本地账号；后续可扩展企业微信、钉钉等
 * 嵌套在飞书内时点击应用直接进入，通过 code 换 token 免登
 */
export type AuthProviderType = 'feishu' | 'local' | 'both'

/** 从环境变量读取，构建时注入；默认 local 兼容旧版 */
export function getAuthProvider(): AuthProviderType {
  const v = import.meta.env.VITE_AUTH_PROVIDER as string
  if (v === 'feishu' || v === 'both') return v
  return 'local'
}

export function isFeishuEnabled(): boolean {
  const p = getAuthProvider()
  return p === 'feishu' || p === 'both'
}

export function isFeishuOnly(): boolean {
  return getAuthProvider() === 'feishu'
}

export function isInFeishuEmbed(): boolean {
  if (typeof window === 'undefined') return false
  const u = new URL(window.location.href)
  return u.searchParams.get('from') === 'feishu' || u.searchParams.get('lark_from') === 'feishu'
}

export function getFeishuRedirectUri(): string {
  if (typeof window === 'undefined') return ''
  const base = window.location.origin + window.location.pathname
  const q = new URLSearchParams(window.location.search)
  q.delete('code')
  q.delete('state')
  const rest = q.toString()
  return rest ? `${base}?${rest}` : base
}

export function getFeishuCodeFromUrl(): { code: string; state: string | null } | null {
  if (typeof window === 'undefined') return null
  const u = new URL(window.location.href)
  const code = u.searchParams.get('code')
  if (!code || !code.trim()) return null
  return { code: code.trim(), state: u.searchParams.get('state') }
}

export function clearFeishuCodeInUrl(): void {
  if (typeof window === 'undefined') return
  const u = new URL(window.location.href)
  u.searchParams.delete('code')
  u.searchParams.delete('state')
  const newUrl = u.pathname + (u.search || '') + u.hash
  window.history.replaceState({}, '', newUrl)
}
