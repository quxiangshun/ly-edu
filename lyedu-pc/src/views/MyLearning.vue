<template>
  <div class="my-learning-container">
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <img src="/icon-192.png" alt="" class="header-logo-icon" />
          <h1>LyEdu</h1>
        </div>
        <el-menu
          mode="horizontal"
          default-active="my"
          class="header-menu"
        >
          <el-menu-item index="home" @click="$router.push('/')">首页</el-menu-item>
          <el-menu-item index="courses" @click="$router.push('/courses')">课程中心</el-menu-item>
          <el-menu-item index="my">我的学习</el-menu-item>
        </el-menu>
        <div class="header-right">
          <template v-if="!token">
            <el-button type="primary" @click="$router.push('/login')">登录</el-button>
          </template>
          <template v-else>
            <el-dropdown>
              <span class="el-dropdown-link" style="cursor: pointer;">
                <el-icon><User /></el-icon>
                已登录
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="$router.push('/courses')">进入课程中心</el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </div>
      </div>
    </el-header>
    <el-main class="main-content">
      <div class="content-inner">
        <h2>我的学习</h2>
        <p class="desc">仅展示您已观看过视频的课程</p>
        <template v-if="!token">
          <el-empty description="请先登录后查看学习记录">
            <el-button type="primary" @click="$router.push('/login')">去登录</el-button>
          </el-empty>
        </template>
        <template v-else>
          <el-row :gutter="20" v-loading="loading">
            <el-col :span="6" v-for="course in courseList" :key="course.id">
              <el-card class="course-card" shadow="hover" @click="$router.push(`/course/${course.id}`)">
                <img
                  :src="course.cover || 'https://via.placeholder.com/300x200'"
                  class="course-image"
                  :alt="course.title"
                />
                <div class="course-info">
                  <h3>{{ course.title }}</h3>
                  <p>{{ course.description || '暂无描述' }}</p>
                  <el-button type="primary" size="small" @click.stop="$router.push(`/course/${course.id}`)">继续学习</el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>
          <el-empty v-if="!loading && courseList.length === 0" description="暂无学习记录，去课程中心看看吧">
            <el-button type="primary" @click="$router.push('/courses')">去选课</el-button>
          </el-empty>
        </template>
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import type { Course } from '@/api/course'
import { getWatchedCourses } from '@/api/learning'

const router = useRouter()
const token = ref<string | null>(localStorage.getItem('token'))
const loading = ref(false)
const courseList = ref<Course[]>([])

const loadWatchedCourses = async () => {
  if (!token.value) return
  loading.value = true
  try {
    const list = await getWatchedCourses()
    courseList.value = Array.isArray(list) ? list : []
  } catch {
    courseList.value = []
  } finally {
    loading.value = false
  }
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  token.value = null
  courseList.value = []
  ElMessage.success('已退出登录')
  router.push('/')
}

onMounted(() => {
  token.value = localStorage.getItem('token')
  loadWatchedCourses()
})
</script>

<style scoped lang="scss">
.my-learning-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;

  .header-content {
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
    display: flex;
    align-items: center;
    padding: 0 20px;

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
  }
}

.main-content {
  flex: 1;
  background: #f5f7fa;
  padding: 40px 20px;
}

.content-inner {
  max-width: 1200px;
  margin: 0 auto;

  h2 {
    margin-bottom: 8px;
    color: #303133;
  }

  .desc {
    margin-bottom: 24px;
    font-size: 14px;
    color: #909399;
  }

  .course-card {
    margin-bottom: 20px;
    cursor: pointer;
    transition: transform 0.3s;

    &:hover {
      transform: translateY(-5px);
    }

    .course-image {
      width: 100%;
      height: 150px;
      object-fit: cover;
      margin-bottom: 15px;
    }

    .course-info {
      h3 {
        font-size: 16px;
        margin-bottom: 10px;
        color: #303133;
      }

      p {
        font-size: 14px;
        color: #909399;
        margin-bottom: 15px;
      }
    }
  }
}
</style>
