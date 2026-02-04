<template>
  <div class="page">
    <van-nav-bar title="我的证书" left-arrow @click-left="$router.back()" fixed placeholder />
    <div class="content">
      <van-loading v-if="loading" class="loading" size="24px">加载中...</van-loading>
      <van-cell-group v-else inset>
        <van-cell
          v-for="c in list"
          :key="c.id"
          :title="c.title || '证书'"
          :label="c.issuedAt || c.createTime"
        />
        <van-empty v-if="list.length === 0" description="暂无证书" />
      </van-cell-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMyCertificates } from '@/api/userCertificate'

const list = ref<{ id: number; title?: string; issuedAt?: string; createTime?: string }[]>([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const res = await getMyCertificates()
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
