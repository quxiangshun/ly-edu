<template>
  <div class="login-container">
    <van-nav-bar title="登录" left-arrow @click-left="$router.back()" />
    
    <div class="login-content">
      <div class="logo">
        <img src="/icon-192.png" alt="LyEdu" class="login-logo" />
        <h1 class="login-title">LyEdu <span class="login-subtitle">企业培训平台</span></h1>
      </div>

      <!-- 飞书扫码登录（扩展点：后续可加企业微信、钉钉等） -->
      <div v-if="isFeishuEnabled()" class="feishu-login">
        <van-button
          round
          block
          type="primary"
          :loading="feishuLoading"
          @click="handleFeishuLogin"
          class="feishu-btn"
        >
          飞书扫码登录
        </van-button>
      </div>

      <van-form v-if="!isFeishuOnly()" @submit="handleLogin">
        <div v-if="isFeishuEnabled()" class="divider">或使用账号密码</div>
        <van-cell-group inset>
          <van-field
            v-model="loginForm.username"
            name="username"
            label="用户名"
            placeholder="请输入用户名"
            :rules="[{ required: true, message: '请输入用户名' }]"
          />
          <van-field
            v-model="loginForm.password"
            :type="showPassword ? 'text' : 'password'"
            name="password"
            label="密码"
            placeholder="请输入密码"
            :rules="[{ required: true, message: '请输入密码' }]"
          >
            <template #right-icon>
              <van-icon
                :name="showPassword ? 'eye-o' : 'closed-eye'"
                @click="showPassword = !showPassword"
                style="cursor: pointer;"
              />
            </template>
          </van-field>
        </van-cell-group>

        <div class="login-button">
          <van-button round block type="primary" native-type="submit" :loading="loading">
            登录
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showSuccessToast } from 'vant'
import request from '@/utils/request'
import { getFeishuAuthUrl } from '@/api/auth'
import { isFeishuEnabled, isFeishuOnly } from '@/utils/auth'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const feishuLoading = ref(false)
const showPassword = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const handleFeishuLogin = async () => {
  feishuLoading.value = true
  try {
    const r = (route.query.redirect as string) || '/index'
    const path = r.startsWith('/') ? r : `/${r}`
    const fullRedirect = window.location.origin + path
    const res = await getFeishuAuthUrl(fullRedirect, 'feishu_scan')
    if (res?.url) {
      window.location.href = res.url
      return
    }
    showSuccessToast('获取飞书登录地址失败')
  } catch (e) {
    showSuccessToast('飞书登录失败，请重试')
  } finally {
    feishuLoading.value = false
  }
}

const handleLogin = async () => {
  loading.value = true
  try {
    const res = await request.post('/auth/login', loginForm)
    localStorage.setItem('token', res.token)
    localStorage.setItem('user', JSON.stringify(res.userInfo ?? {}))
    showSuccessToast('登录成功')
    let redirect = (route.query.redirect as string) || '/index'
    if (redirect === '/login' || redirect === '/') redirect = '/index'
    const target = redirect.startsWith('/') ? redirect : `/${redirect}`
    const url = window.location.origin + target
    try {
      await router.push(target)
    } catch {
      window.location.href = url
      return
    }
    setTimeout(() => {
      if (location.pathname === '/login') window.location.href = url
    }, 100)
  } catch (e) {
    // 错误提示由 axios 拦截器处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  min-height: 100vh;
  background: #f7f8fa;
}

.login-content {
  padding: 40px 20px;

  .logo {
    text-align: center;
    margin-bottom: 40px;

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
      color: #667eea;
      margin: 0;
      font-weight: 600;
    }

    .login-subtitle {
      font-size: 16px;
      color: #969799;
      font-weight: normal;
    }
  }

  .login-button {
    margin-top: 30px;
    padding: 0 16px;
  }

  .feishu-login {
    margin-bottom: 16px;
    padding: 0 16px;
  }

  .divider {
    text-align: center;
    color: #969799;
    font-size: 12px;
    margin: 8px 0 16px;
  }
}
</style>
