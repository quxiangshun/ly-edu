type BrandTheme = {
  primary: string
  onPrimary: string
}

function clamp01(n: number) {
  return Math.max(0, Math.min(1, n))
}

function rgbToHex(r: number, g: number, b: number) {
  const to = (x: number) => Math.max(0, Math.min(255, Math.round(x))).toString(16).padStart(2, '0')
  return `#${to(r)}${to(g)}${to(b)}`
}

function relativeLuminance(r: number, g: number, b: number) {
  const srgb = [r, g, b].map((v) => v / 255).map((v) => (v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)))
  return 0.2126 * srgb[0] + 0.7152 * srgb[1] + 0.0722 * srgb[2]
}

function bestOnColor(hex: string) {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex)
  if (!m) return '#ffffff'
  const n = parseInt(m[1], 16)
  const r = (n >> 16) & 255
  const g = (n >> 8) & 255
  const b = n & 255
  const L = relativeLuminance(r, g, b)
  // 对比度更高的一边
  return L > 0.5 ? '#111111' : '#ffffff'
}

async function loadImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    // 同源 /uploads 走代理，通常不需要跨域；加上以防未来改成 CDN
    img.crossOrigin = 'anonymous'
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error('load image failed'))
    img.src = url
  })
}

function extractDominantColor(img: HTMLImageElement): string {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  if (!ctx) return '#409eff'

  // 下采样到小尺寸，快速统计
  const w = 64
  const h = 64
  canvas.width = w
  canvas.height = h
  ctx.clearRect(0, 0, w, h)
  ctx.drawImage(img, 0, 0, w, h)
  const { data } = ctx.getImageData(0, 0, w, h)

  // 简单“主色”估算：过滤透明/近白/近黑像素后做加权平均（权重偏向饱和度）
  let sumR = 0
  let sumG = 0
  let sumB = 0
  let sumW = 0

  for (let i = 0; i < data.length; i += 4) {
    const a = data[i + 3] / 255
    if (a < 0.6) continue
    const r = data[i]
    const g = data[i + 1]
    const b = data[i + 2]
    const max = Math.max(r, g, b)
    const min = Math.min(r, g, b)
    const v = max / 255
    const s = max === 0 ? 0 : (max - min) / max

    // 过滤背景（白/黑/灰）
    if (v > 0.95 && s < 0.1) continue
    if (v < 0.12 && s < 0.3) continue
    if (s < 0.08) continue

    const weight = clamp01(s) * a
    sumR += r * weight
    sumG += g * weight
    sumB += b * weight
    sumW += weight
  }

  if (sumW <= 0) return '#409eff'
  return rgbToHex(sumR / sumW, sumG / sumW, sumB / sumW)
}

function applyThemeVars(t: BrandTheme) {
  const root = document.documentElement
  root.style.setProperty('--brand-primary', t.primary)
  root.style.setProperty('--brand-on-primary', t.onPrimary)

  // Element Plus 主题主色
  root.style.setProperty('--el-color-primary', t.primary)
}

export function applyDefaultTheme() {
  applyThemeVars({ primary: '#409eff', onPrimary: '#ffffff' })
}

/** 使用自定义主色（hex，如 #409eff） */
export function applyCustomTheme(hex: string) {
  const primary = /^#?[0-9a-f]{6}$/i.test(hex) ? (hex.startsWith('#') ? hex : '#' + hex) : '#409eff'
  const onPrimary = bestOnColor(primary)
  applyThemeVars({ primary, onPrimary })
}

export async function applyThemeFromLogoUrl(logoUrl: string) {
  const url = logoUrl || ''
  const cacheKey = `__brand_theme__:${url}`
  try {
    const cached = localStorage.getItem(cacheKey)
    if (cached) {
      const t = JSON.parse(cached) as BrandTheme
      if (t?.primary && t?.onPrimary) {
        applyThemeVars(t)
        return
      }
    }
  } catch {}

  try {
    const img = await loadImage(url)
    const primary = extractDominantColor(img)
    const onPrimary = bestOnColor(primary)
    const t: BrandTheme = { primary, onPrimary }
    applyThemeVars(t)
    try {
      localStorage.setItem(cacheKey, JSON.stringify(t))
    } catch {}
  } catch {
    // 回退默认
    applyDefaultTheme()
  }
}

/** 根据配置应用主题（用于恢复已保存样式） */
export async function applyThemeFromConfig(
  mode: string,
  customColor: string,
  logoUrl: string
): Promise<void> {
  const m = String(mode ?? 'auto').toLowerCase()
  if (m === 'custom' && customColor) {
    applyCustomTheme(customColor)
    return
  }
  if (m === 'default') {
    applyDefaultTheme()
    return
  }
  await applyThemeFromLogoUrl(logoUrl || '')
}

