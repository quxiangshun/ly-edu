import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Vant from 'vant'
import 'vant/lib/index.css'
import App from './App.vue'
import router from './router'
import './style.css'
import { getConfigByKey } from '@/api/config'
import { applyThemeFromConfig, applyDefaultTheme } from '@/utils/theme'

async function initBranding() {
  try {
    const [title, logo, mode, color] = await Promise.all([
      getConfigByKey('site.title').catch(() => ''),
      getConfigByKey('site.logo').catch(() => ''),
      getConfigByKey('site.theme_mode').catch(() => 'auto'),
      getConfigByKey('site.theme_color').catch(() => '')
    ])

    if (title) {
      document.title = String(title)
    }

    let logoUrl = ''
    if (logo) {
      const raw = String(logo)
      if (raw.startsWith('http://') || raw.startsWith('https://')) {
        logoUrl = raw
      } else if (raw.startsWith('/')) {
        logoUrl = window.location.origin + raw
      } else {
        logoUrl = raw
      }
    }

    await applyThemeFromConfig(String(mode ?? 'auto'), String(color ?? ''), logoUrl)
  } catch (_e) {
    applyDefaultTheme()
  }
}

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(Vant)

// 应用全局主题（与管理后台同一套配置）
initBranding()

app.mount('#app')
