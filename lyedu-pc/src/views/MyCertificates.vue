<template>
  <div class="my-certificates-container">
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <img src="/icon-192.png" alt="" class="header-logo-icon" />
          <h1>LyEdu</h1>
        </div>
        <el-menu mode="horizontal" default-active="certificates" class="header-menu">
          <el-menu-item index="home" @click="$router.push('/')">首页</el-menu-item>
          <el-menu-item index="courses" @click="$router.push('/courses')">课程中心</el-menu-item>
          <el-menu-item index="knowledge" @click="$router.push('/knowledge')">知识中心</el-menu-item>
          <el-menu-item index="exam" @click="$router.push('/exam')">考试中心</el-menu-item>
          <el-menu-item index="certificates">我的证书</el-menu-item>
          <el-menu-item index="my" @click="$router.push('/my-learning')">我的学习</el-menu-item>
        </el-menu>
      </div>
    </el-header>
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
.header {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  padding: 0;
  height: 56px;
}
.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  margin-right: 32px;
}
.header-logo-icon {
  width: 32px;
  height: 32px;
}
.header-menu {
  flex: 1;
  border: none;
}
.main-content {
  flex: 1;
  padding: 24px 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
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
