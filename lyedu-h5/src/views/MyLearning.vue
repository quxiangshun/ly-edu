<template>
  <div class="my-learning-container">
    <van-nav-bar title="我的学习" left-arrow @click-left="$router.back()" />
    <div class="desc">展示您已加入的课程</div>
    <template v-if="!token">
      <van-empty description="请先登录后查看学习记录">
        <van-button type="primary" round @click="$router.push('/login')">去登录</van-button>
      </van-empty>
    </template>
    <template v-else>
      <van-loading v-if="loading" class="loading" size="24px">加载中...</van-loading>
      <div v-else-if="courseList.length === 0" class="empty-wrap">
        <van-empty description="暂无已加入课程，去课程中心看看吧">
          <van-button type="primary" round @click="$router.push('/courses')">去选课</van-button>
        </van-empty>
      </div>
      <div v-else class="course-list">
        <van-card
          v-for="item in courseList"
          :key="item.course.id"
          :title="item.course.title"
          :desc="item.course.description || '暂无描述'"
          :thumb="item.course.cover || 'https://via.placeholder.com/200x120'"
          @click="$router.push(`/course/${item.course.id}`)"
        >
          <template #tags>
            <div class="progress-wrap">
              <van-progress :percentage="item.progress ?? 0" :stroke-width="6" />
              <van-tag type="primary" style="margin-top: 6px">继续学习</van-tag>
            </div>
          </template>
        </van-card>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMyCourses } from '@/api/learning'
import { getCourseById, type Course } from '@/api/course'

const token = ref<string | null>(localStorage.getItem('token'))
const loading = ref(false)
const courseList = ref<{ course: Course; progress: number }[]>([])

const loadMyCourses = async () => {
  if (!token.value) return
  loading.value = true
  try {
    const res = await getMyCourses()
    const rows = Array.isArray(res) ? res : []
    const courseIds = rows
      .map((r: any) => Number(r.courseId ?? r.course_id))
      .filter((id: number) => Number.isFinite(id) && id > 0)
    const uniqIds = Array.from(new Set(courseIds))
    const details = await Promise.all(
      uniqIds.map(async (id) => {
        try {
          const d = await getCourseById(id)
          return d?.course ? d.course : null
        } catch {
          return null
        }
      })
    )
    const idToCourse = new Map<number, Course>()
    details.forEach((c) => {
      if (c?.id) idToCourse.set(c.id, c)
    })
    courseList.value = rows
      .map((r: any) => {
        const cid = Number(r.courseId ?? r.course_id)
        const course = idToCourse.get(cid)
        if (!course) return null
        return { course, progress: Number(r.progress ?? 0) }
      })
      .filter(Boolean) as { course: Course; progress: number }[]
  } catch {
    courseList.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  token.value = localStorage.getItem('token')
  loadMyCourses()
})
</script>

<style scoped lang="scss">
.my-learning-container {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 20px;
}

.desc {
  padding: 12px 16px;
  font-size: 14px;
  color: #969799;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

.empty-wrap {
  padding-top: 40px;
}

.course-list {
  padding: 0 16px;

  .progress-wrap {
    margin-top: 8px;
  }

  :deep(.van-card) {
    margin-bottom: 12px;
    border-radius: 8px;
    overflow: hidden;
  }
}
</style>
