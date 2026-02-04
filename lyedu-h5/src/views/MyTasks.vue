<template>
  <div class="page">
    <van-nav-bar title="我的任务" left-arrow @click-left="$router.back()" fixed placeholder />
    <div class="content">
      <van-loading v-if="loading" class="loading" size="24px">加载中...</van-loading>
      <van-cell-group v-else inset>
        <van-cell
          v-for="t in list"
          :key="t.task?.id ?? t.taskId"
          :title="(t.task?.title as string) || '任务'"
          :value="t.userTask?.status === 1 ? '已完成' : '进行中'"
        />
        <van-empty v-if="list.length === 0" description="暂无任务" />
      </van-cell-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMyTasks } from '@/api/userTask'

const list = ref<{ task?: { id?: number; title?: string }; taskId?: number; userTask?: { status?: number } }[]>([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const res = await getMyTasks()
    list.value = Array.isArray(res) ? res : []
  } catch {
    list.value = []
  } finally {
    loading.value = false
  }
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
.loading {
  display: flex;
  justify-content: center;
  padding: 24px;
}
</style>
