<template>
  <div class="knowledge-center-container">
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <img src="/icon-192.png" alt="" class="header-logo-icon" />
          <h1>LyEdu</h1>
        </div>
        <el-menu mode="horizontal" default-active="knowledge" class="header-menu">
          <el-menu-item index="home" @click="$router.push('/')">首页</el-menu-item>
          <el-menu-item index="courses" @click="$router.push('/courses')">课程中心</el-menu-item>
          <el-menu-item index="knowledge">知识中心</el-menu-item>
          <el-menu-item index="exam" @click="$router.push('/exam')">考试中心</el-menu-item>
          <el-menu-item index="certificates" @click="$router.push('/certificates')">我的证书</el-menu-item>
          <el-menu-item index="my" @click="$router.push('/my-learning')">我的学习</el-menu-item>
        </el-menu>
      </div>
    </el-header>
    <el-main class="main-content">
      <div class="knowledge-content">
        <h2>知识中心</h2>
        <p class="subtitle">可下载的文档与资料（按部门可见）</p>
        <el-form :inline="true" class="search-form">
          <el-form-item>
            <el-input v-model="searchForm.keyword" placeholder="搜索标题/分类" clearable style="width: 200px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadList">搜索</el-button>
          </el-form-item>
        </el-form>
        <el-table :data="knowledgeList" v-loading="loading" border class="knowledge-table">
          <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
          <el-table-column prop="category" label="分类" width="120">
            <template #default="{ row }">{{ row.category || '-' }}</template>
          </el-table-column>
          <el-table-column prop="fileType" label="类型" width="80">
            <template #default="{ row }">{{ row.fileType || '-' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button v-if="isPdf(row)" type="primary" link @click="handlePreview(row)">预览</el-button>
              <el-button type="primary" link @click="handleDownload(row)">下载</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          layout="prev, pager, next"
          @current-change="loadList"
          style="margin-top: 20px; justify-content: center"
        />
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getKnowledgePage, type Knowledge } from '@/api/knowledge'

const router = useRouter()

function isPdf(row: Knowledge) {
  const t = (row.fileType || '').toLowerCase()
  const name = (row.fileName || row.title || '').toLowerCase()
  return t === 'pdf' || name.endsWith('.pdf')
}

function handlePreview(row: Knowledge) {
  if (!row.fileUrl) {
    ElMessage.warning('文件地址无效')
    return
  }
  router.push({
    path: '/preview',
    query: {
      url: row.fileUrl,
      title: row.title || row.fileName || '文档',
      type: 'pdf'
    }
  })
}

const loading = ref(false)
const knowledgeList = ref<Knowledge[]>([])
const searchForm = reactive({ keyword: '' })
const pagination = reactive({ page: 1, size: 15, total: 0 })

async function loadList() {
  loading.value = true
  try {
    const res = await getKnowledgePage({
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword || undefined
    })
    knowledgeList.value = res?.records ?? []
    pagination.total = res?.total ?? 0
  } catch (_e) {
    knowledgeList.value = []
  } finally {
    loading.value = false
  }
}

function handleDownload(row: Knowledge) {
  if (!row.fileUrl) return
  const url = row.fileUrl
  const ext = (row.fileType || '').toLowerCase()
  const name = row.fileName || row.title || 'download'
  if (ext === 'txt' || name.toLowerCase().endsWith('.txt')) {
    fetch(url)
      .then((r) => r.blob())
      .then((blob) => {
        const a = document.createElement('a')
        a.href = URL.createObjectURL(blob)
        a.download = name.includes('.') ? name : name + '.txt'
        a.click()
        URL.revokeObjectURL(a.href)
      })
      .catch(() => ElMessage.error('下载失败'))
  } else {
    window.open(url, '_blank')
  }
}

onMounted(() => loadList())
</script>

<style scoped lang="scss">
.knowledge-center-container {
  min-height: 100vh;
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
  .main-content {
    max-width: 1000px;
    margin: 0 auto;
    padding: 24px 16px;
  }
  .knowledge-content {
    h2 {
      margin: 0 0 8px;
    }
    .subtitle {
      color: #909399;
      margin: 0 0 20px;
    }
    .search-form {
      margin-bottom: 16px;
    }
    .knowledge-table {
      width: 100%;
    }
  }
}
</style>
