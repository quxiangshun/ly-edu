<template>
  <div class="exam-result-page">
    <van-nav-bar title="考试成绩" left-arrow fixed placeholder @click-left="$router.push('/exam')" />

    <div class="content">
      <van-result
        v-if="record"
        :icon="record.passed === 1 ? 'success' : 'fail'"
        :title="record.passed === 1 ? '考试通过' : '未通过'"
      >
        <template #default>
          <p class="result-score">得分：{{ record.score ?? 0 }} 分</p>
          <p v-if="record.submitTime" class="submit-time">交卷时间：{{ formatTime(record.submitTime) }}</p>
        </template>
        <template #button>
          <van-button type="primary" block round @click="$router.push('/exam')">返回考试列表</van-button>
        </template>
      </van-result>
      <van-empty v-else description="暂无成绩记录" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { ExamRecord } from '@/api/exam'

const router = useRouter()
const record = ref<ExamRecord | null>(null)

function formatTime(s?: string) {
  if (!s) return '-'
  return s.replace('T', ' ').slice(0, 19)
}

onMounted(() => {
  const state = history.state as { record?: ExamRecord }
  record.value = state?.record ?? null
  if (!record.value) router.replace('/exam')
})
</script>

<style scoped lang="scss">
.exam-result-page {
  min-height: 100vh;
  background: #f7f8fa;
}
.content {
  padding: 24px 16px;
}
.result-score {
  font-size: 18px;
  color: #323233;
  margin: 12px 0;
}
.submit-time {
  font-size: 13px;
  color: #969799;
}
</style>
