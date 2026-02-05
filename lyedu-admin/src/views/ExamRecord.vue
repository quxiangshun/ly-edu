<template>
  <div class="exam-record-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span>考试记录</span>
            <el-tooltip content="查看所有用户的考试记录和成绩" placement="right">
              <el-icon class="card-help-icon" @click="openPageHelp('exam-record')">
                <QuestionFilled />
              </el-icon>
            </el-tooltip>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="用户名/姓名/考试名称" clearable />
        </el-form-item>
        <el-form-item label="考试ID">
          <el-input-number v-model="searchForm.examId" :min="1" placeholder="考试ID" clearable />
        </el-form-item>
        <el-form-item label="用户ID">
          <el-input-number v-model="searchForm.userId" :min="1" placeholder="用户ID" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="recordList" v-loading="loading" border :max-height="tableMaxHeight">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="examId" label="考试ID" width="100" />
        <el-table-column prop="examTitle" label="考试名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="userId" label="用户ID" width="100" />
        <el-table-column prop="realName" label="姓名" width="120">
          <template #default="{ row }">
            {{ row.realName || row.username || '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="score" label="得分" width="100" align="center">
          <template #default="{ row }">
            <span :style="{ color: getScoreColor(row.score, row.passed) }" style="font-weight: 600;">
              {{ row.score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="passed" label="是否通过" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.passed === 1 ? 'success' : 'danger'">
              {{ row.passed === 1 ? '通过' : '未通过' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="submitTime" label="提交时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.submitTime) }}
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
import { getExamRecordPage, type ExamRecord } from '@/api/examRecord'
import { useHelp } from '@/hooks/useHelp'
import { useTableMaxHeight } from '@/hooks/useTableHeight'

const tableMaxHeight = useTableMaxHeight()
const { openPageHelp } = useHelp()

const loading = ref(false)
const recordList = ref<ExamRecord[]>([])

const searchForm = reactive({
  keyword: '',
  examId: undefined as number | undefined,
  userId: undefined as number | undefined
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

function getScoreColor(score: number, passed: number): string {
  if (passed === 1) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

async function loadRecords() {
  loading.value = true
  try {
    const res = await getExamRecordPage({
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword || undefined,
      examId: searchForm.examId,
      userId: searchForm.userId
    })
    recordList.value = res.records || []
    pagination.total = res.total || 0
  } catch (error: any) {
    ElMessage.error(error?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadRecords()
}

function handleReset() {
  searchForm.keyword = ''
  searchForm.examId = undefined
  searchForm.userId = undefined
  pagination.page = 1
  loadRecords()
}

function handleSizeChange(size: number) {
  pagination.size = size
  pagination.page = 1
  loadRecords()
}

function handlePageChange(page: number) {
  pagination.page = page
  loadRecords()
}

onMounted(() => {
  loadRecords()
})
</script>

<style scoped lang="scss">
.exam-record-container {
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
