<template>
  <div class="course-detail-container">
    <van-nav-bar title="课程详情" left-arrow @click-left="$router.back()" fixed placeholder />

    <van-loading v-if="loading" class="page-loading" size="24px" vertical>加载中...</van-loading>
    <template v-else>
      <div v-if="courseDetail" class="bilibili-layout">
        <!-- 1. 顶部固定视频区（position: fixed，不随滚动） -->
        <div ref="fixedVideoAreaRef" class="fixed-video-area">
          <template v-if="currentVideo && fixedVideoUrl">
            <video
              ref="fixedVideoRef"
              class="fixed-video-player"
              :src="fixedVideoUrl"
              :poster="fixedVideoPoster"
              preload="metadata"
              controls
              playsinline
              webkit-playsinline
              @timeupdate="onFixedVideoTimeUpdate"
              @ended="onFixedVideoEnded"
              @play="fixedVideoCoverHidden = true"
            />
            <!-- 封面层：始终显示设置的封面，直到用户点击播放 -->
            <div
              v-show="!fixedVideoCoverHidden"
              class="fixed-video-poster-overlay"
              :style="fixedVideoPoster ? { backgroundImage: `url(${fixedVideoPoster})` } : {}"
              @click="fixedVideoRef?.play()"
            />
          </template>
          <template v-else>
            <div class="video-cover-wrap" :style="coverStyle" @click="playFirstOrSelect">
              <van-icon name="play-circle-o" class="cover-play-icon" />
              <span v-if="videoCount > 0" class="cover-hint">点击选择视频播放</span>
            </div>
          </template>
        </div>

        <!-- 占位：与固定视频区同高，保证下方内容不被遮挡 -->
        <div class="video-area-spacer" :style="{ height: videoAreaHeightPx + 'px' }" />

        <!-- 2. 可滚动区：标题 + 描述，再到 Tab（Tab 到达视频底部时吸附） -->
        <div class="scroll-body">
          <div class="title-desc-section">
            <h1 class="course-title">{{ courseDetail.course.title }}</h1>
            <div class="course-meta">
              <van-tag v-if="courseDetail.course.isRequired === 1" type="danger" plain size="medium">必修</van-tag>
              <van-tag v-else-if="courseDetail.course.isRequired === 0" type="primary" plain size="medium">选修</van-tag>
              <span v-if="videoCount > 0" class="meta-text">{{ videoCount }} 节视频</span>
            </div>
            <p v-if="courseDetail.course.description" class="course-desc">{{ courseDetail.course.description }}</p>
            <p v-else class="course-desc placeholder">暂无描述</p>
            <div v-if="courseDetail.courseProgress != null" class="progress-row">
              <van-circle
                :rate="(courseDetail.courseProgress ?? 0) / 100"
                :size="48"
                :stroke-width="4"
                layer-color="#ebedf0"
                color="#1989fa"
              />
              <span class="progress-text">已学 {{ Math.round(courseDetail.courseProgress ?? 0) }}%</span>
            </div>
            <div v-if="examId" class="exam-card">
              <div class="exam-title">课程考试</div>
              <div class="exam-meta">
                <span v-if="examStatus?.startTime">开始：{{ examStatus?.startTime }}</span>
                <span v-if="examStatus?.endTime">结束：{{ examStatus?.endTime }}</span>
                <span v-if="examStatus?.durationMinutes && !examStatus?.unlimited">时长 {{ examStatus?.durationMinutes }} 分钟</span>
                <span v-if="examStatus?.unlimited">无时间限制</span>
              </div>
              <div class="exam-action">
                <van-button
                  type="primary"
                  size="small"
                  round
                  :loading="examLoading"
                  :disabled="examStatus && examStatus.canStart === false"
                  @click="handleStartExam"
                >
                  {{ examStatus?.canStart === false ? (examStatus?.message || '不可开始') : '开始考试' }}
                </van-button>
              </div>
            </div>
          </div>

          <!-- 3. Tab：滚动到视频底部时吸附，继续向下滚动内容在 Tab 下滚动，向上滚动还原 -->
          <div class="tabs-section">
            <van-tabs v-model:active="activeTab" shrink sticky :offset-top="tabsStickyTop">
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
                      :class="{ 'cell-playing': currentVideo?.id === video.id }"
                      is-link
                      @click="handlePlayInPlace(video)"
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
                    :class="{ 'cell-playing': currentVideo?.id === video.id }"
                    is-link
                    @click="handlePlayInPlace(video)"
                  >
                    <template #icon>
                      <van-icon name="play-circle-o" size="20" color="#1989fa" style="margin-right: 8px" />
                    </template>
                  </van-cell>
                </van-cell-group>
              </div>
              <van-empty v-else description="暂无课时" />
            </van-tab>
            <van-tab title="附件" name="attachments">
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
            <van-tab :title="'评论' + (commentTree.length ? ` ${commentTree.length}` : '')" name="comments">
              <div class="comment-tab-content">
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
            </van-tab>
          </van-tabs>
        </div>
        </div>
      </div>
    </template>

    <!-- 底部固定：开始学习 -->
    <div v-if="courseDetail" class="bottom-action-bar">
      <van-button type="primary" block round @click="handleStartLearn" class="bottom-start-btn">
        {{ startButtonText }}
      </van-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showSuccessToast, showFailToast } from 'vant'
import { getCourseById, getCourseComments, addCourseComment, type CourseDetail, type CourseAttachment, type ChapterItem, type CourseCommentDto } from '@/api/course'
import { joinCourse, updateVideoProgress } from '@/api/learning'
import { getExamStatus } from '@/api/exam'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const courseDetail = ref<CourseDetail | null>(null)
const activeTab = ref('catalog')
const comments = ref<CourseCommentDto[]>([])
const commentContent = ref('')
const commentSubmitting = ref(false)
const hasToken = ref(!!localStorage.getItem('token'))
/** 当前在详情页顶部固定区播放的视频（B站式） */
const currentVideo = ref<{ id: number; title?: string; url?: string; cover?: string; duration?: number } | null>(null)
const fixedVideoRef = ref<HTMLVideoElement | null>(null)
/** 是否隐藏封面遮罩（开始播放后为 true，切换视频时重置） */
const fixedVideoCoverHidden = ref(false)
const fixedVideoAreaRef = ref<HTMLElement | null>(null)
/** 固定视频区高度（px），用于 spacer 与 Tab 吸附位置 */
const videoAreaHeightPx = ref(220)
/** Tab 吸附时的 top 值（视频区底部），用于 van-tabs sticky */
const tabsStickyTop = ref(220)
const NAV_BAR_HEIGHT = 46
const fixedVideoLastProgressSaveAt = ref(0)
const FIXED_VIDEO_PROGRESS_INTERVAL_MS = 5000
const examId = ref<number | null>(null)
const examStatus = ref<{ canStart: boolean; status: string; message: string; durationMinutes?: number; unlimited: boolean; startTime?: string; endTime?: string } | null>(null)
const examLoading = ref(false)

const apiBase = () => window.location.origin + '/api'
/** 将后端返回的 url 转为可播放的完整地址（与 VideoPlayer 一致） */
function buildVideoUrl(url: string | undefined): string {
  if (!url?.trim()) return ''
  let u = url.trim()
  if (u.startsWith('http://') || u.startsWith('https://')) return u
  if (u.startsWith('/uploads/')) return apiBase() + u
  if (u.startsWith('/')) return apiBase() + u
  return apiBase() + '/uploads/' + u.replace(/^\/+/, '')
}
function buildPosterUrl(url: string | undefined): string {
  if (!url?.trim()) return ''
  let u = url.trim()
  if (u.startsWith('http://') || u.startsWith('https://')) return u
  if (u.startsWith('/')) return apiBase() + u
  return apiBase() + '/uploads/images/' + u.replace(/^\/+/, '')
}

const fixedVideoUrl = computed(() => (currentVideo.value?.url ? buildVideoUrl(currentVideo.value.url) : ''))
const fixedVideoPoster = computed(() => (currentVideo.value?.cover ? buildPosterUrl(currentVideo.value.cover) : ''))

/** 顶部封面图：课程封面或第一个视频封面 */
const coverStyle = computed(() => {
  const d = courseDetail.value
  const cover = d?.course?.cover
  if (cover) {
    const u = buildPosterUrl(cover)
    if (u) return { backgroundImage: `url(${u})`, backgroundSize: 'cover', backgroundPosition: 'center' }
  }
  const first = d?.videos?.[0] || d?.chapters?.[0]?.hours?.[0]
  if (first?.cover) {
    const u = buildPosterUrl(first.cover)
    if (u) return { backgroundImage: `url(${u})`, backgroundSize: 'cover', backgroundPosition: 'center' }
  }
  return { background: 'linear-gradient(135deg, #e8f4ff 0%, #dcebff 100%)' }
})

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
    examId.value = (res as any).examId ?? null
    if (examId.value) {
      await loadExamStatus(examId.value)
    } else {
      examStatus.value = null
    }
    // 默认使用第一个视频（章节内首个或未分类首个）
    const firstVideo = res?.chapters?.[0]?.hours?.[0] ?? res?.videos?.[0]
    if (firstVideo) {
      const cover = getVideoCover(firstVideo)
      currentVideo.value = { id: firstVideo.id, title: firstVideo.title, url: firstVideo.url, cover: cover || undefined, duration: firstVideo.duration }
      fixedVideoCoverHidden.value = false
    } else {
      currentVideo.value = null
    }
    const list = await getCourseComments(courseId)
    comments.value = list || []
  } catch (e: any) {
    const msg = e?.message || e?.response?.data?.message || e?.response?.data?.detail || '加载课程详情失败'
    showFailToast(typeof msg === 'string' ? msg : '加载课程详情失败')
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

/** 从视频对象中取封面（兼容后端 cover / cover_url 等） */
function getVideoCover(video: any): string {
  if (!video) return ''
  const c = video.cover ?? (video as any).cover_url ?? video.coverUrl ?? ''
  return typeof c === 'string' ? c : ''
}

/** 在详情页顶部固定区播放（B站式）；也可跳转独立播放页 */
function handlePlayInPlace(video: any) {
  const cover = getVideoCover(video)
  currentVideo.value = { id: video.id, title: video.title, url: video.url, cover: cover || undefined, duration: video.duration }
  fixedVideoCoverHidden.value = false
  nextTick(() => {
    const el = fixedVideoRef.value
    if (el) {
      el.load()
      el.play().catch(() => {})
    }
  })
}

/** 跳转到独立视频播放页（与原先一致） */
const handlePlayVideo = (video: any) => {
  router.push(`/video/${video.id}`)
}

/** 封面点击：播放第一个视频或仅做占位 */
function playFirstOrSelect() {
  const d = courseDetail.value
  const first = d?.chapters?.[0]?.hours?.[0] || d?.videos?.[0]
  if (first) handlePlayInPlace(first)
}

/** 详情页内嵌播放：定时上报进度 */
function onFixedVideoTimeUpdate() {
  const token = localStorage.getItem('token')
  if (!token || !currentVideo.value || !fixedVideoRef.value) return
  const el = fixedVideoRef.value
  const progress = Math.floor(el.currentTime)
  let duration = Math.floor(el.duration)
  if (!Number.isFinite(duration) || duration <= 0) duration = Math.floor((currentVideo.value?.duration ?? 0))
  if (!Number.isFinite(progress) || progress < 1 || duration <= 0) return
  const now = Date.now()
  if (now - fixedVideoLastProgressSaveAt.value < FIXED_VIDEO_PROGRESS_INTERVAL_MS) return
  fixedVideoLastProgressSaveAt.value = now
  updateVideoProgress(currentVideo.value.id, progress, duration).catch(() => {})
}

/** 详情页内嵌播放：结束时上报一次并刷新课程进度展示 */
function onFixedVideoEnded() {
  const token = localStorage.getItem('token')
  if (!token || !currentVideo.value || !fixedVideoRef.value) return
  const el = fixedVideoRef.value
  const progress = Math.floor(el.currentTime)
  let duration = Math.floor(el.duration) || Math.floor((currentVideo.value?.duration ?? 0))
  if (duration > 0) updateVideoProgress(currentVideo.value.id, progress, duration).catch(() => {})
  loadCourseDetail()
}

async function loadExamStatus(eid: number) {
  examLoading.value = true
  try {
    const res = await getExamStatus(eid)
    examStatus.value = res as any
  } catch {
    examStatus.value = null
  } finally {
    examLoading.value = false
  }
}

function handleStartExam() {
  if (!examId.value) return
  if (examStatus.value && examStatus.value.canStart === false) {
    showFailToast(examStatus.value.message || '考试未开始或已结束')
    return
  }
  router.push(`/exam/${examId.value}/take`)
}

function measureVideoAreaHeight() {
  const h = NAV_BAR_HEIGHT + Math.round(window.innerWidth * 0.5625)
  videoAreaHeightPx.value = h
  tabsStickyTop.value = h
}

onMounted(() => {
  measureVideoAreaHeight()
  window.addEventListener('resize', measureVideoAreaHeight)
  loadCourseDetail()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', measureVideoAreaHeight)
  if (!localStorage.getItem('token') || !currentVideo.value || !fixedVideoRef.value) return
  const el = fixedVideoRef.value
  const progress = Math.floor(el.currentTime)
  const duration = Math.floor(el.duration) || Math.floor((currentVideo.value?.duration ?? 0))
  if (duration > 0 && progress >= 1) updateVideoProgress(currentVideo.value.id, progress, duration).catch(() => {})
})
</script>

<style scoped lang="scss">
.course-detail-container {
  min-height: 100vh;
  background: #f2f3f5;
  padding-bottom: calc(76px + env(safe-area-inset-bottom));
}

.page-loading {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}

/* B站式布局：固定视频区 + 标题/描述 + Tab */
.bilibili-layout {
  background: #fff;
}

/* 1. 顶部固定视频播放区（固定于导航栏下方，不随滚动） */
.fixed-video-area {
  position: fixed;
  top: 46px; /* 与 van-nav-bar 高度一致 */
  left: 0;
  right: 0;
  width: 100%;
  height: 56.25vw; /* 16:9 */
  background: #000;
  overflow: hidden;
  z-index: 1;
}
.fixed-video-player {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}
/* 封面遮罩：在播放前始终显示设置的封面，避免浏览器显示首帧 */
.fixed-video-poster-overlay {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background-color: #000;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 2;
  pointer-events: auto;
}
.video-cover-wrap {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  .cover-play-icon {
    font-size: 64px;
    color: rgba(255, 255, 255, 0.9);
  }
  .cover-hint {
    margin-top: 8px;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.8);
  }
}

/* 2. 标题/描述（紧接视频下方） */
.title-desc-section {
  padding: 14px 16px 16px;
  border-bottom: 1px solid #ebedf0;
  .course-title {
    font-size: 18px;
    font-weight: 600;
    color: #323233;
    line-height: 1.4;
    margin: 0 0 8px;
  }
  .course-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 10px;
    .meta-text {
      font-size: 13px;
      color: #969799;
    }
  }
  .course-desc {
    font-size: 14px;
    color: #646566;
    line-height: 1.5;
    margin: 0 0 12px;
    &.placeholder {
      color: #c8c9cc;
    }
  }
  .progress-row {
    display: flex;
    align-items: center;
    gap: 10px;
    .progress-text {
      font-size: 12px;
      color: #969799;
    }
  }
  .exam-card {
    margin-top: 10px;
    padding: 12px;
    border: 1px solid #ebedf0;
    border-radius: 8px;
    background: #f8f9fb;
    .exam-title {
      font-weight: 600;
      color: #323233;
      margin-bottom: 6px;
    }
    .exam-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      font-size: 13px;
      color: #646566;
      margin-bottom: 8px;
    }
    .exam-action {
      display: flex;
      justify-content: flex-start;
    }
  }
}

/* 3. Tab 区域（课程目录 / 附件 / 评论） */
.tabs-section {
  min-height: 200px;
  :deep(.van-tabs__wrap) {
    padding: 0 16px;
  }
  :deep(.van-tabs__content) {
    padding: 12px 0 24px;
  }
  .cell-playing {
    background: #e8f4ff;
  }
}
.comment-tab-content {
  padding: 0 16px;
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

.empty-block {
  padding: 24px 0;
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
</style>
