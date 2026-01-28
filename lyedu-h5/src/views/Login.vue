<template>
  <div class="login-container">
    <van-nav-bar title="登录" left-arrow @click-left="$router.back()" />
    
    <div class="login-content">
      <div class="logo">
        <h1>LyEdu</h1>
        <p>企业培训平台</p>
      </div>

      <van-form @submit="handleLogin">
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
            type="password"
            name="password"
            label="密码"
            placeholder="请输入密码"
            :rules="[{ required: true, message: '请输入密码' }]"
          />
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
import { useRouter } from 'vue-router'
import { showToast } from 'vant'

const router = useRouter()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  loading.value = true
  // TODO: 调用登录接口
  setTimeout(() => {
    loading.value = false
    showToast.success('登录成功')
    router.push('/')
  }, 1000)
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

    h1 {
      font-size: 36px;
      color: #667eea;
      margin-bottom: 10px;
    }

    p {
      color: #969799;
      font-size: 14px;
    }
  }

  .login-button {
    margin-top: 30px;
    padding: 0 16px;
  }
}
</style>
