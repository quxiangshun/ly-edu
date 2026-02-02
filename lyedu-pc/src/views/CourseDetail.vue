<template>
  <div class="course-detail-container">
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <img src="/icon-192.png" alt="" class="header-logo-icon" />
          <h1>LyEdu</h1>
        </div>
        <el-menu mode="horizontal" default-active="courses" class="header-menu">
          <el-menu-item index="home" @click="$router.push('/')">首页</el-menu-item>
          <el-menu-item index="courses" @click="$router.push('/courses')">课程中心</el-menu-item>
          <el-menu-item index="my" @click="$router.push('/my-learning')">我的学习</el-menu-item>
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
              <div class="course-tags">
                <el-tag v-if="courseDetail.course.isRequired === 1" type="danger" size="small">必修</el-tag>
                <el-tag v-else-if="courseDetail.course.isRequired === 0" type="info" size="small">选修</el-tag>
              </div>
              <p class="course-description">{{ courseDetail.course.description || '暂无描述' }}</p>
              <div class="course-meta-row">
                <el-progress
                  v-if="courseDetail.courseProgress != null"
                  type="circle"
                  :percentage="courseDetail.courseProgress"
                  :width="72"
                  :stroke-width="6"
                  class="progress-ring"
                />
                <div class="course-actions">
                  <el-button type="primary" size="large" @click="handleStartLearn">
                    开始学习
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 标签：课程目录 / 课程附件 -->
        <el-card class="tabs-card" v-if="hasChaptersOrAttachments">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="课程目录" name="catalog">
              <div v-if="chaptersWithVideos.length > 0" class="chapter-list">
                <div v-for="(chapter, chIndex) in chaptersWithVideos" :key="chapter.id ?? 'uncat-' + chIndex" class="chapter-block">
                  <div class="chapter-header">
                    <span class="chapter-num">第 {{ chIndex + 1 }} 章</span>
                    <span class="chapter-title">{{ chapter.title }}</span>
                  </div>
                  <div class="video-list">
                    <div
                      v-for="(video, index) in chapter.hours"
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
                          <span v-if="getLearnRecord(video.id)" class="learn-record">
                            {{ formatLearnRecord(video.id) }}
                          </span>
                        </div>
                      </div>
                      <div class="video-action">
                        <el-icon><VideoPlay /></el-icon>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else-if="courseDetail.videos && courseDetail.videos.length > 0" class="video-list">
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
                      <span v-if="getLearnRecord(video.id)" class="learn-record">
                        {{ formatLearnRecord(video.id) }}
                      </span>
                    </div>
                  </div>
                  <div class="video-action">
                    <el-icon><VideoPlay /></el-icon>
                  </div>
                </div>
              </div>
              <el-empty v-else description="暂无课时" />
            </el-tab-pane>
            <el-tab-pane label="课程附件" name="attachments">
              <div v-if="courseDetail.attachments && courseDetail.attachments.length > 0" class="attachment-list">
                <div
                  v-for="att in courseDetail.attachments"
                  :key="att.id"
                  class="attachment-item"
                  @click="handleDownloadAttachment(att)"
                >
                  <el-icon class="att-icon"><Document /></el-icon>
                  <span class="att-name">{{ att.name }}</span>
                  <el-icon class="att-download"><Download /></el-icon>
                </div>
              </div>
              <el-empty v-else description="暂无附件" />
            </el-tab-pane>
          </el-tabs>
        </el-card>

        <!-- 无章节/附件时保留原扁平视频列表 -->
        <el-card v-else-if="courseDetail.videos && courseDetail.videos.length > 0" class="videos-card">
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
                  <span v-if="getLearnRecord(video.id)" class="learn-record">
                    {{ formatLearnRecord(video.id) }}
                  </span>
                </div>
              </div>
              <div class="video-action">
                <el-icon><VideoPlay /></el-icon>
              </div>
            </div>
          </div>
        </el-card>

        <el-empty v-else-if="!hasChaptersOrAttachments" description="暂无视频" />
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Clock, VideoPlay, Document, Download } from '@element-plus/icons-vue'
import { getCourseById, type CourseDetail, type CourseAttachment, type ChapterItem } from '@/api/course'
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

/** 仅包含有视频的章节，用于课程目录展示 */
const chaptersWithVideos = computed<ChapterItem[]>(() => {
  const d = courseDetail.value
  if (!d?.chapters?.length) return []
  return d.chapters.filter((ch) => ch.hours && ch.hours.length > 0)
})

function getLearnRecord(videoId: number) {
  const d = courseDetail.value
  if (!d?.learnRecord) return null
  return d.learnRecord[String(videoId)] ?? d.learnRecord[videoId] ?? null
}

function formatLearnRecord(videoId: number): string {
  const rec = getLearnRecord(videoId)
  if (!rec) return ''
  const p = rec.progress ?? 0
  const d = rec.duration ?? 0
  if (d <= 0) return ''
  return `已看 ${formatDuration(p)} / ${formatDuration(d)}`
}

function handleDownloadAttachment(att: CourseAttachment) {
  if (!att.fileUrl) {
    ElMessage.warning('附件地址无效')
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
      })
      .catch(() => ElMessage.error('下载失败'))
  } else {
    window.open(att.fileUrl, '_blank')
  }
}

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
    router.push({ path: '/login', query: { redirect: `/course/${route.params.id}` } })
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
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;

      .header-logo-icon {
        width: 28px;
        height: 28px;
        display: block;
        object-fit: contain;
      }

      h1 {
        color: #667eea;
        font-size: 24px;
        margin: 0;
        line-height: 28px;
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
        margin-bottom: 8px;
      }

      .course-tags {
        margin-bottom: 10px;
      }

      .course-description {
        font-size: 16px;
        color: #606266;
        line-height: 1.6;
        margin-bottom: 15px;
      }

      .course-meta-row {
        display: flex;
        align-items: center;
        gap: 24px;
        margin-top: 20px;

        .progress-ring {
          flex-shrink: 0;
        }

        .course-actions {
          margin-top: 0;
        }
      }

      .course-actions {
        margin-top: 20px;
      }
    }
  }
}

.tabs-card {
  margin-bottom: 20px;

  .chapter-list {
    .chapter-block {
      margin-bottom: 24px;
      background: #fafbfc;
      border-radius: 10px;
      overflow: hidden;
      border: 1px solid #ebeef5;

      &:last-child {
        margin-bottom: 0;
      }

      .chapter-header {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 14px 18px;
        background: linear-gradient(135deg, #f0f5ff 0%, #e8efff 100%);
        border-left: 4px solid #409eff;

        .chapter-num {
          font-size: 13px;
          color: #409eff;
          font-weight: 600;
          flex-shrink: 0;
        }

        .chapter-title {
          font-size: 16px;
          font-weight: 600;
          color: #303133;
          margin: 0;
        }
      }

      .video-list {
        padding: 8px 0;

        .video-item {
          display: flex;
          align-items: center;
          padding: 14px 18px;
          margin: 0 8px 4px;
          border-radius: 8px;
          cursor: pointer;
          transition: background-color 0.2s;

          &:hover {
            background-color: #fff;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
          }

          .video-index {
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #e8f4ff;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            color: #409eff;
            margin-right: 14px;
            flex-shrink: 0;
          }

          .video-info {
            flex: 1;
            min-width: 0;

            h4 {
              font-size: 15px;
              color: #303133;
              margin: 0 0 6px;
              font-weight: 500;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }

            .video-meta {
              display: flex;
              align-items: center;
              gap: 12px;
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
            font-size: 22px;
            flex-shrink: 0;
          }
        }
      }
    }
  }

  .attachment-list {
    .attachment-item {
      display: flex;
      align-items: center;
      padding: 12px 16px;
      border: 1px solid #ebeef5;
      border-radius: 6px;
      margin-bottom: 8px;
      cursor: pointer;
      transition: background-color 0.2s;

      &:hover {
        background-color: #f5f7fa;
      }

      .att-icon {
        margin-right: 12px;
        color: #909399;
        font-size: 20px;
      }

      .att-name {
        flex: 1;
        font-size: 14px;
        color: #303133;
      }

      .att-download {
        color: #409eff;
        font-size: 18px;
      }
    }
  }
}

.video-meta .learn-record {
  margin-left: 12px;
  color: #67c23a;
  font-size: 13px;
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
