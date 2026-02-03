<template>
  <div class="exam-list-container">
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <img src="/icon-192.png" alt="" class="header-logo-icon" />
          <h1>LyEdu</h1>
        </div>
        <el-menu mode="horizontal" default-active="exam" class="header-menu">
          <el-menu-item index="home" @click="$router.push('/')">首页</el-menu-item>
          <el-menu-item index="courses" @click="$router.push('/courses')">课程中心</el-menu-item>
          <el-menu-item index="knowledge" @click="$router.push('/knowledge')">知识中心</el-menu-item>
          <el-menu-item index="exam">考试中心</el-menu-item>
          <el-menu-item index="certificates" @click="$router.push('/certificates')">我的证书</el-menu-item>
          <el-menu-item index="tasks" @click="$router.push('/tasks')">我的任务</el-menu-item>
          <el-menu-item index="my" @click="$router.push('/my-learning')">我的学习</el-menu-item>
        </el-menu>
      </div>
    </el-header>
    <el-main class="main-content">
      <div class="exam-content">
        <h2>考试中心</h2>
        <p class="subtitle">可参加的考试（按部门可见）</p>
        <el-table :data="examList" v-loading="loading" border class="exam-table">
          <el-table-column prop="title" label="考试名称" min-width="200" show-overflow-tooltip />
          <el-table-column prop="startTime" label="开始时间" width="170">
            <template #default="{ row }">{{ row.startTime ? formatTime(row.startTime) : '-' }}</template>
          </el-table-column>
          <el-table-column prop="endTime" label="结束时间" width="170">
            <template #default="{ row }">{{ row.endTime ? formatTime(row.endTime) : '-' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button
                v-if="recordMap.get(row.id)"
                type="success"
                link
                @click="goResult(row)"
              >
                查看成绩 ({{ recordMap.get(row.id)?.score }}分)
              </el-button>
              <el-button v-else type="primary" link @click="goTake(row)">参加考试</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          layout="prev, pager, next"
          @current-change="loadList"
          style="margin-top: 20px; justify-content: center"
        />
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getExamPage, getMyRecords, type Exam, type ExamRecord } from '@/api/exam'

const router = useRouter()
const loading = ref(false)
const examList = ref<Exam[]>([])
const myRecords = ref<ExamRecord[]>([])
const recordMap = computed(() => {
  const map = new Map<number, ExamRecord>()
  myRecords.value.forEach((r) => map.set(r.examId, r))
  return map
})
const pagination = reactive({ page: 1, size: 15, total: 0 })

function formatTime(s: string) {
  if (!s) return '-'
  return s.replace('T', ' ').slice(0, 19)
}

async function loadList() {
  loading.value = true
  try {
    const [examRes, recordsRes] = await Promise.all([
      getExamPage({ page: pagination.page, size: pagination.size }),
      getMyRecords()
    ])
    examList.value = examRes?.records ?? []
    pagination.total = examRes?.total ?? 0
    myRecords.value = recordsRes ?? []
  } catch (_e) {
    examList.value = []
  } finally {
    loading.value = false
  }
}

function goTake(row: Exam) {
  router.push(`/exam/${row.id}/take`)
}

function goResult(row: Exam) {
  const r = recordMap.value.get(row.id)
  if (r) router.push({ path: `/exam/${row.id}/result`, state: { record: r } })
}

onMounted(loadList)
</script>

<style scoped lang="scss">
.exam-list-container {
  min-height: 100vh;
  .header {
    background: #fff;
    border-bottom: 1px solid #e4e7ed;
    padding: 0 24px;
  }
  .header-content {
    max-width: 1000px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .logo {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    .header-logo-icon {
      width: 32px;
      height: 32px;
    }
    h1 {
      margin: 0;
      font-size: 20px;
      color: #409eff;
    }
  }
  .main-content {
    max-width: 900px;
    margin: 0 auto;
    padding: 24px 16px;
  }
  .exam-content {
    h2 {
      margin: 0 0 8px;
    }
    .subtitle {
      color: #909399;
      margin: 0 0 20px;
    }
    .exam-table {
      width: 100%;
    }
  }
}
</style>
