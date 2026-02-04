<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <img :src="logoSrc" :alt="siteTitle" class="login-logo" />
        <h1 class="login-title">{{ siteTitle }} <span class="login-subtitle">企业培训平台</span></h1>
      </div>

      <!-- 飞书扫码登录（扩展点：后续可加企业微信、钉钉等） -->
      <div v-if="isFeishuEnabled()" class="feishu-login">
        <el-button
          type="primary"
          size="large"
          :loading="feishuLoading"
          @click="handleFeishuLogin"
          class="login-button feishu-btn"
        >
          飞书扫码登录
        </el-button>
      </div>

      <el-form
        v-if="!isFeishuOnly()"
        :model="loginForm"
        :rules="rules"
        ref="loginFormRef"
        class="login-form"
      >
        <template v-if="isFeishuEnabled()">
          <div class="divider"><span>或使用账号密码</span></div>
        </template>
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            @keyup.enter="handleLogin"
          >
            <template #suffix>
              <el-icon
                class="password-icon"
                @click="showPassword = !showPassword"
                style="cursor: pointer; color: #909399;"
              >
                <component :is="showPassword ? 'View' : 'Hide'" />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { View, Hide } from '@element-plus/icons-vue'
import { login, type LoginParams } from '@/api/user'
import { getFeishuAuthUrl } from '@/api/auth'
import { isFeishuEnabled, isFeishuOnly } from '@/utils/auth'
import { getConfigByKey } from '@/api/config'
import { applyThemeFromConfig, applyDefaultTheme } from '@/utils/theme'

const router = useRouter()
const route = useRoute()
const loginFormRef = ref<FormInstance>()
const loading = ref(false)
const feishuLoading = ref(false)
const showPassword = ref(false)

const siteTitle = ref('LyEdu')
const siteLogo = ref('')

const logoSrc = computed(() => {
  const raw = siteLogo.value || '/icon-192.png'
  if (raw.startsWith('http://') || raw.startsWith('https://')) return raw
  if (raw.startsWith('/')) return window.location.origin + raw
  return raw
})

const loginForm = reactive<LoginParams>({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const doRedirect = (target: string) => {
  const url = window.location.origin + target
  router.push(target).catch(() => {
    window.location.href = url
  })
  setTimeout(() => {
    if (location.pathname === '/login') window.location.href = url
  }, 100)
}

const handleFeishuLogin = async () => {
  feishuLoading.value = true
  try {
    const r = (route.query.redirect as string) || '/'
    const path = r.startsWith('/') ? r : `/${r}`
    const fullRedirect = window.location.origin + path
    const res = await getFeishuAuthUrl(fullRedirect, 'feishu_scan')
    if (res?.url) {
      window.location.href = res.url
      return
    }
    ElMessage.error('获取飞书登录地址失败')
  } catch (e) {
    ElMessage.error('飞书登录失败，请重试')
  } finally {
    feishuLoading.value = false
  }
}

async function loadBranding() {
  try {
    const title = await getConfigByKey('site.title')
    if (title) {
      siteTitle.value = title
      document.title = title
    }
  } catch (_e) {}

  try {
    const logo = await getConfigByKey('site.logo')
    if (logo) siteLogo.value = logo
  } catch (_e) {}

  try {
    const mode = (await getConfigByKey('site.theme_mode')) ?? 'auto'
    const color = (await getConfigByKey('site.theme_color')) ?? ''
    const logoUrl = siteLogo.value
    await applyThemeFromConfig(String(mode), String(color), logoUrl ? logoSrc.value : '')
  } catch (_e) {
    applyDefaultTheme()
  }
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()
    loading.value = true
    const res = await login(loginForm)
    if (!res?.token) {
      ElMessage.error('登录响应异常，请重试')
      return
    }
    localStorage.setItem('token', res.token)
    localStorage.setItem('user', JSON.stringify(res.userInfo ?? {}))
    ElMessage.success('登录成功')
    let redirect = (route.query.redirect as string) || '/'
    if (redirect === '/login') redirect = '/'
    const target = redirect.startsWith('/') ? redirect : `/${redirect}`
    doRedirect(target)
  } catch (e) {
    // 校验或请求失败时，错误提示由 axios 拦截器或 UI 负责
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadBranding()
})
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, var(--el-color-primary) 0%, rgba(0, 0, 0, 0.2) 100%);
}

.login-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;

  .login-logo {
    width: 72px;
    height: 72px;
    margin-bottom: 12px;
    display: block;
    margin-left: auto;
    margin-right: auto;
  }

  .login-title {
    font-size: 28px;
    color: var(--el-color-primary);
    margin: 0;
    font-weight: 600;
  }

  .login-subtitle {
    font-size: 16px;
    color: #666;
    font-weight: normal;
  }
}

.login-form {
  .login-button {
    width: 100%;
  }
}

.feishu-login {
  margin-bottom: 16px;
  .feishu-btn {
    width: 100%;
  }
}

.divider {
  text-align: center;
  color: #909399;
  font-size: 12px;
  margin: 8px 0 16px;
}
</style>
