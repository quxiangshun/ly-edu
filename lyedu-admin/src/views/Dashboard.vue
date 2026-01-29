<template>
  <div class="dashboard-container">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h2>LyEdu 管理后台</h2>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ userInfo?.realName || userInfo?.username || '管理员' }}
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人设置</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main>
        <div class="welcome">
          <h1>欢迎使用 LyEdu 企业培训系统</h1>
          <p>这是一个完全开源的企业培训解决方案</p>
          <div class="stats">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-value">0</div>
                <div class="stat-label">学员总数</div>
              </div>
            </el-card>
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-value">0</div>
                <div class="stat-label">课程总数</div>
              </div>
            </el-card>
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-value">0</div>
                <div class="stat-label">部门总数</div>
              </div>
            </el-card>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'

const router = useRouter()

// 获取用户信息
const userInfo = computed(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      return JSON.parse(userStr)
    } catch {
      return null
    }
  }
  return null
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  ElMessage.success('已退出登录')
  router.push('/login')
}

// 检查登录状态
onMounted(() => {
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
  }
})
</script>

<style scoped lang="scss">
.dashboard-container {
  width: 100%;
  height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;

  .header-left {
    h2 {
      color: #667eea;
      margin: 0;
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      color: #606266;
    }
  }
}

.welcome {
  padding: 40px;
  text-align: center;

  h1 {
    font-size: 32px;
    color: #303133;
    margin-bottom: 10px;
  }

  p {
    font-size: 16px;
    color: #909399;
    margin-bottom: 40px;
  }

  .stats {
    display: flex;
    gap: 20px;
    justify-content: center;
    margin-top: 40px;

    .stat-card {
      width: 200px;

      .stat-content {
        text-align: center;

        .stat-value {
          font-size: 36px;
          font-weight: bold;
          color: #667eea;
          margin-bottom: 10px;
        }

        .stat-label {
          font-size: 14px;
          color: #909399;
        }
      }
    }
  }
}
</style>
