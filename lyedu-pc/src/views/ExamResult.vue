<template>
  <div class="exam-result-container">
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <img src="/icon-192.png" alt="" class="header-logo-icon" />
          <h1>LyEdu</h1>
        </div>
        <span class="title">考试成绩</span>
        <el-button type="primary" link @click="$router.push('/exam')">返回考试列表</el-button>
      </div>
    </el-header>
    <el-main class="main-content">
      <el-result
        v-if="record"
        :icon="record.passed === 1 ? 'success' : 'warning'"
        :title="record.passed === 1 ? '考试通过' : '未通过'"
      >
        <template #sub-title>
          <p>得分：{{ record.score ?? 0 }} 分</p>
          <p v-if="record.submitTime" class="submit-time">交卷时间：{{ formatTime(record.submitTime) }}</p>
        </template>
        <template #extra>
          <el-button type="primary" @click="$router.push('/exam')">返回考试列表</el-button>
        </template>
      </el-result>
      <el-empty v-else description="暂无成绩记录" />
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { ExamRecord } from '@/api/exam'

const route = useRoute()
const router = useRouter()
const record = ref<ExamRecord | null>(null)

function formatTime(s?: string) {
  if (!s) return '-'
  return s.replace('T', ' ').slice(0, 19)
}

onMounted(() => {
  const state = history.state as { record?: ExamRecord }
  record.value = state?.record ?? null
  if (!record.value) {
    router.replace('/exam')
  }
})
</script>

<style scoped lang="scss">
.exam-result-container {
  min-height: 100vh;
  .header {
    background: #fff;
    border-bottom: 1px solid #e4e7ed;
    padding: 0 24px;
  }
  .header-content {
    max-width: 900px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    gap: 16px;
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
  .title {
    flex: 1;
    font-size: 16px;
    color: #303133;
  }
  .main-content {
    max-width: 900px;
    margin: 0 auto;
    padding: 24px 16px;
  }
  .submit-time {
    margin-top: 8px;
    color: #909399;
    font-size: 14px;
  }
}
</style>
