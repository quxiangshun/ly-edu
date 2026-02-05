<template>
  <div class="my-liked-container">
    <van-nav-bar title="我点赞的视频" left-arrow @click-left="$router.back()" />

    <template v-if="!token">
      <van-empty description="请先登录后查看点赞视频">
        <van-button type="primary" round @click="$router.push('/login')">去登录</van-button>
      </van-empty>
    </template>
    <template v-else>
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <div v-if="list.length === 0 && !loading" class="empty-wrap">
          <van-empty description="暂无点赞视频，去课程里给喜欢的视频点个赞吧">
            <van-button type="primary" round @click="$router.push('/courses')">去课程中心</van-button>
          </van-empty>
        </div>
        <div v-else class="video-list">
          <div
            v-for="item in list"
            :key="item.id"
            class="video-card"
            @click="$router.push(`/video/${item.id}`)"
          >
            <div class="video-thumb">
              <van-image
                width="100%"
                height="120"
                fit="cover"
                :src="coverUrl(item.cover)"
                radius="8"
              >
                <template v-if="item.duration" #default>
                  <div class="duration-tag">{{ formatDuration(item.duration) }}</div>
                </template>
              </van-image>
            </div>
            <div class="video-body">
              <div class="video-title">{{ item.title }}</div>
              <div class="video-meta">
                <span><van-icon name="play-circle-o" size="14" /> {{ item.playCount ?? 0 }} 次</span>
                <span><van-icon name="good-job" size="14" /> {{ item.likeCount ?? 0 }} 赞</span>
              </div>
            </div>
          </div>
        </div>
      </van-list>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getLikedVideos } from '@/api/video'
import type { Video } from '@/api/course'

const token = ref<string | null>(localStorage.getItem('token'))
const list = ref<Video[]>([])
const loading = ref(false)
const finished = ref(false)
const page = ref(1)
const size = 10

function coverUrl(cover?: string) {
  if (!cover) return 'https://via.placeholder.com/320x120?text=视频'
  if (cover.startsWith('http')) return cover
  const base = window.location.origin + '/api'
  return cover.startsWith('/') ? base + cover : base + '/' + cover
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

async function onLoad() {
  if (!token.value) {
    finished.value = true
    return
  }
  loading.value = true
  try {
    const res = await getLikedVideos({ page: page.value, size })
    const records = res?.records ?? []
    list.value.push(...records)
    if (records.length < size) {
      finished.value = true
    } else {
      page.value += 1
    }
  } catch {
    finished.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  token.value = localStorage.getItem('token')
})
</script>

<style scoped lang="scss">
.my-liked-container {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 20px;
}

.empty-wrap {
  padding: 60px 0;
}

.video-list {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.video-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: opacity 0.2s;
  &:active {
    opacity: 0.9;
  }
}

.video-thumb {
  position: relative;
  background: #000;
  .duration-tag {
    position: absolute;
    right: 6px;
    bottom: 6px;
    padding: 2px 6px;
    border-radius: 4px;
    background: rgba(0, 0, 0, 0.6);
    color: #fff;
    font-size: 12px;
  }
}

.video-body {
  padding: 10px 12px;
  .video-title {
    font-size: 15px;
    color: #323233;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-bottom: 6px;
  }
  .video-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 12px;
    color: #969799;
  }
}
</style>
