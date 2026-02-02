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
            <div class="course-tags">
              <van-tag v-if="courseDetail.course.isRequired === 1" type="danger" plain>必修</van-tag>
              <van-tag v-else-if="courseDetail.course.isRequired === 0" type="primary" plain>选修</van-tag>
            </div>
            <p class="course-description">{{ courseDetail.course.description || '暂无描述' }}</p>
            <div class="course-meta-row">
              <van-circle
                v-if="courseDetail.courseProgress != null"
                :rate="courseDetail.courseProgress"
                :size="72"
                :stroke-width="6"
                layer-color="#ebedf0"
                color="#1989fa"
                class="progress-ring"
              />
              <van-button type="primary" block @click="handleStartLearn" class="start-btn">开始学习</van-button>
            </div>
          </div>
        </div>

        <!-- 标签：课程目录 / 课程附件 -->
        <div v-if="hasChaptersOrAttachments" class="tabs-section">
          <van-tabs v-model:active="activeTab">
            <van-tab title="课程目录" name="catalog">
              <div v-if="courseDetail.chapters && courseDetail.chapters.length > 0" class="chapter-list">
                <div v-for="(chapter, chIndex) in courseDetail.chapters" :key="chapter.id ?? 'uncat-' + chIndex" class="chapter-block">
                  <div class="chapter-title">{{ chapter.title }}</div>
                  <van-cell-group>
                    <van-cell
                      v-for="(video, index) in chapter.hours"
                      :key="video.id"
                      :title="`${index + 1}. ${video.title}`"
                      :label="videoLabel(video)"
                      is-link
                      @click="handlePlayVideo(video)"
                    >
                      <template #icon>
                        <van-icon name="play-circle-o" size="20" color="#1989fa" style="margin-right: 8px" />
                      </template>
                    </van-cell>
                  </van-cell-group>
                </div>
              </div>
              <div v-else-if="courseDetail.videos && courseDetail.videos.length > 0" class="videos-section">
                <van-cell-group>
                  <van-cell
                    v-for="(video, index) in courseDetail.videos"
                    :key="video.id"
                    :title="`${index + 1}. ${video.title}`"
                    :label="videoLabel(video)"
                    is-link
                    @click="handlePlayVideo(video)"
                  >
                    <template #icon>
                      <van-icon name="play-circle-o" size="20" color="#1989fa" style="margin-right: 8px" />
                    </template>
                  </van-cell>
                </van-cell-group>
              </div>
              <van-empty v-else description="暂无课时" />
            </van-tab>
            <van-tab title="课程附件" name="attachments">
              <div v-if="courseDetail.attachments && courseDetail.attachments.length > 0" class="attachment-list">
                <van-cell
                  v-for="att in courseDetail.attachments"
                  :key="att.id"
                  :title="att.name"
                  is-link
                  @click="handleDownloadAttachment(att)"
                >
                  <template #icon>
                    <van-icon name="description" size="20" color="#969799" style="margin-right: 8px" />
                  </template>
                </van-cell>
              </div>
              <van-empty v-else description="暂无附件" />
            </van-tab>
          </van-tabs>
        </div>

        <!-- 无章节/附件时保留原扁平视频列表 -->
        <div v-else-if="courseDetail.videos && courseDetail.videos.length > 0" class="videos-section">
          <div class="section-title">课程视频 ({{ courseDetail.videos.length }})</div>
          <van-cell-group>
            <van-cell
              v-for="(video, index) in courseDetail.videos"
              :key="video.id"
              :title="`${index + 1}. ${video.title}`"
              :label="videoLabel(video)"
              is-link
              @click="handlePlayVideo(video)"
            >
              <template #icon>
                <van-icon name="play-circle-o" size="20" color="#1989fa" style="margin-right: 8px" />
              </template>
            </van-cell>
          </van-cell-group>
        </div>

        <van-empty v-else-if="!hasChaptersOrAttachments" description="暂无视频" />

        <!-- 操作按钮（无 tabs 时显示） -->
        <div v-if="!hasChaptersOrAttachments" class="action-buttons">
          <van-button type="primary" block @click="handleStartLearn">开始学习</van-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showSuccessToast, showFailToast } from 'vant'
import { getCourseById, type CourseDetail, type CourseAttachment } from '@/api/course'
import { joinCourse } from '@/api/learning'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const courseDetail = ref<CourseDetail | null>(null)
const activeTab = ref('catalog')

const hasChaptersOrAttachments = computed(() => {
  const d = courseDetail.value
  if (!d) return false
  const hasChapters = d.chapters && d.chapters.length > 0
  const hasAttachments = d.attachments && d.attachments.length > 0
  return hasChapters || hasAttachments
})

function getLearnRecord(videoId: number) {
  const d = courseDetail.value
  if (!d?.learnRecord) return null
  return d.learnRecord[String(videoId)] ?? d.learnRecord[videoId] ?? null
}

function videoLabel(video: { id: number; duration?: number }): string {
  const parts: string[] = []
  if (video.duration) parts.push(formatDuration(video.duration))
  const rec = getLearnRecord(video.id)
  if (rec) parts.push(`已看 ${formatDuration(rec.progress)} / ${formatDuration(rec.duration)}`)
  return parts.join(' · ')
}

function handleDownloadAttachment(att: CourseAttachment) {
  if (!att.fileUrl) {
    showFailToast('附件地址无效')
    return
  }
  const ext = (att.type || '').toLowerCase()
  if (ext === 'txt' || att.name?.toLowerCase().endsWith('.txt')) {
    fetch(att.fileUrl)
      .then(r => r.blob())
      .then(blob => {
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = att.name || 'download.txt'
        a.click()
        URL.revokeObjectURL(url)
        showSuccessToast('下载成功')
      })
      .catch(() => showFailToast('下载失败'))
  } else {
    window.open(att.fileUrl, '_blank')
  }
}

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
    router.push({ path: '/login', query: { redirect: `/course/${route.params.id}` } })
    return
  }

  try {
    await joinCourse(courseDetail.value.course.id)
    showSuccessToast('已加入课程')
    const vids = courseDetail.value.videos
    const firstInChapter = courseDetail.value.chapters?.[0]?.hours?.[0]
    if (firstInChapter) {
      handlePlayVideo(firstInChapter)
    } else if (vids && vids.length > 0) {
      handlePlayVideo(vids[0])
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
      margin-bottom: 6px;
    }

    .course-tags {
      margin-bottom: 8px;
    }

    .course-description {
      font-size: 14px;
      color: #969799;
      line-height: 1.6;
      margin-bottom: 10px;
    }

    .course-meta-row {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-top: 12px;

      .progress-ring {
        flex-shrink: 0;
      }

      .start-btn {
        flex: 1;
      }
    }
  }
}

.tabs-section {
  background: #fff;
  border-radius: 8px;
  padding: 0 15px 15px;
  margin-bottom: 10px;

  .chapter-list {
    .chapter-block {
      margin-bottom: 16px;

      .chapter-title {
        font-size: 15px;
        font-weight: 600;
        color: #323233;
        margin-bottom: 10px;
        padding-bottom: 6px;
        border-bottom: 1px solid #ebedf0;
      }
    }
  }

  .attachment-list {
    margin-top: 10px;
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
