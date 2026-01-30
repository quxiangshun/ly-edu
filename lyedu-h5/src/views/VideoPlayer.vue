<template>
  <div class="video-player-container">
    <van-nav-bar
      :title="video?.title || '视频播放'"
      left-arrow
      @click-left="$router.back()"
      fixed
      placeholder
    />

    <div v-loading="loading" class="content">
      <div v-if="video && relatedVideos.length > 0" class="video-content">
        <!-- 视频播放器 -->
        <div class="video-wrapper">
          <video
            ref="videoPlayer"
            :src="videoUrl"
            controls
            preload="metadata"
            class="video-element"
            playsinline
            webkit-playsinline
            x5-playsinline
            @loadedmetadata="handleLoadedMetadata"
            @timeupdate="handleTimeUpdate"
            @ended="handleVideoEnded"
          >
            您的浏览器不支持视频播放
          </video>
        </div>

        <!-- 视频信息 -->
        <div class="video-info">
          <h2>{{ video.title }}</h2>
          <div class="video-meta" v-if="video.duration">
            <van-icon name="clock-o" />
            <span>时长: {{ formatDuration(video.duration) }}</span>
          </div>
        </div>

        <!-- 可滚动视频列表 -->
        <div class="video-list-section">
          <div class="section-header">
            <span class="section-title">视频列表</span>
            <span class="video-count">{{ relatedVideos.length }} 个视频</span>
          </div>
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
                <div class="video-meta-item" v-if="relatedVideo.duration">
                  <van-icon name="clock-o" size="12" />
                  <span>{{ formatDuration(relatedVideo.duration) }}</span>
                </div>
              </div>
              <div class="video-action" v-if="relatedVideo.id === video.id">
                <van-icon name="play-circle-o" size="18" color="#1989fa" />
              </div>
            </div>
          </div>
        </div>
      </div>
      <van-empty v-else description="视频不存在" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showSuccessToast, showFailToast } from 'vant'
import { getVideoById } from '@/api/video'
import { getCourseById } from '@/api/course'
import type { Video } from '@/api/course'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const video = ref<Video | null>(null)
const relatedVideos = ref<Video[]>([])
const videoPlayer = ref<HTMLVideoElement | null>(null)
const videoListRef = ref<HTMLElement | null>(null)
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
    showFailToast('视频ID无效')
    router.back()
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
      
      // 等待DOM更新后，滚动到当前视频项
      await nextTick()
      scrollToCurrentVideo()
    }
  } catch (e: any) {
    showFailToast(e?.response?.data?.message || '加载视频失败')
    router.back()
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

const handleTimeUpdate = () => {
  if (videoPlayer.value) {
    currentTime.value = videoPlayer.value.currentTime
    // TODO: 可以在这里保存播放进度
  }
}

const handleVideoEnded = async () => {
  if (!video.value || !relatedVideos.value.length) return
  
  // 找到当前视频在列表中的索引
  const currentIndex = relatedVideos.value.findIndex(v => v.id === video.value!.id)
  
  // 如果还有下一个视频，自动播放
  if (currentIndex >= 0 && currentIndex < relatedVideos.value.length - 1) {
    const nextVideo = relatedVideos.value[currentIndex + 1]
    showSuccessToast('播放完成，即将播放下一集')
    
    // 延迟一下再切换，让用户看到提示
    setTimeout(() => {
      handlePlayVideo(nextVideo.id)
    }, 500)
  } else {
    showSuccessToast('视频播放完成，已是最后一集')
  }
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
    videoPlayer.value.pause()
    videoPlayer.value.load()
  }
})

onMounted(() => {
  loadVideo()
})

onUnmounted(() => {
  if (videoPlayer.value) {
    videoPlayer.value.pause()
    videoPlayer.value = null
  }
})
</script>

<style scoped lang="scss">
.video-player-container {
  height: 100vh;
  background: #f7f8fa;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.content {
  flex: 1;
  min-height: 0;
  padding: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.video-content {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;

  .video-wrapper {
    width: 100%;
    height: 220px;
    flex-shrink: 0;
    background: #000;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 10px;
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
    flex-shrink: 0;
    background: #fff;
    border-radius: 8px;
    padding: 10px 15px;
    margin-bottom: 10px;

    h2 {
      font-size: 16px;
      color: #323233;
      margin-bottom: 6px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .video-meta {
      display: flex;
      align-items: center;
      gap: 5px;
      font-size: 13px;
      color: #969799;
    }
  }
}

.video-list-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  padding: 10px 15px;

  .section-header {
    flex-shrink: 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;

    .section-title {
      font-size: 16px;
      font-weight: 500;
      color: #323233;
    }

    .video-count {
      font-size: 13px;
      color: #969799;
    }
  }

  .video-list {
    flex: 1;
    min-height: 0;
    overflow-y: auto;

    .video-item {
      display: flex;
      align-items: center;
      padding: 12px;
      border-bottom: 1px solid #f0f0f0;
      cursor: pointer;
      transition: background-color 0.3s;

      &:hover {
        background-color: #f5f7fa;
      }

      &.active {
        background-color: #e6f7ff;
        border-left: 3px solid #1989fa;
      }

      &:last-child {
        border-bottom: none;
      }

      .video-index {
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f0f0f0;
        border-radius: 50%;
        font-weight: 500;
        font-size: 13px;
        color: #606266;
        margin-right: 10px;
        flex-shrink: 0;
      }

      &.active .video-index {
        background: #1989fa;
        color: #fff;
      }

      .video-info-item {
        flex: 1;
        min-width: 0;

        h4 {
          font-size: 14px;
          color: #323233;
          margin-bottom: 6px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .video-meta-item {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          color: #969799;
        }
      }

      .video-action {
        margin-left: 8px;
        flex-shrink: 0;
      }
    }
  }
}

// 滚动条样式
.video-list {
  &::-webkit-scrollbar {
    width: 4px;
  }

  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 2px;
  }

  &::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 2px;

    &:hover {
      background: #a8a8a8;
    }
  }
}
</style>
