<template>
  <div class="image-library-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>图片库</span>
          <span class="card-desc">用于课程封面等，支持 jpg/png/gif/webp</span>
          <el-upload
            :show-file-list="false"
            :before-upload="beforeUpload"
            :http-request="handleUpload"
            accept=".jpg,.jpeg,.png,.gif,.webp"
          >
            <el-button type="primary">上传图片</el-button>
          </el-upload>
        </div>
      </template>

      <el-form :inline="true" class="search-form">
        <el-form-item>
          <el-input v-model="keyword" placeholder="按文件名搜索" clearable style="width: 200px" @clear="loadList" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadList">搜索</el-button>
        </el-form-item>
      </el-form>

      <div class="image-grid" v-loading="loading">
        <div v-for="item in imageList" :key="item.id" class="image-item">
          <el-image :src="imageUrl(item)" fit="cover" class="thumb" />
          <div class="meta">{{ item.name }}</div>
          <div class="actions">
            <el-button type="primary" link size="small" @click="copyUrl(item)">复制链接</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(item)">删除</el-button>
          </div>
        </div>
        <el-empty v-if="!loading && imageList.length === 0" description="暂无图片" />
      </div>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[12, 24, 48]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadList"
        @current-change="loadList"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getImagePage, uploadImage, deleteImage, type ImageItem, type ImagePageResult } from '@/api/image'

const loading = ref(false)
const keyword = ref('')
const imageList = ref<ImageItem[]>([])
const pagination = reactive({ page: 1, size: 24, total: 0 })

function imageUrl(item: ImageItem) {
  const url = item.url
  if (!url) return ''
  if (url.startsWith('http')) return url
  return window.location.origin + url
}

async function loadList() {
  loading.value = true
  try {
    const res = await getImagePage({
      page: pagination.page,
      size: pagination.size,
      keyword: keyword.value || undefined
    })
    const data = (res as unknown as { data?: ImagePageResult })?.data ?? res
    imageList.value = data?.records ?? []
    pagination.total = data?.total ?? 0
  } catch (_e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function beforeUpload(file: File) {
  const ok = /\.(jpe?g|png|gif|webp)$/i.test(file.name)
  if (!ok) {
    ElMessage.error('仅支持 jpg/png/gif/webp')
    return false
  }
  return true
}

async function handleUpload({ file }: { file: File }) {
  try {
    await uploadImage(file)
    ElMessage.success('上传成功')
    loadList()
  } catch (_e) {
    ElMessage.error('上传失败')
  }
}

function copyUrl(item: ImageItem) {
  const url = item.url?.startsWith('http') ? item.url : (window.location.origin + (item.url || ''))
  navigator.clipboard.writeText(url).then(() => ElMessage.success('已复制链接'))
}

function handleDelete(item: ImageItem) {
  ElMessageBox.confirm('确定删除该图片？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await deleteImage(item.id)
      ElMessage.success('已删除')
      loadList()
    } catch (_e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(loadList)
</script>

<style scoped lang="scss">
.image-library-container {
  .card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    .card-desc {
      color: #909399;
      font-size: 13px;
    }
  }
  .search-form {
    margin-bottom: 16px;
  }
  .image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 16px;
    min-height: 120px;
  }
  .image-item {
    border: 1px solid #ebeef5;
    border-radius: 8px;
    overflow: hidden;
    .thumb {
      width: 100%;
      height: 100px;
      display: block;
      background: #f5f7fa;
    }
    .meta {
      padding: 6px 8px;
      font-size: 12px;
      color: #606266;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .actions {
      padding: 4px 8px 8px;
      display: flex;
      gap: 4px;
      flex-wrap: wrap;
    }
  }
}
</style>
