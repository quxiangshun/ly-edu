<template>
  <div class="user-task-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span>用户任务</span>
            <el-tooltip content="查看所有用户的任务完成情况" placement="right">
              <el-icon class="card-help-icon" @click="openPageHelp('user-task')">
                <QuestionFilled />
              </el-icon>
            </el-tooltip>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="用户名/姓名/任务名称" clearable />
        </el-form-item>
        <el-form-item label="用户ID">
          <el-input-number v-model="searchForm.userId" :min="1" placeholder="用户ID" clearable />
        </el-form-item>
        <el-form-item label="任务ID">
          <el-input-number v-model="searchForm.taskId" :min="1" placeholder="任务ID" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="taskList" v-loading="loading" border :max-height="tableMaxHeight">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="userId" label="用户ID" width="100" />
        <el-table-column prop="realName" label="姓名" width="120">
          <template #default="{ row }">
            {{ row.realName || row.username || '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="taskId" label="任务ID" width="100" />
        <el-table-column prop="taskTitle" label="任务名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="完成状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '已完成' : '进行中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="completedAt" label="完成时间" width="180">
          <template #default="{ row }">
            {{ row.status === 1 ? formatTime(row.completedAt) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="updateTime" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.updateTime) }}
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import { getUserTaskPage, type UserTask } from '@/api/userTask'
import { useHelp } from '@/hooks/useHelp'
import { useTableMaxHeight } from '@/hooks/useTableHeight'

const tableMaxHeight = useTableMaxHeight()
const { openPageHelp } = useHelp()

const loading = ref(false)
const taskList = ref<UserTask[]>([])

const searchForm = reactive({
  keyword: '',
  userId: undefined as number | undefined,
  taskId: undefined as number | undefined
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

function formatTime(time?: string): string {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

async function loadTasks() {
  loading.value = true
  try {
    const res = await getUserTaskPage({
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword || undefined,
      userId: searchForm.userId,
      taskId: searchForm.taskId
    })
    taskList.value = res.records || []
    pagination.total = res.total || 0
  } catch (error: any) {
    ElMessage.error(error?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadTasks()
}

function handleReset() {
  searchForm.keyword = ''
  searchForm.userId = undefined
  searchForm.taskId = undefined
  pagination.page = 1
  loadTasks()
}

function handleSizeChange(size: number) {
  pagination.size = size
  pagination.page = 1
  loadTasks()
}

function handlePageChange(page: number) {
  pagination.page = page
  loadTasks()
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped lang="scss">
.user-task-container {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .card-header-left {
    display: flex;
    align-items: center;
    gap: 8px;

    .card-help-icon {
      font-size: 16px;
      color: #909399;
      cursor: pointer;
      transition: color 0.3s;

      &:hover {
        color: var(--el-color-primary);
      }
    }
  }
}

.search-form {
  margin-bottom: 20px;
}
</style>
