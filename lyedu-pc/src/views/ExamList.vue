<template>
  <div class="exam-list-container">
    <AppHeader />
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
import AppHeader from '@/components/AppHeader.vue'
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
  .main-content {
    max-width: 900px;
    margin: 0 auto;
    padding: 24px 16px;
    margin-top: 60px;
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
