<template>
  <div class="my-learning-container">
    <AppHeader />
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
            <el-col :span="6" v-for="item in courseList" :key="item.course.id">
              <el-card class="course-card" shadow="hover" @click="$router.push(`/course/${item.course.id}`)">
                <img
                  :src="item.course.cover || 'https://via.placeholder.com/300x200'"
                  class="course-image"
                  :alt="item.course.title"
                />
                <div class="course-info">
                  <h3>{{ item.course.title }}</h3>
                  <p>{{ item.course.description || '暂无描述' }}</p>
                  <div class="progress-row">
                    <el-progress
                      :percentage="item.progress ?? 0"
                      :stroke-width="8"
                      :show-text="true"
                    />
                  </div>
                  <el-button type="primary" size="small" @click.stop="$router.push(`/course/${item.course.id}`)">继续学习</el-button>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
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

.main-content {
  flex: 1;
  background: #f5f7fa;
  padding: 40px 20px;
  margin-top: 60px;
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
      .progress-row {
        margin: 10px 0;
      }

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
