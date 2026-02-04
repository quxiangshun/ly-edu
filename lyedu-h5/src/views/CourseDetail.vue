<template>
  <div class="course-detail-container">
    <van-nav-bar title="课程详情" left-arrow @click-left="$router.back()" fixed placeholder />

    <van-loading v-if="loading" class="page-loading" size="24px" vertical>加载中...</van-loading>
    <div v-else class="content">
      <div v-if="courseDetail">
        <!-- 标题区（课程封面用于视频页作为封面，不在此单独展示） -->
        <div class="course-card title-card">
          <h1 class="course-title">{{ courseDetail.course.title }}</h1>
          <div class="course-meta">
            <van-tag v-if="courseDetail.course.isRequired === 1" type="danger" plain size="medium">必修</van-tag>
            <van-tag v-else-if="courseDetail.course.isRequired === 0" type="primary" plain size="medium">选修</van-tag>
            <span v-if="videoCount > 0" class="meta-text">{{ videoCount }} 节视频</span>
          </div>
        </div>

        <!-- 描述与进度 -->
        <div class="course-card info-card">
          <p v-if="courseDetail.course.description" class="course-desc">{{ courseDetail.course.description }}</p>
          <p v-else class="course-desc placeholder">暂无描述</p>
          <div class="progress-row">
            <div v-if="courseDetail.courseProgress != null" class="progress-wrap">
              <van-circle
                :rate="(courseDetail.courseProgress ?? 0) / 100"
                :size="56"
                :stroke-width="5"
                layer-color="#ebedf0"
                color="#1989fa"
              />
              <span class="progress-text">已学 {{ Math.round(courseDetail.courseProgress ?? 0) }}%</span>
            </div>
          </div>
        </div>

        <!-- 课程目录 / 附件 -->
        <div v-if="hasChaptersOrAttachments" class="course-card tabs-card">
          <van-tabs v-model:active="activeTab" shrink>
            <van-tab title="课程目录" name="catalog">
              <div v-if="chaptersWithVideos.length > 0" class="chapter-list">
                <div v-for="(chapter, chIndex) in chaptersWithVideos" :key="chapter.id ?? 'uncat-' + chIndex" class="chapter-block">
                  <div class="chapter-header">
                    <span class="chapter-num">第{{ chIndex + 1 }}章</span>
                    <span class="chapter-title">{{ chapter.title }}</span>
                  </div>
                  <van-cell-group inset>
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

        <!-- 无章节/附件时扁平视频列表 -->
        <div v-else-if="courseDetail.videos && courseDetail.videos.length > 0" class="course-card">
          <div class="card-title">课程视频 ({{ courseDetail.videos.length }})</div>
          <van-cell-group inset>
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

        <van-empty v-else-if="!hasChaptersOrAttachments" description="暂无视频" class="empty-block" />

        <!-- 课程评论 -->
        <div class="course-card comment-card">
          <div class="card-title">课程评论</div>
          <van-field
            v-if="hasToken"
            v-model="commentContent"
            type="textarea"
            rows="2"
            placeholder="写下你的评论..."
            maxlength="500"
            show-word-limit
          />
          <van-button v-if="hasToken" type="primary" size="small" round :loading="commentSubmitting" @click="submitComment" class="comment-submit">发表</van-button>
          <p v-else class="comment-login-tip">登录后可发表评论</p>
          <van-divider v-if="commentTree.length > 0" :style="{ margin: '16px 0 12px' }" />
          <div class="comment-list" v-if="commentTree.length > 0">
            <div v-for="node in commentTree" :key="node.id" class="comment-node">
              <div class="comment-item">
                <span class="comment-user">{{ node.userRealName || '用户' }}</span>
                <span class="comment-time">{{ formatCommentTime(node.createTime) }}</span>
                <p class="comment-content">{{ node.content }}</p>
              </div>
              <div v-if="node.replies?.length" class="comment-replies">
                <div v-for="r in node.replies" :key="r.id" class="comment-item reply">
                  <span class="comment-user">{{ r.userRealName || '用户' }}</span>
                  <span class="comment-time">{{ formatCommentTime(r.createTime) }}</span>
                  <p class="comment-content">{{ r.content }}</p>
                </div>
              </div>
            </div>
          </div>
          <van-empty v-else description="暂无评论" class="empty-block" />
        </div>
      </div>
    </div>

    <!-- 底部固定操作栏：开始学习 -->
    <div v-if="courseDetail" class="bottom-action-bar">
      <van-button type="primary" block round @click="handleStartLearn" class="bottom-start-btn">
        {{ startButtonText }}
      </van-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showSuccessToast, showFailToast } from 'vant'
import { getCourseById, getCourseComments, addCourseComment, type CourseDetail, type CourseAttachment, type ChapterItem, type CourseCommentDto } from '@/api/course'
import { joinCourse } from '@/api/learning'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const courseDetail = ref<CourseDetail | null>(null)
const activeTab = ref('catalog')
const comments = ref<CourseCommentDto[]>([])
const commentContent = ref('')
const commentSubmitting = ref(false)
const hasToken = ref(!!localStorage.getItem('token'))

/** 评论树：根评论 + replies */
const commentTree = computed(() => {
  const list = comments.value || []
  const roots = list.filter((c) => !c.parentId || c.parentId === 0)
  return roots.map((r) => ({
    ...r,
    replies: list.filter((c) => c.parentId === r.id)
  }))
})

function formatCommentTime(t?: string): string {
  if (!t) return ''
  const d = new Date(t)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

async function submitComment() {
  const courseId = Number(route.params.id)
  const content = commentContent.value?.trim()
  if (!courseId || !content) {
    showFailToast('请输入评论内容')
    return
  }
  commentSubmitting.value = true
  try {
    await addCourseComment(courseId, { content })
    commentContent.value = ''
    showSuccessToast('发表成功')
    const list = await getCourseComments(courseId)
    comments.value = list || []
  } catch (e: unknown) {
    showFailToast((e as { response?: { data?: { message?: string } } })?.response?.data?.message || '发表失败')
  } finally {
    commentSubmitting.value = false
  }
}

const videoCount = computed(() => {
  const d = courseDetail.value
  if (!d?.videos) return 0
  return d.videos.length
})

const startButtonText = computed(() => {
  const p = courseDetail.value?.courseProgress ?? 0
  return p > 0 ? '继续学习' : '开始学习'
})

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
    hasToken.value = !!localStorage.getItem('token')
    const list = await getCourseComments(courseId)
    comments.value = list || []
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
    const vids = courseDetail.value.videos || []
    const firstInChapter = courseDetail.value.chapters?.[0]?.hours?.[0]
    const firstVideo = firstInChapter || (vids.length > 0 ? vids[0] : null)
    if (firstVideo) {
      router.push(`/video/${firstVideo.id}`)
    } else {
      showFailToast('课程暂无视频')
      router.push('/my-learning')
    }
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { message?: string } } })?.response?.data?.message
    showFailToast(msg || '加入课程失败')
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
  background: #f2f3f5;
  padding-bottom: calc(76px + env(safe-area-inset-bottom)); /* 预留底部固定按钮高度 */
}

.page-loading {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}

.content {
  padding: 12px 16px;
}

/* 标题区 */
.title-card {
  padding: 14px 16px;
  .course-title {
    font-size: 20px;
    font-weight: 600;
    color: #323233;
    line-height: 1.4;
    margin: 0 0 10px;
  }
  .course-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    .meta-text {
      font-size: 13px;
      color: #969799;
    }
  }
}

/* 通用卡片 */
.course-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  .card-title {
    font-size: 16px;
    font-weight: 600;
    color: #323233;
    margin-bottom: 14px;
  }
}

.info-card {
  .course-desc {
    font-size: 14px;
    color: #646566;
    line-height: 1.6;
    margin: 0 0 16px;
    &.placeholder {
      color: #c8c9cc;
    }
  }
  .progress-row {
    display: flex;
    align-items: center;
    gap: 16px;
    justify-content: flex-start;
    .progress-wrap {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
      .progress-text {
        font-size: 12px;
        color: #969799;
      }
    }
  }
}

.bottom-action-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 10px 16px calc(12px + env(safe-area-inset-bottom));
  background: rgba(242, 243, 245, 0.92);
  backdrop-filter: blur(10px);
  border-top: 1px solid #ebedf0;
  z-index: 20;
}

.bottom-start-btn {
  height: 44px;
  font-size: 16px;
}

.tabs-card {
  padding: 0 16px 16px;
  :deep(.van-tabs__wrap) {
    padding: 0 16px;
  }
  .chapter-list .chapter-block {
    margin-bottom: 14px;
    background: #f7f8fa;
    border-radius: 10px;
    overflow: hidden;
    .chapter-header {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 14px;
      background: linear-gradient(135deg, #e8f4ff 0%, #dcebff 100%);
      border-left: 4px solid #1989fa;
      .chapter-num {
        font-size: 12px;
        color: #1989fa;
        font-weight: 600;
        flex-shrink: 0;
      }
      .chapter-title {
        font-size: 15px;
        font-weight: 600;
        color: #323233;
      }
    }
    :deep(.van-cell-group--inset) {
      margin: 0 10px 10px;
      border-radius: 8px;
      overflow: hidden;
    }
  }
  .attachment-list {
    padding-top: 8px;
  }
}

.empty-block {
  padding: 24px 0;
}

.comment-card {
  .card-title {
    margin-bottom: 12px;
  }
  .comment-submit {
    margin-top: 10px;
  }
  .comment-login-tip {
    font-size: 13px;
    color: #969799;
    margin: 0 0 12px;
  }
  .comment-list {
    .comment-node {
      border-bottom: 1px solid #ebedf0;
      padding-bottom: 14px;
      margin-bottom: 14px;
      &:last-child {
        border-bottom: none;
        margin-bottom: 0;
      }
    }
    .comment-item {
      .comment-user {
        font-weight: 500;
        color: #323233;
        margin-right: 8px;
        font-size: 14px;
      }
      .comment-time {
        font-size: 12px;
        color: #969799;
      }
      .comment-content {
        margin: 6px 0 0;
        font-size: 14px;
        color: #646566;
        line-height: 1.5;
        white-space: pre-wrap;
      }
      &.reply {
        margin-left: 16px;
        padding: 8px 0 0 10px;
        border-left: 3px solid #ebedf0;
      }
    }
  }
}
</style>
