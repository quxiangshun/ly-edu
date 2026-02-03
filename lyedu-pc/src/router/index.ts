import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import {
  getFeishuCodeFromUrl,
  clearFeishuCodeInUrl,
  getFeishuRedirectUri,
  isFeishuEnabled,
  isInFeishuEmbed
} from '@/utils/auth'
import { feishuCallback, getFeishuAuthUrl } from '@/api/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: {
      title: '首页'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: '登录'
    }
  },
  {
    path: '/courses',
    name: 'Courses',
    component: () => import('@/views/Courses.vue'),
    meta: {
      title: '课程中心',
      requiresAuth: true
    }
  },
  {
    path: '/course/:id',
    name: 'CourseDetail',
    component: () => import('@/views/CourseDetail.vue'),
    meta: {
      title: '课程详情',
      requiresAuth: true
    }
  },
  {
    path: '/video/:id',
    name: 'VideoPlayer',
    component: () => import('@/views/VideoPlayer.vue'),
    meta: {
      title: '视频播放',
      requiresAuth: true
    }
  },
  {
    path: '/my-learning',
    name: 'MyLearning',
    component: () => import('@/views/MyLearning.vue'),
    meta: {
      title: '我的学习',
      requiresAuth: true
    }
  },
  {
    path: '/knowledge',
    name: 'KnowledgeCenter',
    component: () => import('@/views/KnowledgeCenter.vue'),
    meta: {
      title: '知识中心',
      requiresAuth: true
    }
  },
  {
    path: '/preview',
    name: 'DocumentPreview',
    component: () => import('@/views/DocumentPreview.vue'),
    meta: {
      title: '文档预览',
      requiresAuth: true
    }
  },
  {
    path: '/exam',
    name: 'ExamList',
    component: () => import('@/views/ExamList.vue'),
    meta: {
      title: '考试中心',
      requiresAuth: true
    }
  },
  {
    path: '/exam/:id/take',
    name: 'ExamTake',
    component: () => import('@/views/ExamTake.vue'),
    meta: {
      title: '参加考试',
      requiresAuth: true
    }
  },
  {
    path: '/exam/:id/result',
    name: 'ExamResult',
    component: () => import('@/views/ExamResult.vue'),
    meta: {
      title: '考试成绩',
      requiresAuth: true
    }
  },
  {
    path: '/certificates',
    name: 'MyCertificates',
    component: () => import('@/views/MyCertificates.vue'),
    meta: {
      title: '我的证书',
      requiresAuth: true
    }
  },
  {
    path: '/tasks',
    name: 'TaskList',
    component: () => import('@/views/TaskList.vue'),
    meta: {
      title: '我的任务',
      requiresAuth: true
    }
  },
  {
    path: '/task/:id',
    name: 'TaskDetail',
    component: () => import('@/views/TaskDetail.vue'),
    meta: {
      title: '任务详情',
      requiresAuth: true
    }
  },
  {
    path: '/certificate/:id/print',
    name: 'CertificatePrint',
    component: () => import('@/views/CertificatePrint.vue'),
    meta: {
      title: '证书打印',
      requiresAuth: true
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 飞书回调：URL 带 code 时先换 token 再继续
router.beforeEach(async (to, _from, next) => {
  const feishuPayload = getFeishuCodeFromUrl()
  if (feishuPayload) {
    try {
      const redirectUri = getFeishuRedirectUri()
      const res = await feishuCallback(feishuPayload.code, redirectUri)
      if (res?.token) {
        localStorage.setItem('token', res.token)
        localStorage.setItem('user', JSON.stringify(res.userInfo ?? {}))
      }
    } catch (_e) {
      // 错误由 API 拦截器提示
    }
    clearFeishuCodeInUrl()
    const path = to.path + (to.hash || '')
    const query = { ...to.query }
    delete query.code
    delete query.state
    next({ path, query, replace: true })
    return
  }

  const requiresAuth = to.matched.some(r => r.meta?.requiresAuth)
  const token = localStorage.getItem('token')
  if (requiresAuth && !token) {
    if (isFeishuEnabled() && isInFeishuEmbed()) {
      try {
        const redirectUri = getFeishuRedirectUri()
        const fullRedirect = window.location.origin + to.fullPath
        const res = await getFeishuAuthUrl(fullRedirect, 'feishu_embed')
        if (res?.url) {
          window.location.href = res.url
          return
        }
      } catch (_e) {
        // 降级到登录页
      }
      next({ path: '/login', query: { redirect: to.fullPath } })
      return
    }
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

// 视频播放页：禁止整页滚动，仅右侧列表可滚动
const VIDEO_PAGE_CLASS = 'lyedu-video-page'
router.afterEach((to, from) => {
  if (to.name === 'VideoPlayer') {
    document.body.classList.add(VIDEO_PAGE_CLASS)
  } else if (from.name === 'VideoPlayer') {
    document.body.classList.remove(VIDEO_PAGE_CLASS)
  }
})

export default router
