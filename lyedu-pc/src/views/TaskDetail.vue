<template>
  <div class="task-detail-container">
    <AppHeader />
    <el-main class="main-content">
      <div v-if="loading" class="loading-wrap">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      <div v-else-if="task" class="task-detail-content">
        <h2>{{ task.title }}</h2>
        <p v-if="task.description" class="desc">{{ task.description }}</p>
        <div class="progress-bar" v-if="userTask">
          <el-tag v-if="userTask.status === 1" type="success">已完成</el-tag>
          <el-tag v-else type="info">进行中</el-tag>
          <el-button type="primary" size="small" @click="syncProgress" :loading="syncing" style="margin-left: 12px">
            同步进度
          </el-button>
        </div>
        <h3>闯关项（按顺序完成）</h3>
        <ul class="items-list">
          <li v-for="(item, index) in itemsList" :key="index" class="item-row">
            <span class="item-index">{{ index + 1 }}.</span>
            <el-tag v-if="itemDone(item)" type="success" size="small">已完成</el-tag>
            <el-tag v-else type="info" size="small">未完成</el-tag>
            <template v-if="item.type === 'course'">
              <router-link :to="{ name: 'CourseDetail', params: { id: String(item.id) } }" class="item-link">
                课程：{{ courseNameMap.get(item.id) ?? 'ID ' + item.id }}
              </router-link>
            </template>
            <template v-else-if="item.type === 'exam'">
              <router-link :to="{ name: 'ExamTake', params: { id: String(item.id) } }" class="item-link">
                考试：{{ examNameMap.get(item.id) ?? 'ID ' + item.id }}
              </router-link>
            </template>
            <span v-else>{{ item.type }} ID {{ item.id }}</span>
          </li>
        </ul>
        <el-empty v-if="itemsList.length === 0" description="暂无闯关项" />
        <div class="back-wrap">
          <el-button @click="$router.push('/tasks')">返回任务列表</el-button>
        </div>
      </div>
      <el-empty v-else description="任务不存在或无权查看" />
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import AppHeader from '@/components/AppHeader.vue'
import { getTaskDetail, getOrCreateProgress, updateProgress, type UserTask } from '@/api/userTask'
import { getMyCourses } from '@/api/learning'
import { getMyRecords } from '@/api/exam'
import { getCourseById } from '@/api/course'
import { getExamById } from '@/api/exam'
import type { Task } from '@/api/task'

const route = useRoute()
const loading = ref(true)
const syncing = ref(false)
const task = ref<Task | null>(null)
const userTask = ref<UserTask | null>(null)
const myCourses = ref<{ courseId: number; progress: number }[]>([])
const myRecords = ref<{ examId: number; passed?: number }[]>([])
const courseNameMap = ref(new Map<number, string>())
const examNameMap = ref(new Map<number, string>())

const taskId = computed(() => Number(route.params.id))

interface ItemRow {
  type: string
  id: number
}

const itemsList = computed((): ItemRow[] => {
  const t = task.value
  if (!t?.items) return []
  try {
    const arr = JSON.parse(t.items)
    return Array.isArray(arr) ? arr : []
  } catch {
    return []
  }
})

function itemDone(item: ItemRow): boolean {
  if (item.type === 'course') {
    const c = myCourses.value.find((x) => x.courseId === item.id)
    return (c?.progress ?? 0) >= 100
  }
  if (item.type === 'exam') {
    const r = myRecords.value.find((x) => x.examId === item.id)
    return r?.passed === 1
  }
  return false
}

function buildProgressJson(): string {
  const items = itemsList.value.map((item) => ({
    type: item.type,
    id: item.id,
    done: itemDone(item) ? 1 : 0
  }))
  return JSON.stringify({ items })
}

async function syncProgress() {
  if (!taskId.value) return
  syncing.value = true
  try {
    const progress = buildProgressJson()
    const res = await updateProgress(taskId.value, progress)
    userTask.value = (res as unknown as { data: UserTask })?.data ?? res
    ElMessage.success('进度已同步')
  } catch (e) {
    ElMessage.error('同步失败')
  } finally {
    syncing.value = false
  }
}

async function loadDetail() {
  if (!taskId.value) {
    loading.value = false
    return
  }
  loading.value = true
  try {
    const [t, ut, courses, records] = await Promise.all([
      getTaskDetail(taskId.value),
      getOrCreateProgress(taskId.value),
      getMyCourses(),
      getMyRecords()
    ])
    task.value = (t as unknown as { data?: Task })?.data ?? (t as Task) ?? null
    userTask.value = (ut as unknown as { data?: UserTask })?.data ?? (ut as UserTask) ?? null
    const courseList = (courses as unknown as { data?: { courseId: number; progress: number }[] })?.data ?? (courses as { courseId: number; progress: number }[])
    myCourses.value = Array.isArray(courseList) ? courseList : []
    const recordList = (records as unknown as { data?: { examId: number; passed?: number }[] })?.data ?? (records as { examId: number; passed?: number }[])
    myRecords.value = Array.isArray(recordList) ? recordList : []
    const items = itemsList.value
    const courseIds = items.filter((i) => i.type === 'course').map((i) => i.id)
    const examIds = items.filter((i) => i.type === 'exam').map((i) => i.id)
    for (const id of courseIds) {
      try {
        const c = await getCourseById(id)
        const name = (c as unknown as { data?: { title?: string } })?.data?.title ?? (c as { title?: string })?.title
        if (name) courseNameMap.value.set(id, name)
      } catch (_) {}
    }
    for (const id of examIds) {
      try {
        const e = await getExamById(id)
        const name = (e as unknown as { data?: { title?: string } })?.data?.title ?? (e as { title?: string })?.title
        if (name) examNameMap.value.set(id, name)
      } catch (_) {}
    }
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => loadDetail())
</script>

<style scoped>
.task-detail-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.main-content {
  flex: 1;
  padding: 24px 20px;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
  margin-top: 60px;
}
.loading-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
}
.task-detail-content h2 {
  margin: 0 0 8px 0;
  font-size: 22px;
}
.desc {
  color: #666;
  margin: 0 0 16px 0;
}
.progress-bar {
  margin-bottom: 20px;
}
.task-detail-content h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
}
.items-list {
  list-style: none;
  padding: 0;
  margin: 0 0 24px 0;
}
.item-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}
.item-index {
  min-width: 24px;
}
.item-link {
  color: var(--el-color-primary);
  text-decoration: none;
}
.item-link:hover {
  text-decoration: underline;
}
.back-wrap {
  margin-top: 24px;
}
</style>
