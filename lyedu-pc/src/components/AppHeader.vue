<template>
  <el-header class="app-header">
    <div class="header-content">
      <div class="logo" @click="$router.push('/')">
        <img src="/icon-192.png" alt="" class="header-logo-icon" />
        <h1>LyEdu</h1>
      </div>
      <el-menu
        mode="horizontal"
        :default-active="activeMenu"
        class="header-menu"
        @select="handleMenuSelect"
      >
        <el-menu-item index="home">首页</el-menu-item>
        <el-menu-item index="courses">课程中心</el-menu-item>
        <el-menu-item index="knowledge" @click="$router.push('/knowledge')">知识中心</el-menu-item>
        <el-menu-item index="exam" @click="$router.push('/exam')">考试中心</el-menu-item>
        <el-menu-item index="certificates" @click="$router.push('/certificates')">我的证书</el-menu-item>
        <el-menu-item index="tasks" @click="$router.push('/tasks')">我的任务</el-menu-item>
        <el-menu-item index="points" @click="$router.push('/points')">积分</el-menu-item>
        <el-menu-item index="my" @click="$router.push('/my-learning')">我的学习</el-menu-item>
      </el-menu>
      <div class="header-right">
        <template v-if="!isLoggedIn">
          <el-button type="primary" @click="$router.push('/login')">登录</el-button>
        </template>
        <template v-else>
          <div class="user-info">
            <el-icon><User /></el-icon>
            <span class="user-name">{{ userName }}</span>
          </div>
          <el-button type="text" class="logout-btn" @click="handleLogout">退出登录</el-button>
        </template>
      </div>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const token = ref<string | null>(null)
const userInfo = ref<any>(null)

const isLoggedIn = computed(() => !!token.value)
const userName = computed(() => {
  if (userInfo.value) {
    return userInfo.value.realName || userInfo.value.username || '用户'
  }
  return '用户'
})

const activeMenu = computed(() => {
  const path = route.path
  if (path === '/') return 'home'
  if (path.startsWith('/courses') || path.startsWith('/course/')) return 'courses'
  if (path.startsWith('/knowledge')) return 'knowledge'
  if (path.startsWith('/exam')) return 'exam'
  if (path.startsWith('/certificates')) return 'certificates'
  if (path.startsWith('/tasks') || path.startsWith('/task/')) return 'tasks'
  if (path.startsWith('/points')) return 'points'
  if (path.startsWith('/my-learning')) return 'my'
  return 'home'
})

const handleMenuSelect = (index: string) => {
  if (index === 'home') {
    router.push('/')
  } else if (index === 'courses') {
    router.push('/courses')
  } else if (index === 'my') {
    router.push('/my-learning')
  }
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  token.value = null
  userInfo.value = null
  ElMessage.success('已退出登录')
  router.push('/')
}

const loadUserInfo = () => {
  token.value = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      userInfo.value = JSON.parse(userStr)
    } catch {
      userInfo.value = null
    }
  } else {
    userInfo.value = null
  }
}

onMounted(() => {
  loadUserInfo()
  // 监听storage变化
  window.addEventListener('storage', loadUserInfo)
  // 定期检查token变化（处理同页面内修改的情况）
  setInterval(() => {
    const currentToken = localStorage.getItem('token')
    if (currentToken !== token.value) {
      loadUserInfo()
    }
  }, 500)
})
</script>

<style scoped lang="scss">
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
  height: 60px;

  .header-content {
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    height: 100%;

    .logo {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;

      .header-logo-icon {
        width: 28px;
        height: 28px;
        display: block;
        object-fit: contain;
      }

      h1 {
        color: #667eea;
        font-size: 24px;
        margin: 0;
        line-height: 28px;
      }
    }

    .header-menu {
      flex: 1;
      margin-left: 40px;
      border: none;
    }

    .header-right {
      margin-left: 20px;
      display: flex;
      align-items: center;
      gap: 12px;

      .user-info {
        display: flex;
        align-items: center;
        gap: 6px;
        color: #606266;
        font-size: 14px;

        .user-name {
          font-weight: 500;
        }
      }

      .logout-btn {
        color: #606266;
        padding: 0 8px;

        &:hover {
          color: var(--el-color-danger);
        }
      }
    }
  }
}
</style>
