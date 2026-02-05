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
    component: () => import('@/views/MainLayout.vue'),
    redirect: '/index',
    children: [
      {
        path: 'index',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'courses',
        name: 'Courses',
        component: () => import('@/views/Courses.vue'),
        meta: { title: '课程中心', requiresAuth: true }
      },
      {
        path: 'my',
        name: 'My',
        component: () => import('@/views/My.vue'),
        meta: { title: '我的', requiresAuth: true }
      }
    ]
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
    path: '/my-points',
    name: 'MyPoints',
    component: () => import('@/views/MyPoints.vue'),
    meta: { title: '我的积分', requiresAuth: true }
  },
  {
    path: '/my-certificates',
    name: 'MyCertificates',
    component: () => import('@/views/MyCertificates.vue'),
    meta: { title: '我的证书', requiresAuth: true }
  },
  {
    path: '/my-tasks',
    name: 'MyTasks',
    component: () => import('@/views/MyTasks.vue'),
    meta: { title: '我的任务', requiresAuth: true }
  },
  {
    path: '/my-liked-videos',
    name: 'MyLikedVideos',
    component: () => import('@/views/MyLikedVideos.vue'),
    meta: { title: '我点赞的视频', requiresAuth: true }
  },
  {
    path: '/exam',
    name: 'ExamList',
    component: () => import('@/views/ExamList.vue'),
    meta: { title: '考试中心', requiresAuth: true }
  },
  {
    path: '/exam/:id/take',
    name: 'ExamTake',
    component: () => import('@/views/ExamTake.vue'),
    meta: { title: '答题', requiresAuth: true }
  },
  {
    path: '/exam/:id/result',
    name: 'ExamResult',
    component: () => import('@/views/ExamResult.vue'),
    meta: { title: '考试成绩', requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '个人资料', requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { title: '设置' }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About.vue'),
    meta: { title: '关于' }
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

export default router
