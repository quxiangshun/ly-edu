<template>
  <div class="courses-container">
    <AppHeader />
    <el-main class="main-content">
      <div class="courses-content">
        <h2>课程中心</h2>
        <el-row :gutter="20" v-loading="loading">
          <el-col :span="6" v-for="course in courseList" :key="course.id">
            <el-card class="course-card" shadow="hover" @click="router.push(`/course/${course.id}`)">
              <img
                :src="course.cover || 'https://via.placeholder.com/300x200'"
                class="course-image"
                :alt="course.title"
              />
              <div class="course-info">
                <h3>{{ course.title }}</h3>
                <p>{{ course.description || '暂无描述' }}</p>
                <el-button type="primary" size="small" @click.stop="handleStartLearn(course)">开始学习</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          layout="prev, pager, next"
          @current-change="loadCourses"
          style="margin-top: 20px; justify-content: center"
        />
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/AppHeader.vue'
import { getCoursePage, type Course } from '@/api/course'
import { joinCourse } from '@/api/learning'

const router = useRouter()
const loading = ref(false)
const courseList = ref<Course[]>([])
const pagination = reactive({
  page: 1,
  size: 12,
  total: 0
})

const loadCourses = async () => {
  loading.value = true
  try {
    const res = await getCoursePage({
      page: pagination.page,
      size: pagination.size
    })
    courseList.value = res.records
    pagination.total = res.total
  } catch (e) {
    ElMessage.error('加载课程失败')
  } finally {
    loading.value = false
  }
}

const handleStartLearn = async (course: Course) => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push({ path: '/login', query: { redirect: `/course/${course.id}` } })
    return
  }
  
  try {
    await joinCourse(course.id)
    ElMessage.success('已加入课程')
    router.push(`/course/${course.id}`)
  } catch (e) {
    ElMessage.error('加入课程失败')
  }
}

onMounted(() => {
  loadCourses()
})
</script>

<style scoped lang="scss">
.courses-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  background: #f5f7fa;
  padding: 40px 20px;
  margin-top: 60px;

  .courses-content {
    max-width: 1200px;
    margin: 0 auto;

    h2 {
      margin-bottom: 30px;
      color: #303133;
    }

    .course-card {
      margin-bottom: 20px;
      cursor: pointer;
      transition: transform 0.3s;

      &:hover {
        transform: translateY(-5px);
      }

      .course-image {
        width: 100%;
        height: 150px;
        object-fit: cover;
        margin-bottom: 15px;
      }

      .course-info {
        h3 {
          font-size: 16px;
          margin-bottom: 10px;
          color: #303133;
        }

        p {
          font-size: 14px;
          color: #909399;
          margin-bottom: 15px;
        }
      }
    }
  }
}
</style>
