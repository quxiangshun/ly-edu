<template>
  <div class="video-player-container">
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
      <div v-if="video" class="video-content">
        <el-card class="video-card">
          <div class="video-wrapper">
            <video
              ref="videoPlayer"
              :src="videoUrl"
              controls
              preload="metadata"
              class="video-element"
              @loadedmetadata="handleLoadedMetadata"
              @timeupdate="handleTimeUpdate"
              @ended="handleVideoEnded"
            >
              您的浏览器不支持视频播放
            </video>
          </div>
          <div class="video-info">
            <h2>{{ video.title }}</h2>
            <div class="video-meta">
              <span v-if="video.duration" class="duration">
                <el-icon><Clock /></el-icon>
                时长: {{ formatDuration(video.duration) }}
              </span>
            </div>
          </div>
        </el-card>

        <!-- 相关视频列表 -->
        <el-card v-if="relatedVideos && relatedVideos.length > 0" class="related-videos-card">
          <template #header>
            <div class="card-header">
              <span>相关视频</span>
            </div>
          </template>
          <div class="video-list">
            <div
              v-for="(relatedVideo, index) in relatedVideos"
              :key="relatedVideo.id"
              class="video-item"
              :class="{ active: relatedVideo.id === video.id }"
              @click="handlePlayVideo(relatedVideo.id)"
            >
              <div class="video-index">{{ index + 1 }}</div>
              <div class="video-info-item">
                <h4>{{ relatedVideo.title }}</h4>
                <div class="video-meta-item">
                  <span v-if="relatedVideo.duration" class="duration">
                    <el-icon><Clock /></el-icon>
                    {{ formatDuration(relatedVideo.duration) }}
                  </span>
                </div>
              </div>
              <div class="video-action">
                <el-icon><VideoPlay /></el-icon>
              </div>
            </div>
          </div>
        </el-card>
      </div>
      <el-empty v-else description="视频不存在" />
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Clock, VideoPlay } from '@element-plus/icons-vue'
import { getVideoById } from '@/api/video'
import { getCourseById } from '@/api/course'
import type { Video } from '@/api/course'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const video = ref<Video | null>(null)
const relatedVideos = ref<Video[]>([])
const videoPlayer = ref<HTMLVideoElement | null>(null)
const currentTime = ref(0)

const videoUrl = computed(() => {
  if (!video.value?.url) return ''
  let url = video.value.url
  
  // 如果URL是相对路径，转换为完整URL
  if (url.startsWith('/')) {
    url = `http://localhost:9700${url}`
  } else if (!url.startsWith('http://') && !url.startsWith('https://')) {
    // 否则添加基础URL
    url = `http://localhost:9700/api${url}`
  }
  
  // 对URL中的中文字符进行编码
  try {
    const urlObj = new URL(url)
    // 编码路径部分的中文字符（保留斜杠）
    const pathParts = urlObj.pathname.split('/').filter(p => p)
    const encodedPath = '/' + pathParts.map(part => encodeURIComponent(part)).join('/')
    urlObj.pathname = encodedPath
    return urlObj.toString()
  } catch (e) {
    // 如果URL解析失败，尝试简单编码
    return encodeURI(url)
  }
})

const loadVideo = async () => {
  const videoId = Number(route.params.id)
  if (!videoId) {
    ElMessage.error('视频ID无效')
    router.push('/courses')
    return
  }

  loading.value = true
  try {
    const res = await getVideoById(videoId)
    video.value = res

    // 加载相关视频（同一课程的其他视频）
    if (res.courseId) {
      const courseRes = await getCourseById(res.courseId)
      relatedVideos.value = courseRes.videos || []
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '加载视频失败')
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

const handlePlayVideo = (videoId: number) => {
  router.push(`/video/${videoId}`)
}

const handleLoadedMetadata = () => {
  // 视频元数据加载完成
  if (videoPlayer.value) {
    console.log('视频时长:', videoPlayer.value.duration)
  }
}

const handleTimeUpdate = () => {
  if (videoPlayer.value) {
    currentTime.value = videoPlayer.value.currentTime
    // TODO: 可以在这里保存播放进度
  }
}

const handleVideoEnded = () => {
  ElMessage.success('视频播放完成')
  // TODO: 可以在这里更新学习进度
}

// 监听路由参数变化，当视频ID变化时重新加载
watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    loadVideo()
  }
}, { immediate: false })

// 监听视频URL变化，强制视频元素重新加载
watch(videoUrl, (newUrl, oldUrl) => {
  if (newUrl && newUrl !== oldUrl && videoPlayer.value) {
    // 暂停当前播放
    videoPlayer.value.pause()
    // 重置视频源
    videoPlayer.value.load()
  }
})

onMounted(() => {
  loadVideo()
})

onUnmounted(() => {
  // 清理资源
  if (videoPlayer.value) {
    videoPlayer.value.pause()
  }
})
</script>

<style scoped lang="scss">
.video-player-container {
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

  .video-content {
    max-width: 1200px;
    margin: 0 auto;
  }
}

.video-card {
  margin-bottom: 20px;

  .video-wrapper {
    width: 100%;
    background: #000;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 20px;

    .video-element {
      width: 100%;
      height: auto;
      max-height: 600px;
      display: block;
    }
  }

  .video-info {
    h2 {
      font-size: 24px;
      color: #303133;
      margin-bottom: 15px;
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
}

.related-videos-card {
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

      &.active {
        background-color: #e6f7ff;
        border-left: 3px solid #409eff;
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

      .video-info-item {
        flex: 1;

        h4 {
          font-size: 16px;
          color: #303133;
          margin-bottom: 8px;
        }

        .video-meta-item {
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
