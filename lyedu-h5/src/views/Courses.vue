<template>
  <div class="courses-container">
    <van-nav-bar title="课程中心" left-arrow @click-left="$router.back()" fixed placeholder />
    
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab title="全部" name="all">
        <div class="courses-list" v-loading="loading">
          <van-card
            v-for="course in courseList"
            :key="course.id"
            :title="course.title"
            :desc="course.description || '暂无描述'"
            :thumb="course.cover || 'https://via.placeholder.com/200x120'"
            @click="handleCourseClick(course)"
          >
            <template #tags>
              <van-tag type="primary" v-if="course.status === 1">上架</van-tag>
            </template>
            <template #footer>
              <van-button size="mini" type="primary" @click.stop="handleStartLearn(course)">开始学习</van-button>
            </template>
          </van-card>
          <van-empty v-if="!loading && courseList.length === 0" description="暂无课程" />
        </div>
      </van-tab>
      <van-tab title="进行中" name="ongoing">
        <van-empty description="暂无进行中的课程" />
      </van-tab>
      <van-tab title="已完成" name="completed">
        <van-empty description="暂无已完成的课程" />
      </van-tab>
    </van-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showSuccessToast, showFailToast } from 'vant'
import { getCoursePage, type Course } from '@/api/course'
import { joinCourse } from '@/api/learning'

const router = useRouter()
const activeTab = ref('all')
const loading = ref(false)
const courseList = ref<Course[]>([])

const loadCourses = async () => {
  loading.value = true
  try {
    const res = await getCoursePage({ page: 1, size: 20 })
    courseList.value = res.records
  } catch (e) {
    showFailToast('加载课程失败')
  } finally {
    loading.value = false
  }
}

const handleCourseClick = async (course: Course) => {
  router.push(`/course/${course.id}`)
}

const handleStartLearn = async (course: Course) => {
  const token = localStorage.getItem('token')
  if (!token) {
    showFailToast('请先登录')
    router.push({ path: '/login', query: { redirect: `/course/${course.id}` } })
    return
  }
  
  try {
    await joinCourse(course.id)
    showSuccessToast('已加入课程')
    router.push(`/course/${course.id}`)
  } catch (e) {
    showFailToast('加入课程失败')
  }
}

onMounted(() => {
  loadCourses()
})
</script>

<style scoped lang="scss">
.courses-container {
  min-height: 100vh;
  background: #f7f8fa;
}

.courses-list {
  padding: 10px;
}
</style>
