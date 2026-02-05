<template>
  <div class="my-certificates-container">
    <AppHeader />
    <el-main class="main-content">
      <div class="cert-content">
        <h2>我的证书</h2>
        <p class="subtitle">考试/任务合格后自动颁发</p>
        <el-empty v-if="!loading && list.length === 0" description="暂无证书" />
        <el-table v-else :data="list" v-loading="loading" border class="cert-table">
          <el-table-column prop="title" label="证书名称" min-width="200" show-overflow-tooltip />
          <el-table-column prop="certificateNo" label="证书编号" width="220" show-overflow-tooltip />
          <el-table-column prop="issuedAt" label="颁发时间" width="180">
            <template #default="{ row }">{{ row.issuedAt ? formatTime(row.issuedAt) : '-' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="goPrint(row)">查看/打印</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/AppHeader.vue'
import { getMyCertificates, type UserCertificate } from '@/api/userCertificate'

const router = useRouter()
const loading = ref(false)
const list = ref<UserCertificate[]>([])

function formatTime(s: string) {
  if (!s) return '-'
  return s.replace('T', ' ').slice(0, 19)
}

async function loadList() {
  loading.value = true
  try {
    const res = await getMyCertificates()
    list.value = (res as unknown as { data: UserCertificate[] }).data ?? res ?? []
  } catch (e) {
    ElMessage.error('加载证书列表失败')
  } finally {
    loading.value = false
  }
}

function goPrint(row: UserCertificate) {
  router.push({ name: 'CertificatePrint', params: { id: String(row.id) } })
}

onMounted(() => loadList())
</script>

<style scoped>
.my-certificates-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.main-content {
  flex: 1;
  padding: 24px 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  margin-top: 60px;
}
.cert-content h2 {
  margin: 0 0 8px 0;
  font-size: 22px;
}
.subtitle {
  color: #666;
  margin: 0 0 20px 0;
}
.cert-table {
  width: 100%;
}
</style>
