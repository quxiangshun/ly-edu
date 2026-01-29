<template>
  <div class="course-detail-container">
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <h1>LyEdu</h1>
        </div>
        <el-menu mode="horizontal" default-active="courses" class="header-menu">
          <el-menu-item index="home" @click="$router.push('/')">首页</el-menu-item>
          <el-menu-item index="courses" @click="$router.push('/courses')">课程中心</el-menu-item>
          <el-menu-item index="my">我的学习</el-menu-item>
        </el-menu>
      </div>
    </el-header>
    <el-main class="main-content" v-loading="loading">
      <div v-if="courseDetail" class="course-detail-content">
        <!-- 课程信息 -->
        <el-card class="course-info-card">
          <div class="course-header">
            <img
              :src="courseDetail.course.cover || 'https://via.placeholder.com/400x250'"
              class="course-cover"
              :alt="courseDetail.course.title"
            />
            <div class="course-info">
              <h1>{{ courseDetail.course.title }}</h1>
              <p class="course-description">{{ courseDetail.course.description || '暂无描述' }}</p>
              <div class="course-actions">
                <el-button type="primary" size="large" @click="handleStartLearn">
                  开始学习
                </el-button>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 视频列表 -->
        <el-card class="videos-card" v-if="courseDetail.videos && courseDetail.videos.length > 0">
          <template #header>
            <div class="card-header">
              <span>课程视频 ({{ courseDetail.videos.length }})</span>
            </div>
          </template>
          <div class="video-list">
            <div
              v-for="(video, index) in courseDetail.videos"
              :key="video.id"
              class="video-item"
              @click="handlePlayVideo(video)"
            >
              <div class="video-index">{{ index + 1 }}</div>
              <div class="video-info">
                <h4>{{ video.title }}</h4>
                <div class="video-meta">
                  <span v-if="video.duration" class="duration">
                    <el-icon><Clock /></el-icon>
                    {{ formatDuration(video.duration) }}
                  </span>
                </div>
              </div>
              <div class="video-action">
                <el-icon><VideoPlay /></el-icon>
              </div>
            </div>
          </div>
        </el-card>

        <el-empty v-else description="暂无视频" />
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Clock, VideoPlay } from '@element-plus/icons-vue'
import { getCourseById, type CourseDetail } from '@/api/course'
import { joinCourse } from '@/api/learning'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const courseDetail = ref<CourseDetail | null>(null)

const loadCourseDetail = async () => {
  const courseId = Number(route.params.id)
  if (!courseId) {
    ElMessage.error('课程ID无效')
    router.push('/courses')
    return
  }

  loading.value = true
  try {
    const res = await getCourseById(courseId)
    courseDetail.value = res
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '加载课程详情失败')
    router.push('/courses')
  } finally {
    loading.value = false
  }
}

const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

const handleStartLearn = async () => {
  if (!courseDetail.value) return
  
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    await joinCourse(courseDetail.value.course.id)
    ElMessage.success('已加入课程')
    // 如果有视频，跳转到第一个视频
    if (courseDetail.value.videos && courseDetail.value.videos.length > 0) {
      handlePlayVideo(courseDetail.value.videos[0])
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '加入课程失败')
  }
}

const handlePlayVideo = (video: any) => {
  router.push(`/video/${video.id}`)
}

onMounted(() => {
  loadCourseDetail()
})
</script>

<style scoped lang="scss">
.course-detail-container {
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
      cursor: pointer;
      h1 {
        color: #667eea;
        font-size: 24px;
        margin: 0;
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

  .course-detail-content {
    max-width: 1200px;
    margin: 0 auto;
  }
}

.course-info-card {
  margin-bottom: 20px;

  .course-header {
    display: flex;
    gap: 30px;

    .course-cover {
      width: 400px;
      height: 250px;
      object-fit: cover;
      border-radius: 8px;
    }

    .course-info {
      flex: 1;

      h1 {
        font-size: 28px;
        color: #303133;
        margin-bottom: 15px;
      }

      .course-description {
        font-size: 16px;
        color: #606266;
        line-height: 1.6;
        margin-bottom: 30px;
      }

      .course-actions {
        margin-top: 20px;
      }
    }
  }
}

.videos-card {
  .card-header {
    font-size: 18px;
    font-weight: 500;
    color: #303133;
  }

  .video-list {
    .video-item {
      display: flex;
      align-items: center;
      padding: 15px;
      border-bottom: 1px solid #f0f0f0;
      cursor: pointer;
      transition: background-color 0.3s;

      &:hover {
        background-color: #f5f7fa;
      }

      &:last-child {
        border-bottom: none;
      }

      .video-index {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f0f0f0;
        border-radius: 50%;
        font-weight: 500;
        color: #606266;
        margin-right: 15px;
      }

      .video-info {
        flex: 1;

        h4 {
          font-size: 16px;
          color: #303133;
          margin-bottom: 8px;
        }

        .video-meta {
          display: flex;
          align-items: center;
          gap: 15px;
          font-size: 14px;
          color: #909399;

          .duration {
            display: flex;
            align-items: center;
            gap: 5px;
          }
        }
      }

      .video-action {
        color: #409eff;
        font-size: 24px;
      }
    }
  }
}
</style>
