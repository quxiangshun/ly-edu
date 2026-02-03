<template>
  <div class="my-points-container">
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <img src="/icon-192.png" alt="" class="header-logo-icon" />
          <h1>LyEdu</h1>
        </div>
        <el-menu mode="horizontal" default-active="points" class="header-menu">
          <el-menu-item index="home" @click="$router.push('/')">首页</el-menu-item>
          <el-menu-item index="courses" @click="$router.push('/courses')">课程中心</el-menu-item>
          <el-menu-item index="knowledge" @click="$router.push('/knowledge')">知识中心</el-menu-item>
          <el-menu-item index="exam" @click="$router.push('/exam')">考试中心</el-menu-item>
          <el-menu-item index="certificates" @click="$router.push('/certificates')">我的证书</el-menu-item>
          <el-menu-item index="tasks" @click="$router.push('/tasks')">我的任务</el-menu-item>
          <el-menu-item index="points">积分</el-menu-item>
          <el-menu-item index="my" @click="$router.push('/my-learning')">我的学习</el-menu-item>
        </el-menu>
      </div>
    </el-header>
    <el-main class="main-content">
      <div class="points-content">
        <h2>我的积分</h2>
        <p class="subtitle">完成课程、考试合格、完成任务可获得积分</p>

        <el-row :gutter="24" class="summary-row">
          <el-col :span="8">
            <el-card shadow="hover" class="total-card">
              <div class="total-value">{{ totalPoints }}</div>
              <div class="total-label">当前积分</div>
            </el-card>
          </el-col>
        </el-row>

        <el-tabs v-model="activeTab" class="points-tabs">
          <el-tab-pane label="积分流水" name="log">
            <el-table :data="logList" v-loading="logLoading" border class="log-table">
              <el-table-column prop="remark" label="说明" min-width="160" show-overflow-tooltip />
              <el-table-column prop="points" label="积分" width="100">
                <template #default="{ row }">+{{ row.points }}</template>
              </el-table-column>
              <el-table-column prop="createTime" label="时间" width="180">
                <template #default="{ row }">{{ row.createTime ? formatTime(row.createTime) : '-' }}</template>
              </el-table-column>
            </el-table>
            <el-pagination
              v-model:current-page="logPage"
              v-model:page-size="logSize"
              :total="logTotal"
              :page-sizes="[10, 20]"
              layout="total, prev, pager, next"
              @current-change="loadLog"
              @size-change="loadLog"
              style="margin-top: 16px"
            />
          </el-tab-pane>
          <el-tab-pane label="积分排行" name="ranking">
            <el-table :data="rankingList" v-loading="rankLoading" border class="rank-table">
              <el-table-column prop="rank" label="排名" width="80" />
              <el-table-column prop="realName" label="姓名" min-width="120">
                <template #default="{ row }">{{ row.realName || row.username || '-' }}</template>
              </el-table-column>
              <el-table-column prop="totalPoints" label="积分" width="100" />
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getMyTotal, getMyLog, getRanking, type PointLogItem, type RankingItem } from '@/api/point'

const totalPoints = ref(0)
const activeTab = ref('log')
const logList = ref<PointLogItem[]>([])
const logLoading = ref(false)
const logPage = ref(1)
const logSize = ref(20)
const logTotal = ref(0)
const rankingList = ref<RankingItem[]>([])
const rankLoading = ref(false)

function formatTime(s: string) {
  if (!s) return '-'
  return s.replace('T', ' ').slice(0, 19)
}

async function loadTotal() {
  try {
    const res = await getMyTotal()
    totalPoints.value = (res as unknown as { data: number })?.data ?? res ?? 0
  } catch (_e) {
    totalPoints.value = 0
  }
}

async function loadLog() {
  logLoading.value = true
  try {
    const res = await getMyLog({ page: logPage.value, size: logSize.value })
    const arr = (res as unknown as { data: PointLogItem[] })?.data ?? res ?? []
    logList.value = Array.isArray(arr) ? arr : []
    logTotal.value = logList.value.length
  } catch (_e) {
    logList.value = []
  } finally {
    logLoading.value = false
  }
}

async function loadRanking() {
  rankLoading.value = true
  try {
    const res = await getRanking({ limit: 50 })
    rankingList.value = (res as unknown as { data: RankingItem[] })?.data ?? res ?? []
  } catch (_e) {
    rankingList.value = []
  } finally {
    rankLoading.value = false
  }
}

watch(activeTab, (tab) => {
  if (tab === 'ranking' && rankingList.value.length === 0) loadRanking()
})

onMounted(() => {
  loadTotal()
  loadLog()
})
</script>

<style scoped>
.my-points-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.header {
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  padding: 0 24px;
}
.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  height: 60px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  margin-right: 24px;
}
.header-logo-icon {
  width: 32px;
  height: 32px;
  object-fit: contain;
}
.header-menu {
  flex: 1;
  border: none;
}
.main-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px 16px;
  flex: 1;
}
.points-content h2 {
  margin: 0 0 8px;
  font-size: 22px;
}
.subtitle {
  color: #909399;
  margin: 0 0 24px;
  font-size: 14px;
}
.summary-row {
  margin-bottom: 24px;
}
.total-card {
  text-align: center;
}
.total-value {
  font-size: 36px;
  font-weight: bold;
  color: #409eff;
}
.total-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}
.points-tabs {
  margin-top: 16px;
}
.log-table,
.rank-table {
  margin-top: 8px;
}
</style>
