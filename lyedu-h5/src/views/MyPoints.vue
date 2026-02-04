<template>
  <div class="page">
    <van-nav-bar title="我的积分" left-arrow @click-left="$router.back()" fixed placeholder />
    <div class="content">
      <div class="total-card">
        <div class="total-value">{{ total }}</div>
        <div class="total-label">当前积分</div>
      </div>
      <van-tabs v-model:active="activeTab">
        <van-tab title="积分流水" name="log">
          <van-loading v-if="logLoading" class="loading" size="24px">加载中...</van-loading>
          <van-cell-group v-else inset>
            <van-cell
              v-for="item in logList"
              :key="item.id"
              :title="item.remark || '积分变动'"
              :value="`+${item.points}`"
              :label="item.createTime"
            />
            <van-empty v-if="logList.length === 0" description="暂无积分流水" />
          </van-cell-group>
        </van-tab>
        <van-tab title="积分排行" name="rank">
          <van-loading v-if="rankLoading" class="loading" size="24px">加载中...</van-loading>
          <van-cell-group v-else inset>
            <van-cell
              v-for="r in rankingList"
              :key="r.userId"
              :title="r.realName || r.username || '-'"
              :value="`${r.totalPoints} 分`"
              :label="`第 ${r.rank} 名`"
            />
            <van-empty v-if="rankingList.length === 0" description="暂无排行" />
          </van-cell-group>
        </van-tab>
      </van-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { getMyTotal, getMyLog, getRanking } from '@/api/point'

const total = ref(0)
const activeTab = ref('log')
const logList = ref<{ id: number; remark?: string; points: number; createTime?: string }[]>([])
const rankingList = ref<{ userId: number; realName?: string; username?: string; totalPoints: number; rank: number }[]>([])
const logLoading = ref(false)
const rankLoading = ref(false)

async function loadTotal() {
  try {
    const n = await getMyTotal()
    total.value = typeof n === 'number' ? n : 0
  } catch {
    total.value = 0
  }
}

async function loadLog() {
  logLoading.value = true
  try {
    const list = await getMyLog({ page: 1, size: 50 })
    logList.value = Array.isArray(list) ? list : []
  } catch {
    logList.value = []
  } finally {
    logLoading.value = false
  }
}

async function loadRanking() {
  rankLoading.value = true
  try {
    const list = await getRanking({ limit: 50 })
    rankingList.value = Array.isArray(list) ? list : []
  } catch {
    rankingList.value = []
  } finally {
    rankLoading.value = false
  }
}

onMounted(() => {
  loadTotal()
  loadLog()
  loadRanking()
})
watch(activeTab, (name) => {
  if (name === 'rank' && rankingList.value.length === 0) loadRanking()
})
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #f7f8fa;
}
.content {
  padding: 16px;
}
.total-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  margin-bottom: 16px;
  .total-value {
    font-size: 36px;
    font-weight: bold;
  }
  .total-label {
    font-size: 14px;
    opacity: 0.9;
    margin-top: 8px;
  }
}
.loading {
  display: flex;
  justify-content: center;
  padding: 24px;
}
</style>
