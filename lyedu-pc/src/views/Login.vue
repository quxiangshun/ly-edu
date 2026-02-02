<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <img src="/icon-192.png" alt="LyEdu" class="login-logo" />
        <h1 class="login-title">LyEdu <span class="login-subtitle">企业培训平台</span></h1>
      </div>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" class="login-form">
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
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { View, Hide } from '@element-plus/icons-vue'
import { login, type LoginParams } from '@/api/user'

const router = useRouter()
const route = useRoute()
const loginFormRef = ref<FormInstance>()
const loading = ref(false)
const showPassword = ref(false)

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
    const url = window.location.origin + target
    try {
      await router.push(target)
    } catch {
      window.location.href = url
      return
    }
    setTimeout(() => {
      if (location.pathname === '/login') {
        window.location.href = url
      }
    }, 100)
  } catch (e) {
    // 校验或请求失败时，错误提示由 axios 拦截器或 UI 负责
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
    color: #667eea;
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
</style>
