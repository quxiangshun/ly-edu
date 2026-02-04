<template>
  <div class="exam-list-page">
    <van-nav-bar title="考试中心" left-arrow fixed placeholder @click-left="$router.back()" />

    <div class="content">
      <p class="subtitle">可参加的考试（按部门可见）</p>

      <van-loading v-if="loading" class="loading-wrap" vertical>加载中...</van-loading>

      <template v-else>
        <van-empty v-if="!examList.length" description="暂无考试" />
        <van-cell-group v-else inset>
          <div
            v-for="row in examList"
            :key="row.id"
            class="exam-card"
            @click="row.record ? goResult(row) : goTake(row)"
          >
            <div class="exam-card-title">{{ row.title }}</div>
            <div class="exam-card-info">
              <span v-if="row.startTime">开始：{{ formatTime(row.startTime) }}</span>
              <span v-if="row.endTime">结束：{{ formatTime(row.endTime) }}</span>
            </div>
            <div class="exam-card-info">
              <span v-if="row.durationMinutes">时长 {{ row.durationMinutes }} 分钟</span>
              <span v-if="row.passScore != null">及格分 {{ row.passScore }} 分</span>
            </div>
            <div class="exam-card-action">
              <van-tag v-if="row.record" type="success">已考 {{ row.record.score }} 分</van-tag>
              <van-button v-else type="primary" size="small" round>参加考试</van-button>
            </div>
          </div>
        </van-cell-group>

        <van-pagination
          v-if="pagination.total > pagination.size"
          v-model="pagination.page"
          :total-items="pagination.total"
          :items-per-page="pagination.size"
          :show-page-size="3"
          force-ellipses
          @change="onPageChange"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getExamPage, getMyRecords, type Exam, type ExamRecord } from '@/api/exam'

const router = useRouter()
const loading = ref(false)
const examList = ref<(Exam & { record?: ExamRecord })[]>([])
const myRecords = ref<ExamRecord[]>([])
const pagination = reactive({ page: 1, size: 15, total: 0 })

function formatTime(s: string) {
  if (!s) return '-'
  return s.replace('T', ' ').slice(0, 16)
}

async function loadList() {
  loading.value = true
  try {
    const [examRes, recordsRes] = await Promise.all([
      getExamPage({ page: pagination.page, size: pagination.size }),
      getMyRecords()
    ])
    const list = examRes?.records ?? []
    const records = recordsRes ?? []
    myRecords.value = records
    const rMap = new Map<number, ExamRecord>()
    records.forEach((r) => rMap.set(r.examId, r))
    examList.value = list.map((row) => ({ ...row, record: rMap.get(row.id) }))
    pagination.total = examRes?.total ?? 0
  } catch (_e) {
    examList.value = []
  } finally {
    loading.value = false
  }
}

function goTake(row: Exam) {
  router.push(`/exam/${row.id}/take`)
}

function goResult(row: Exam & { record?: ExamRecord }) {
  const r = row.record
  if (r) router.push({ path: `/exam/${row.id}/result`, state: { record: r } })
}

onMounted(loadList)
</script>

<style scoped lang="scss">
.exam-list-page {
  min-height: 100vh;
  background: #f7f8fa;
}
.content {
  padding: 16px;
}
.subtitle {
  color: #969799;
  font-size: 13px;
  margin: 0 0 16px;
}
.loading-wrap {
  padding: 40px 0;
}
.exam-card {
  background: #fff;
  border-radius: 8px;
  padding: 14px 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.exam-card-title {
  font-weight: 600;
  font-size: 16px;
  color: #323233;
  margin-bottom: 8px;
}
.exam-card-info {
  font-size: 12px;
  color: #969799;
  margin-bottom: 4px;
}
.exam-card-info span + span {
  margin-left: 16px;
}
.exam-card-action {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
.van-pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>
