<template>
  <div class="knowledge-center-container">
    <van-nav-bar title="知识中心" left-arrow @click-left="$router.back()" fixed placeholder />
    <div class="content">
      <p class="subtitle">可下载的文档与资料</p>
      <van-list v-model:loading="loading" :finished="finished" finished-text="没有更多了" @load="loadList">
        <van-cell
          v-for="item in knowledgeList"
          :key="item.id"
          :title="item.title"
          :label="item.category ? `分类：${item.category}` : ''"
          is-link
          @click="handleDownload(item)"
        >
          <template #right-icon>
            <van-icon name="down" />
          </template>
        </van-cell>
        <van-empty v-if="!loading && knowledgeList.length === 0" description="暂无知识文档" />
      </van-list>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { showToast } from 'vant'
import { getKnowledgePage, type Knowledge } from '@/api/knowledge'

const loading = ref(false)
const finished = ref(false)
const knowledgeList = ref<Knowledge[]>([])
const page = ref(1)
const size = 20

async function loadList() {
  // 注意：van-list 使用 v-model:loading 时，触发 @load 时 loading 可能已被置为 true
  // 此处不要因为 loading=true 直接 return，否则会导致一直 loading
  if (finished.value) return
  if (!loading.value) loading.value = true
  try {
    const res = await getKnowledgePage({ page: page.value, size })
    const list = res?.records ?? []
    if (list.length > 0) {
      knowledgeList.value.push(...list)
      page.value++
    }
    if (list.length < size) {
      finished.value = true
    }
  } catch (_e) {
    finished.value = true
    showToast('加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

function handleDownload(row: Knowledge) {
  if (!row.fileUrl) {
    showToast('文件地址无效')
    return
  }
  window.open(row.fileUrl, '_blank')
  showToast('正在打开')
}

</script>

<style scoped lang="scss">
.knowledge-center-container {
  min-height: 100vh;
  padding-bottom: 20px;
  .content {
    padding: 16px;
    .subtitle {
      color: #969799;
      margin: 0 0 12px;
      font-size: 14px;
    }
  }
}
</style>
