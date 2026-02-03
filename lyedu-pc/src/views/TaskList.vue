<template>
  <div class="task-list-container">
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <img src="/icon-192.png" alt="" class="header-logo-icon" />
          <h1>LyEdu</h1>
        </div>
        <el-menu mode="horizontal" default-active="tasks" class="header-menu">
          <el-menu-item index="home" @click="$router.push('/')">首页</el-menu-item>
          <el-menu-item index="courses" @click="$router.push('/courses')">课程中心</el-menu-item>
          <el-menu-item index="knowledge" @click="$router.push('/knowledge')">知识中心</el-menu-item>
          <el-menu-item index="exam" @click="$router.push('/exam')">考试中心</el-menu-item>
          <el-menu-item index="certificates" @click="$router.push('/certificates')">我的证书</el-menu-item>
          <el-menu-item index="tasks">我的任务</el-menu-item>
          <el-menu-item index="my" @click="$router.push('/my-learning')">我的学习</el-menu-item>
        </el-menu>
      </div>
    </el-header>
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
.header {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  padding: 0;
  height: 56px;
}
.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  margin-right: 32px;
}
.header-logo-icon {
  width: 32px;
  height: 32px;
}
.header-menu {
  flex: 1;
  border: none;
}
.main-content {
  flex: 1;
  padding: 24px 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
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
