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
        <el-sub-menu index="learn">
          <template #title>学习与考试</template>
          <el-menu-item index="knowledge">知识中心</el-menu-item>
          <el-menu-item index="exam">考试中心</el-menu-item>
          <el-menu-item index="tasks">我的任务</el-menu-item>
          <!-- <el-menu-item index="ppt">PPT 制作</el-menu-item> -->
        </el-sub-menu>
        <el-sub-menu index="my-menu">
          <template #title>我的</template>
          <el-menu-item index="my">我的学习</el-menu-item>
          <el-menu-item index="certificates">我的证书</el-menu-item>
          <el-menu-item index="points">积分</el-menu-item>
        </el-sub-menu>
      </el-menu>
      <div class="header-right">
        <el-tooltip content="使用说明" placement="bottom">
          <div class="help-icon" @click="$router.push('/help')">
            <el-icon :size="20"><QuestionFilled /></el-icon>
          </div>
        </el-tooltip>
        <template v-if="!isLoggedIn">
          <el-button type="primary" @click="$router.push('/login')">登录</el-button>
        </template>
        <template v-else>
          <el-dropdown trigger="click" @command="handleUserCommand">
            <div class="user-info user-dropdown-trigger">
              <el-avatar v-if="userDisplayAvatar" :src="userDisplayAvatar" :size="28" class="user-avatar" />
              <el-icon v-else><User /></el-icon>
              <span class="user-name">{{ userName }}</span>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人信息
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </div>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, ArrowDown, SwitchButton, QuestionFilled } from '@element-plus/icons-vue'
import { getCurrentUser, type CurrentUserInfo } from '@/api/user'
import { getConfigByKey } from '@/api/config'

const router = useRouter()
const route = useRoute()

const token = ref<string | null>(null)
const userInfo = ref<CurrentUserInfo | null>(null)
const siteLogo = ref<string>('')

const isLoggedIn = computed(() => !!token.value)
const userName = computed(() => {
  if (userInfo.value) {
    return userInfo.value.nickname || userInfo.value.realName || userInfo.value.username || '用户'
  }
  return '用户'
})
const userAvatar = computed(() => {
  if (!userInfo.value) return ''
  const u = userInfo.value as CurrentUserInfo & { avatar?: string }
  const url = u.avatar || ''
  if (!url) return ''
  if (url.startsWith('http')) return url
  if (url.startsWith('/')) return window.location.origin + url
  return url
})
/** 用户区展示头像：有用户头像用用户头像，否则用后台配置的 site.logo */
const userDisplayAvatar = computed(() => {
  if (userAvatar.value) return userAvatar.value
  if (!siteLogo.value) return ''
  const raw = siteLogo.value
  if (raw.startsWith('http')) return raw
  if (raw.startsWith('/')) return window.location.origin + raw
  return raw
})

const handleUserCommand = (command: string) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    handleLogout()
  }
}

const activeMenu = computed(() => {
  const path = route.path
  if (path === '/') return 'home'
  if (path.startsWith('/courses') || path.startsWith('/course/')) return 'courses'
  if (path.startsWith('/knowledge')) return 'knowledge'
  if (path.startsWith('/exam')) return 'exam'
  if (path.startsWith('/certificates')) return 'certificates'
  if (path.startsWith('/tasks') || path.startsWith('/task/')) return 'tasks'
  if (path.startsWith('/ppt')) return 'ppt'
  if (path.startsWith('/points')) return 'points'
  if (path.startsWith('/my-learning')) return 'my'
  return 'home'
})

const handleMenuSelect = (index: string) => {
  const routes: Record<string, string> = {
    home: '/',
    courses: '/courses',
    knowledge: '/knowledge',
    exam: '/exam',
    tasks: '/tasks',
    ppt: '/ppt',
    my: '/my-learning',
    certificates: '/certificates',
    points: '/points'
  }
  const path = routes[index]
  if (path) router.push(path)
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  token.value = null
  userInfo.value = null
  ElMessage.success('已退出登录')
  router.push('/')
}

const loadUserInfo = async () => {
  token.value = localStorage.getItem('token')
  if (!token.value) {
    userInfo.value = null
    return
  }
  try {
    const res = await getCurrentUser()
    if (res) {
      userInfo.value = res
    } else {
      userInfo.value = null
    }
  } catch (_e) {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        userInfo.value = JSON.parse(userStr) as CurrentUserInfo
      } catch {
        userInfo.value = null
      }
    } else {
      userInfo.value = null
    }
  }
}

const loadSiteLogo = async () => {
  try {
    const logo = await getConfigByKey('site.logo')
    siteLogo.value = logo ? String(logo) : ''
  } catch (_e) {
    siteLogo.value = ''
  }
}

onMounted(() => {
  loadUserInfo()
  loadSiteLogo()
  window.addEventListener('storage', loadUserInfo)
  setInterval(() => {
    const currentToken = localStorage.getItem('token')
    if (currentToken !== token.value) {
      loadUserInfo()
    }
  }, 2000)
})

watch(() => route.path, () => {
  if (token.value) loadUserInfo()
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

      .help-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        color: #606266;
        cursor: pointer;
        border-radius: 4px;

        &:hover {
          color: var(--el-color-primary);
          background: var(--el-fill-color-light);
        }
      }

      .user-info.user-dropdown-trigger {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #606266;
        font-size: 14px;
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 4px;

        &:hover {
          color: var(--el-color-primary);
          background: var(--el-fill-color-light);
        }

        .user-avatar {
          flex-shrink: 0;
        }

        .user-name {
          font-weight: 500;
        }

        .dropdown-arrow {
          margin-left: 4px;
          font-size: 12px;
        }
      }
    }
  }
}
</style>
