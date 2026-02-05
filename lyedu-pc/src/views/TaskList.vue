<template>
  <div class="task-list-container">
    <AppHeader />
    <el-main class="main-content">
      <div class="task-content">
        <h2>我的任务</h2>
        <p class="subtitle">按顺序完成闯关项（课程学习 + 考试），全部完成后可获证书</p>
        <el-empty v-if="!loading && list.length === 0" description="暂无任务" />
        <el-table v-else :data="list" v-loading="loading" border class="task-table">
          <el-table-column prop="task.title" label="任务名称" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">{{ row.task?.title }}</template>
          </el-table-column>
          <el-table-column label="进度" width="120">
            <template #default="{ row }">
              <el-tag v-if="row.userTask?.status === 1" type="success">已完成</el-tag>
              <el-tag v-else type="info">进行中</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="goDetail(row.task?.id)">进入任务</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/AppHeader.vue'
import { getMyTasks, type TaskWithUserProgress } from '@/api/userTask'

const router = useRouter()
const loading = ref(false)
const list = ref<TaskWithUserProgress[]>([])

async function loadList() {
  loading.value = true
  try {
    const res = await getMyTasks()
    list.value = (res as unknown as { data: TaskWithUserProgress[] }).data ?? res ?? []
  } catch (e) {
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

function goDetail(taskId?: number) {
  if (taskId) router.push({ name: 'TaskDetail', params: { id: String(taskId) } })
}

onMounted(() => loadList())
</script>

<style scoped>
.task-list-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.main-content {
  flex: 1;
  padding: 24px 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  margin-top: 60px;
}
.task-content h2 {
  margin: 0 0 8px 0;
  font-size: 22px;
}
.subtitle {
  color: #666;
  margin: 0 0 20px 0;
}
.task-table {
  width: 100%;
}
</style>
