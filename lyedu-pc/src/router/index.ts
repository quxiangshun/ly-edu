import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 课程中心、我的学习等需登录
router.beforeEach((to, _from, next) => {
  const requiresAuth = to.matched.some(r => r.meta?.requiresAuth)
  const token = localStorage.getItem('token')
  if (requiresAuth && !token) {
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
