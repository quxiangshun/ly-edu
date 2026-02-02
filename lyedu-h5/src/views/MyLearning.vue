<template>
  <div class="my-learning-container">
    <van-nav-bar title="我的学习" left-arrow @click-left="$router.back()" />
    <div class="desc">仅展示您已观看过视频的课程</div>
    <template v-if="!token">
      <van-empty description="请先登录后查看学习记录">
        <van-button type="primary" round @click="$router.push('/login')">去登录</van-button>
      </van-empty>
    </template>
    <template v-else>
      <van-loading v-if="loading" class="loading" size="24px">加载中...</van-loading>
      <div v-else-if="courseList.length === 0" class="empty-wrap">
        <van-empty description="暂无学习记录，去课程中心看看吧">
          <van-button type="primary" round @click="$router.push('/courses')">去选课</van-button>
        </van-empty>
      </div>
      <div v-else class="course-list">
        <van-card
          v-for="course in courseList"
          :key="course.id"
          :title="course.title"
          :desc="course.description || '暂无描述'"
          :thumb="course.cover || 'https://via.placeholder.com/200x120'"
          @click="$router.push(`/course/${course.id}`)"
        >
          <template #tags>
            <van-tag type="primary">继续学习</van-tag>
          </template>
        </van-card>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Course } from '@/api/course'
import { getWatchedCourses } from '@/api/learning'

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
  background: #f7f8fa;
  padding-bottom: 20px;
}

.desc {
  padding: 12px 16px;
  font-size: 14px;
  color: #969799;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

.empty-wrap {
  padding-top: 40px;
}

.course-list {
  padding: 0 16px;

  :deep(.van-card) {
    margin-bottom: 12px;
    border-radius: 8px;
    overflow: hidden;
  }
}
</style>
