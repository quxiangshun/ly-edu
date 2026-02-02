<template>
  <div class="home-container">
    <van-nav-bar fixed placeholder>
      <template #title>
        <span class="nav-title">
          <img src="/icon-192.png" alt="" class="nav-logo-icon" />
          LyEdu
        </span>
      </template>
    </van-nav-bar>

    <div class="banner">
      <h2>欢迎来到 LyEdu</h2>
      <p>随时随地，轻松学习</p>
    </div>

    <div class="features">
      <van-grid :column-num="3" :border="false">
        <van-grid-item icon="video-o" text="视频学习" @click="$router.push('/courses')" />
        <van-grid-item icon="orders-o" text="我的课程" @click="$router.push('/my-learning')" />
        <van-grid-item icon="chart-trending-o" text="学习统计" />
      </van-grid>
    </div>

    <!-- 最近学习（登录后展示） -->
    <div v-if="token && recentCourses.length > 0" class="courses-section">
      <div class="section-header">
        <h3>最近学习</h3>
        <span @click="$router.push('/my-learning')">更多 ></span>
      </div>
      <van-card
        v-for="course in recentCourses.slice(0, 4)"
        :key="'recent-' + course.id"
        :title="course.title"
        :desc="course.description || '暂无描述'"
        :thumb="course.cover || 'https://via.placeholder.com/200x120'"
        @click="$router.push(`/course/${course.id}`)"
      >
        <template #tags>
          <van-tag type="primary">继续学习</van-tag>
        </template>
      </van-card>
    </div>

    <!-- 推荐课程 -->
    <div class="courses-section">
      <div class="section-header">
        <h3>推荐课程</h3>
        <span @click="$router.push('/courses')">更多 ></span>
      </div>
      <van-loading v-if="recommendLoading" class="loading" size="24px">加载中...</van-loading>
      <template v-else>
        <van-card
          v-for="course in recommendedCourses"
          :key="course.id"
          :title="course.title"
          :desc="course.description || '暂无描述'"
          :thumb="course.cover || 'https://via.placeholder.com/200x120'"
          @click="handleCourseClick(course)"
        >
          <template #tags>
            <van-tag type="primary">热门</van-tag>
          </template>
          <template #footer>
            <van-button size="mini" type="primary" @click.stop="handleCourseClick(course)">开始学习</van-button>
          </template>
        </van-card>
        <van-empty v-if="recommendedCourses.length === 0" description="暂无推荐课程" />
      </template>
    </div>

    <van-tabbar v-model="active" fixed placeholder>
      <van-tabbar-item icon="home-o" to="/">首页</van-tabbar-item>
      <van-tabbar-item icon="apps-o" to="/courses">课程</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/my">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showSuccessToast, showFailToast } from 'vant'
import type { Course } from '@/api/course'
import { getRecommendedCourses } from '@/api/course'
import { getWatchedCourses, joinCourse } from '@/api/learning'

const router = useRouter()
const active = ref(0)
const token = ref<string | null>(localStorage.getItem('token'))
const recommendedCourses = ref<Course[]>([])
const recentCourses = ref<Course[]>([])
const recommendLoading = ref(false)

const loadRecommended = async () => {
  recommendLoading.value = true
  try {
    const list = await getRecommendedCourses(6)
    recommendedCourses.value = list ?? []
  } catch {
    recommendedCourses.value = []
  } finally {
    recommendLoading.value = false
  }
}

const loadRecentCourses = async () => {
  if (!token.value) return
  try {
    const list = await getWatchedCourses()
    recentCourses.value = list ?? []
  } catch {
    recentCourses.value = []
  }
}

const handleCourseClick = async (course: Course) => {
  if (!token.value) {
    showFailToast('请先登录')
    router.push({ path: '/login', query: { redirect: `/course/${course.id}` } })
    return
  }
  try {
    await joinCourse(course.id)
    showSuccessToast('已加入课程')
    router.push(`/course/${course.id}`)
  } catch {
    showFailToast('加入课程失败')
  }
}

onMounted(() => {
  token.value = localStorage.getItem('token')
  loadRecommended()
  loadRecentCourses()
})
</script>

<style scoped lang="scss">
.home-container {
  padding-bottom: 50px;
}

.banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  padding: 40px 20px;
  margin-bottom: 20px;

  h2 {
    font-size: 28px;
    margin-bottom: 10px;
  }

  p {
    font-size: 14px;
    opacity: 0.9;
  }
}

.features {
  background: white;
  margin-bottom: 20px;
  padding: 20px 0;
}

.courses-section {
  background: white;
  padding: 20px;
  margin-bottom: 20px;
}
.courses-section .loading {
  display: flex;
  justify-content: center;
  padding: 24px 0;
}
.courses-section .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.courses-section .section-header h3 {
  font-size: 18px;
  color: #323233;
}
.courses-section .section-header span {
  font-size: 14px;
  color: #969799;
}

.nav-title {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  line-height: 24px;
}
.nav-logo-icon {
  width: 24px;
  height: 24px;
  display: block;
  object-fit: contain;
}
</style>
