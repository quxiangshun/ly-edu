<template>
  <div class="video-player-container">
    <AppHeader />
    <el-main class="main-content" v-loading="loading">
      <div v-if="video && relatedVideos.length > 0" class="video-layout">
        <!-- 左侧：固定视频播放器 -->
        <div class="video-section">
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
                @seeking="handleSeeking"
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
        </div>

        <!-- 右侧：可滚动视频列表 -->
        <div class="video-list-section">
          <el-card class="video-list-card">
            <template #header>
              <div class="card-header">
                <span>视频列表</span>
                <span class="video-count">{{ relatedVideos.length }} 个视频</span>
              </div>
            </template>
            <div class="video-list" ref="videoListRef">
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
                  <el-icon v-if="relatedVideo.id === video.id"><VideoPlay /></el-icon>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
      <el-empty v-else description="视频不存在" />
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Clock, VideoPlay } from '@element-plus/icons-vue'
import AppHeader from '@/components/AppHeader.vue'
import { getVideoById } from '@/api/video'
import { getCourseById } from '@/api/course'
import { updateVideoProgress, playPing } from '@/api/learning'
import type { Video } from '@/api/course'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const video = ref<Video | null>(null)
const relatedVideos = ref<Video[]>([])
const videoPlayer = ref<HTMLVideoElement | null>(null)
const videoListRef = ref<HTMLElement | null>(null)
const currentTime = ref(0)
const lastProgressSaveAt = ref(0)
const hasSavedMinProgress = ref(false)
const lastValidCurrentTime = ref(0)
const playerDisableSeek = ref(false)
const playerDisableSpeed = ref(false)
const PROGRESS_SAVE_INTERVAL_MS = 5000
const MIN_PROGRESS_TO_COUNT_AS_WATCHED = 1
const PLAY_PING_INTERVAL_MS = 30000
const playPingTimerRef = ref<ReturnType<typeof setInterval> | null>(null)

const videoUrl = computed(() => {
  if (!video.value?.url) return ''
  let url = video.value.url
  const apiBase = window.location.origin + '/api'
  // 相对路径转为完整URL（适配Docker/多环境）
  if (url.startsWith('/')) {
    url = apiBase + url
  } else if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = apiBase + (url.startsWith('/') ? url : '/' + url)
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

  if (playPingTimerRef.value) {
    clearInterval(playPingTimerRef.value)
    playPingTimerRef.value = null
  }
  loading.value = true
  try {
    const res = await getVideoById(videoId)
    video.value = res

    // 加载相关视频（同一课程的其他视频）
    if (res.courseId) {
      const courseRes = await getCourseById(res.courseId)
      relatedVideos.value = courseRes.videos || []
      
      // 等待DOM更新后，滚动到当前视频项
      await nextTick()
      scrollToCurrentVideo()
    }
    // 防挂机：播放过程中心跳上报（每 30 秒）
    if (localStorage.getItem('token')) {
      playPingTimerRef.value = setInterval(() => {
        const el = videoPlayer.value
        const v = video.value
        if (el && !el.paused && el.currentTime >= MIN_PROGRESS_TO_COUNT_AS_WATCHED && v) {
          playPing(v.id).catch(() => {})
        }
      }, PLAY_PING_INTERVAL_MS)
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '加载视频失败')
    router.push('/courses')
  } finally {
    loading.value = false
  }
}

const scrollToCurrentVideo = () => {
  if (!videoListRef.value || !video.value) return
  
  const activeItem = videoListRef.value.querySelector('.video-item.active')
  if (activeItem) {
    activeItem.scrollIntoView({ behavior: 'smooth', block: 'center' })
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
  // 使用 replace 而不是 push，避免历史记录过多
  router.replace(`/video/${videoId}`)
}

const handleLoadedMetadata = () => {
  if (videoPlayer.value) {
    console.log('视频时长:', videoPlayer.value.duration)
  }
}

const saveProgressIfNeeded = () => {
  const token = localStorage.getItem('token')
  if (!token || !video.value || !videoPlayer.value) return
  const progress = Math.floor(videoPlayer.value.currentTime)
  const duration = Math.floor(videoPlayer.value.duration)
  if (!Number.isFinite(progress) || !Number.isFinite(duration) || duration <= 0) return
  if (progress < MIN_PROGRESS_TO_COUNT_AS_WATCHED) return
  const now = Date.now()
  // 至少播放 1 秒时立即保存一次，这样「我的学习」能马上出现
  if (!hasSavedMinProgress.value) {
    hasSavedMinProgress.value = true
    lastProgressSaveAt.value = now
    updateVideoProgress(video.value.id, progress, duration).catch(() => {})
    return
  }
  if (now - lastProgressSaveAt.value < PROGRESS_SAVE_INTERVAL_MS) return
  lastProgressSaveAt.value = now
  updateVideoProgress(video.value.id, progress, duration).catch(() => {})
}

const handleTimeUpdate = () => {
  if (videoPlayer.value) {
    currentTime.value = videoPlayer.value.currentTime
    lastValidCurrentTime.value = videoPlayer.value.currentTime
    if (playerDisableSpeed.value && videoPlayer.value.playbackRate !== 1) {
      videoPlayer.value.playbackRate = 1
    }
    saveProgressIfNeeded()
  }
}

const handleSeeking = () => {
  if (!videoPlayer.value || !playerDisableSeek.value) return
  videoPlayer.value.currentTime = lastValidCurrentTime.value
}

const handleVideoEnded = async () => {
  if (!video.value || !relatedVideos.value.length) return
  
  // 找到当前视频在列表中的索引
  const currentIndex = relatedVideos.value.findIndex(v => v.id === video.value!.id)
  
  // 如果还有下一个视频，自动播放
  if (currentIndex >= 0 && currentIndex < relatedVideos.value.length - 1) {
    const nextVideo = relatedVideos.value[currentIndex + 1]
    ElMessage.success('播放完成，即将播放下一集')
    
    // 延迟一下再切换，让用户看到提示
    setTimeout(() => {
      handlePlayVideo(nextVideo.id)
    }, 500)
  } else {
    ElMessage.success('视频播放完成，已是最后一集')
  }
}

// 监听路由参数变化，当视频ID变化时重新加载
watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    hasSavedMinProgress.value = false
    loadVideo()
  }
}, { immediate: false })

// 监听视频URL变化，强制视频元素重新加载
watch(videoUrl, (newUrl, oldUrl) => {
  if (newUrl && newUrl !== oldUrl && videoPlayer.value) {
    videoPlayer.value.pause()
    videoPlayer.value.load()
  }
})

onMounted(() => {
  loadVideo()
})

onUnmounted(() => {
  if (playPingTimerRef.value) {
    clearInterval(playPingTimerRef.value)
    playPingTimerRef.value = null
  }
  if (videoPlayer.value && video.value && localStorage.getItem('token')) {
    const progress = Math.floor(videoPlayer.value.currentTime)
    const duration = Math.floor(videoPlayer.value.duration)
    if (Number.isFinite(progress) && Number.isFinite(duration) && progress >= MIN_PROGRESS_TO_COUNT_AS_WATCHED) {
      updateVideoProgress(video.value.id, progress, duration).catch(() => {})
    }
  }
  if (videoPlayer.value) {
    videoPlayer.value.pause()
    videoPlayer.value = null
  }
})
</script>

<style scoped lang="scss">
.video-player-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  /* 统一 Chrome/Edge 布局计算，避免偏移 */
  position: relative;
  width: 100%;

  // 强制主内容区不出现滚动条（覆盖 Element Plus el-main 默认行为）
  :deep(.main-content) {
    overflow: hidden !important;
    min-height: 0 !important;
    display: flex !important;
    flex-direction: column !important;
  }
}

.main-content {
  flex: 1;
  min-height: 0;
  background: #f5f7fa;
  padding: 20px;
  overflow: hidden !important;
  display: flex;
  flex-direction: column;
  margin-top: 60px;
}

.video-layout {
  display: flex;
  gap: 20px;
  flex: 1 1 0;
  min-height: 0;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  overflow: hidden;
}

.video-section {
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.video-card {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;

  // el-card 内部 body 参与 flex 收缩，避免撑高整页
  :deep(.el-card__body) {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .video-wrapper {
    width: 100%;
    height: 420px;
    flex-shrink: 0;
    background: #000;
    border-radius: 8px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;

    .video-element {
      height: 100%;
      width: auto;
      max-width: 100%;
      display: block;
      object-fit: contain;
    }
  }

  .video-info {
    height: 72px;
    flex-shrink: 0;
    padding: 12px 0 0 0;
    overflow: hidden;

    h2 {
      font-size: 24px;
      color: #303133;
      margin-bottom: 8px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
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

.video-list-section {
  width: 380px;
  flex: 0 0 380px;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.video-list-card {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;

  // el-card 内部：header 固定，body 可滚动
  :deep(.el-card__body) {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 18px;
    font-weight: 500;
    color: #303133;

    .video-count {
      font-size: 14px;
      font-weight: normal;
      color: #909399;
    }
  }

  .video-list {
    flex: 1;
    min-height: 0;
    /* 始终预留滚动条空间，避免 Chrome 与 Edge 显示偏移 */
    overflow-y: scroll;
    scrollbar-gutter: stable;
    padding: 0;
    margin: 0;

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
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f0f0f0;
        border-radius: 50%;
        font-weight: 500;
        font-size: 14px;
        color: #606266;
        margin-right: 12px;
        flex-shrink: 0;
      }

      &.active .video-index {
        background: #409eff;
        color: #fff;
      }

      .video-info-item {
        flex: 1;
        min-width: 0;

        h4 {
          font-size: 15px;
          color: #303133;
          margin-bottom: 6px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .video-meta-item {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 13px;
          color: #909399;

          .duration {
            display: flex;
            align-items: center;
            gap: 4px;
          }
        }
      }

      .video-action {
        color: #409eff;
        font-size: 20px;
        margin-left: 10px;
        flex-shrink: 0;
      }
    }
  }
}

// 滚动条样式
.video-list {
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;

    &:hover {
      background: #a8a8a8;
    }
  }
}
</style>
