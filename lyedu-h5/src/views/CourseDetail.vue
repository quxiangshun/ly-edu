<template>
  <div class="course-detail-container">
    <van-nav-bar title="课程详情" left-arrow @click-left="$router.back()" fixed placeholder />
    
    <div v-loading="loading" class="content">
      <div v-if="courseDetail">
        <!-- 课程信息 -->
        <div class="course-header">
          <img
            :src="courseDetail.course.cover || 'https://via.placeholder.com/400x250'"
            class="course-cover"
            :alt="courseDetail.course.title"
          />
          <div class="course-info">
            <h1>{{ courseDetail.course.title }}</h1>
            <p class="course-description">{{ courseDetail.course.description || '暂无描述' }}</p>
          </div>
        </div>

        <!-- 视频列表 -->
        <div v-if="courseDetail.videos && courseDetail.videos.length > 0" class="videos-section">
          <div class="section-title">课程视频 ({{ courseDetail.videos.length }})</div>
          <van-cell-group>
            <van-cell
              v-for="(video, index) in courseDetail.videos"
              :key="video.id"
              :title="`${index + 1}. ${video.title}`"
              :label="video.duration ? formatDuration(video.duration) : ''"
              is-link
              @click="handlePlayVideo(video)"
            >
              <template #icon>
                <van-icon name="play-circle-o" size="20" color="#1989fa" style="margin-right: 8px" />
              </template>
            </van-cell>
          </van-cell-group>
        </div>

        <van-empty v-else description="暂无视频" />

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <van-button type="primary" block @click="handleStartLearn">开始学习</van-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showSuccessToast, showFailToast } from 'vant'
import { getCourseById, type CourseDetail } from '@/api/course'
import { joinCourse } from '@/api/learning'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const courseDetail = ref<CourseDetail | null>(null)

const loadCourseDetail = async () => {
  const courseId = Number(route.params.id)
  if (!courseId) {
    showFailToast('课程ID无效')
    router.back()
    return
  }

  loading.value = true
  try {
    const res = await getCourseById(courseId)
    courseDetail.value = res
  } catch (e: any) {
    showFailToast(e?.response?.data?.message || '加载课程详情失败')
    router.back()
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
    showFailToast('请先登录')
    router.push('/login')
    return
  }

  try {
    await joinCourse(courseDetail.value.course.id)
    showSuccessToast('已加入课程')
    // 如果有视频，跳转到第一个视频
    if (courseDetail.value.videos && courseDetail.value.videos.length > 0) {
      handlePlayVideo(courseDetail.value.videos[0])
    }
  } catch (e: any) {
    showFailToast(e?.response?.data?.message || '加入课程失败')
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
  background: #f7f8fa;
}

.content {
  padding: 10px;
}

.course-header {
  background: #fff;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 10px;

  .course-cover {
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 15px;
  }

  .course-info {
    h1 {
      font-size: 20px;
      color: #323233;
      margin-bottom: 10px;
    }

    .course-description {
      font-size: 14px;
      color: #969799;
      line-height: 1.6;
    }
  }
}

.videos-section {
  background: #fff;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 10px;

  .section-title {
    font-size: 16px;
    font-weight: 500;
    color: #323233;
    margin-bottom: 15px;
  }
}

.action-buttons {
  padding: 15px 0;
}
</style>
