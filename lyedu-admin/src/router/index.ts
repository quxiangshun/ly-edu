import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import Layout from '@/components/Layout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
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
    path: '/',
    component: Layout,
    meta: {
      requiresAuth: true
    },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: {
          title: '仪表盘'
        }
      },
      {
        path: 'department',
        name: 'Department',
        component: () => import('@/views/Department.vue'),
        meta: {
          title: '公司架构'
        }
      },
      {
        path: 'user',
        name: 'User',
        component: () => import('@/views/User.vue'),
        meta: {
          title: '员工管理'
        }
      },
      {
        path: 'course',
        name: 'Course',
        component: () => import('@/views/Course.vue'),
        meta: {
          title: '课程管理'
        }
      },
      {
        path: 'video',
        name: 'Video',
        component: () => import('@/views/Video.vue'),
        meta: {
          title: '视频管理'
        }
      },
      {
        path: 'image',
        name: 'ImageLibrary',
        component: () => import('@/views/ImageLibrary.vue'),
        meta: {
          title: '图片库'
        }
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: () => import('@/views/Knowledge.vue'),
        meta: {
          title: '知识库'
        }
      },
      {
        path: 'question',
        name: 'Question',
        component: () => import('@/views/Question.vue'),
        meta: {
          title: '试题管理'
        }
      },
      {
        path: 'paper',
        name: 'Paper',
        component: () => import('@/views/Paper.vue'),
        meta: {
          title: '试卷管理'
        }
      },
      {
        path: 'exam',
        name: 'Exam',
        component: () => import('@/views/Exam.vue'),
        meta: {
          title: '考试管理'
        }
      },
      {
        path: 'certificate-template',
        name: 'CertificateTemplate',
        component: () => import('@/views/CertificateTemplate.vue'),
        meta: {
          title: '证书模板'
        }
      },
      {
        path: 'certificate',
        name: 'Certificate',
        component: () => import('@/views/Certificate.vue'),
        meta: {
          title: '证书规则'
        }
      },
      {
        path: 'task',
        name: 'Task',
        component: () => import('@/views/Task.vue'),
        meta: {
          title: '周期任务'
        }
      },
      {
        path: 'point-rule',
        name: 'PointRule',
        component: () => import('@/views/PointRule.vue'),
        meta: {
          title: '积分规则'
        }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: {
          title: '系统设置'
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：检查登录状态
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  // 如果访问登录页且已登录，重定向到dashboard
  if (to.path === '/login' && token) {
    next('/dashboard')
    return
  }
  
  // 如果访问需要认证的页面且未登录，重定向到登录页
  if (to.meta.requiresAuth && !token) {
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }
  
  next()
})

export default router
