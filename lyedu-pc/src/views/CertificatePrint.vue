<template>
  <div class="certificate-print-container">
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <img src="/icon-192.png" alt="" class="header-logo-icon" />
          <h1>LyEdu</h1>
        </div>
        <el-menu mode="horizontal" default-active="certificates" class="header-menu">
          <el-menu-item index="home" @click="$router.push('/')">首页</el-menu-item>
          <el-menu-item index="certificates" @click="$router.push('/certificates')">我的证书</el-menu-item>
        </el-menu>
        <div class="actions">
          <el-button type="primary" @click="handlePrint" :loading="loading">打印</el-button>
          <el-button @click="$router.push('/certificates')">返回列表</el-button>
        </div>
      </div>
    </el-header>
    <el-main class="main-content">
      <div v-if="loading" class="loading-wrap">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      <div v-else-if="detail" class="certificate-paper" id="certificate-paper">
        <div class="certificate-inner">
          <h1 class="cert-title">{{ detail.userCertificate?.title || '合格证书' }}</h1>
          <p class="cert-no">证书编号：{{ detail.userCertificate?.certificateNo }}</p>
          <p class="cert-issued">颁发时间：{{ detail.userCertificate?.issuedAt ? formatTime(detail.userCertificate.issuedAt) : '' }}</p>
          <p class="cert-desc" v-if="detail.template?.description">{{ detail.template.description }}</p>
        </div>
      </div>
      <el-empty v-else description="证书不存在或无权查看" />
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { getCertificateDetail, type UserCertificateWithTemplate } from '@/api/userCertificate'

const route = useRoute()
const loading = ref(true)
const detail = ref<UserCertificateWithTemplate | null>(null)

const id = computed(() => Number(route.params.id))

function formatTime(s: string) {
  if (!s) return ''
  return s.replace('T', ' ').slice(0, 19)
}

async function loadDetail() {
  if (!id.value) {
    loading.value = false
    return
  }
  loading.value = true
  try {
    const res = await getCertificateDetail(id.value)
    detail.value = (res as unknown as { data: UserCertificateWithTemplate }).data ?? res ?? null
  } catch (e) {
    ElMessage.error('加载证书失败')
    detail.value = null
  } finally {
    loading.value = false
  }
}

function handlePrint() {
  window.print()
}

onMounted(() => loadDetail())
</script>

<style scoped>
.certificate-print-container {
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
  margin-right: 24px;
}
.header-logo-icon {
  width: 32px;
  height: 32px;
}
.header-menu {
  flex: 1;
  border: none;
}
.actions {
  display: flex;
  gap: 12px;
}
.main-content {
  flex: 1;
  padding: 24px 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}
.loading-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
}
.certificate-paper {
  width: 100%;
  max-width: 800px;
  min-height: 480px;
  border: 2px solid #c9a227;
  border-radius: 8px;
  padding: 48px;
  background: linear-gradient(135deg, #fffef8 0%, #fff9e6 100%);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}
.certificate-inner {
  text-align: center;
  padding: 24px 0;
}
.cert-title {
  font-size: 28px;
  margin: 0 0 24px 0;
  color: #333;
}
.cert-no {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px 0;
}
.cert-issued {
  font-size: 14px;
  color: #666;
  margin: 0 0 16px 0;
}
.cert-desc {
  font-size: 13px;
  color: #888;
  margin: 0;
}

@media print {
  .header {
    display: none !important;
  }
  .certificate-print-container .main-content {
    padding: 0;
  }
  .certificate-paper {
    box-shadow: none;
    border: 2px solid #333;
  }
}
</style>
