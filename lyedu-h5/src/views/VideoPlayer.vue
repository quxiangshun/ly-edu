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
      <div v-if="video" class="video-content">
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

        <div class="video-info">
          <h2>{{ video.title }}</h2>
          <div class="video-meta" v-if="video.duration">
            <van-icon name="clock-o" />
            <span>时长: {{ formatDuration(video.duration) }}</span>
          </div>
        </div>

        <!-- 相关视频列表 -->
        <div v-if="relatedVideos && relatedVideos.length > 0" class="related-videos-section">
          <div class="section-title">相关视频</div>
          <van-cell-group>
            <van-cell
              v-for="(relatedVideo, index) in relatedVideos"
              :key="relatedVideo.id"
              :title="`${index + 1}. ${relatedVideo.title}`"
              :label="relatedVideo.duration ? formatDuration(relatedVideo.duration) : ''"
              is-link
              :class="{ active: relatedVideo.id === video.id }"
              @click="handlePlayVideo(relatedVideo.id)"
            >
              <template #icon>
                <van-icon
                  name="play-circle-o"
                  size="20"
                  color="#1989fa"
                  style="margin-right: 8px"
                />
              </template>
            </van-cell>
          </van-cell-group>
        </div>
      </div>
      <van-empty v-else description="视频不存在" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
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
    }
  } catch (e: any) {
    showFailToast(e?.response?.data?.message || '加载视频失败')
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
  showSuccessToast('视频播放完成')
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
  background: #f7f8fa;
}

.content {
  padding: 10px;
}

.video-content {
  .video-wrapper {
    width: 100%;
    background: #000;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 15px;

    .video-element {
      width: 100%;
      height: auto;
      display: block;
    }
  }

  .video-info {
    background: #fff;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;

    h2 {
      font-size: 18px;
      color: #323233;
      margin-bottom: 10px;
    }

    .video-meta {
      display: flex;
      align-items: center;
      gap: 5px;
      font-size: 14px;
      color: #969799;
    }
  }
}

.related-videos-section {
  background: #fff;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;

  .section-title {
    font-size: 16px;
    font-weight: 500;
    color: #323233;
    margin-bottom: 15px;
  }

  :deep(.van-cell) {
    &.active {
      background-color: #e6f7ff;
    }
  }
}
</style>
