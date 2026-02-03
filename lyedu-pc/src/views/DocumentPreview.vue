<template>
  <div class="document-preview-container">
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <img src="/icon-192.png" alt="" class="header-logo-icon" />
          <h1>LyEdu</h1>
        </div>
        <div class="title-row">
          <span class="doc-title">{{ pageTitle || '文档预览' }}</span>
          <el-button type="primary" link @click="handleDownload">下载</el-button>
        </div>
      </div>
    </el-header>
    <el-main class="main-content">
      <template v-if="isPdf && previewUrl">
        <iframe
          :src="previewUrl"
          class="preview-iframe"
          title="PDF 预览"
        />
      </template>
      <template v-else-if="previewUrl && !isPdf">
        <div class="unsupported-tip">
          <p>当前格式暂不支持在线预览，请下载后查看。</p>
          <el-button type="primary" @click="handleDownload">下载文件</el-button>
        </div>
      </template>
      <template v-else>
        <el-empty description="暂无预览地址" />
      </template>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const rawUrl = ref('')
const pageTitle = ref('')
const blobUrlRef = ref('')

const isPdf = computed(() => {
  const t = (route.query.type as string) || ''
  const name = (pageTitle.value || rawUrl.value || '').toLowerCase()
  return t === 'pdf' || name.endsWith('.pdf')
})

// 同源或可 CORS 的 PDF 用 iframe；跨域时尝试 fetch 转 blob 避免被 X-Frame-Options 拦截
const previewUrl = ref('')

async function ensurePreviewUrl() {
  const url = (route.query.url as string) || ''
  rawUrl.value = url
  pageTitle.value = (route.query.title as string) || '文档预览'
  if (!url) {
    previewUrl.value = ''
    return
  }
  if (!isPdf.value) {
    previewUrl.value = url
    return
  }
  try {
    const res = await fetch(url, { mode: 'cors', credentials: 'omit' })
    if (res.ok) {
      const blob = await res.blob()
      if (blobUrlRef.value) URL.revokeObjectURL(blobUrlRef.value)
      blobUrlRef.value = URL.createObjectURL(blob)
      previewUrl.value = blobUrlRef.value
    } else {
      previewUrl.value = url
    }
  } catch {
    previewUrl.value = url
  }
}

function handleDownload() {
  if (!rawUrl.value) return
  window.open(rawUrl.value, '_blank')
}

onMounted(ensurePreviewUrl)
watch(() => route.query, ensurePreviewUrl, { deep: true })
onUnmounted(() => {
  if (blobUrlRef.value) URL.revokeObjectURL(blobUrlRef.value)
})
</script>

<style scoped lang="scss">
.document-preview-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  .header {
    background: #fff;
    border-bottom: 1px solid #e4e7ed;
    padding: 0 24px;
  }
  .header-content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
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
  .title-row {
    display: flex;
    align-items: center;
    gap: 12px;
    .doc-title {
      font-size: 16px;
      color: #303133;
    }
  }
  .main-content {
    flex: 1;
    padding: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  .preview-iframe {
    flex: 1;
    width: 100%;
    border: none;
    min-height: 80vh;
  }
  .unsupported-tip {
    padding: 40px;
    text-align: center;
    color: #606266;
    p {
      margin-bottom: 16px;
    }
  }
}
</style>
