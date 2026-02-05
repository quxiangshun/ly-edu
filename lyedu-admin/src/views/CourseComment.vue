<template>
  <div class="comment-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span>评论管理</span>
            <el-tooltip content="查看本模块使用说明" placement="right">
              <el-icon class="card-help-icon" @click="openPageHelp('course-comment')">
                <QuestionFilled />
              </el-icon>
            </el-tooltip>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="评论内容/用户名" clearable />
        </el-form-item>
        <el-form-item label="课程ID">
          <el-input-number v-model="searchForm.courseId" :min="1" placeholder="课程ID" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="显示" :value="1" />
            <el-option label="隐藏" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="commentList" v-loading="loading" border :max-height="tableMaxHeight">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="courseTitle" label="课程" min-width="150" show-overflow-tooltip />
        <el-table-column prop="userRealName" label="用户" width="120">
          <template #default="{ row }">
            {{ row.userRealName || row.username || '未知用户' }}
          </template>
        </el-table-column>
        <el-table-column prop="content" label="评论内容" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'warning'">
              {{ row.status === 1 ? '显示' : '隐藏' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="deleted" label="删除状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.deleted === 0 ? 'success' : 'danger'">
              {{ row.deleted === 0 ? '正常' : '已删除' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.createTime) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 1"
              type="warning"
              link
              size="small"
              @click="handleHide(row)"
            >
              隐藏
            </el-button>
            <el-button
              v-else
              type="success"
              link
              size="small"
              @click="handleShow(row)"
            >
              显示
            </el-button>
            <el-button
              v-if="row.deleted === 0"
              type="danger"
              link
              size="small"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import { getCommentPage, deleteComment, updateCommentStatus, type CourseComment } from '@/api/courseComment'
import { useHelp } from '@/hooks/useHelp'
import { useTableMaxHeight } from '@/hooks/useTableHeight'

const tableMaxHeight = useTableMaxHeight()
const { openPageHelp } = useHelp()

const loading = ref(false)
const commentList = ref<CourseComment[]>([])

const searchForm = reactive({
  keyword: '',
  courseId: undefined as number | undefined,
  status: undefined as number | undefined
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

function formatTime(time?: string): string {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

async function loadComments() {
  loading.value = true
  try {
    const res = await getCommentPage({
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword || undefined,
      courseId: searchForm.courseId,
      status: searchForm.status
    })
    commentList.value = res.records || []
    pagination.total = res.total || 0
  } catch (error: any) {
    ElMessage.error(error?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadComments()
}

function handleReset() {
  searchForm.keyword = ''
  searchForm.courseId = undefined
  searchForm.status = undefined
  pagination.page = 1
  loadComments()
}

function handleSizeChange(size: number) {
  pagination.size = size
  pagination.page = 1
  loadComments()
}

function handlePageChange(page: number) {
  pagination.page = page
  loadComments()
}

async function handleHide(row: CourseComment) {
  try {
    await ElMessageBox.confirm('确定要隐藏这条评论吗？隐藏后用户将无法看到。', '提示', {
      type: 'warning'
    })
    await updateCommentStatus(row.id, 0)
    ElMessage.success('已隐藏')
    loadComments()
  } catch {
    // 用户取消
  }
}

async function handleShow(row: CourseComment) {
  try {
    await updateCommentStatus(row.id, 1)
    ElMessage.success('已显示')
    loadComments()
  } catch (error: any) {
    ElMessage.error(error?.message || '操作失败')
  }
}

async function handleDelete(row: CourseComment) {
  try {
    await ElMessageBox.confirm('确定要删除这条评论吗？删除后用户将无法看到。', '提示', {
      type: 'warning'
    })
    await deleteComment(row.id)
    ElMessage.success('已删除')
    loadComments()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.message || '删除失败')
    }
  }
}

onMounted(() => {
  loadComments()
})
</script>

<style scoped lang="scss">
.comment-container {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .card-header-left {
    display: flex;
    align-items: center;
    gap: 8px;

    .card-help-icon {
      font-size: 16px;
      color: #909399;
      cursor: pointer;
      transition: color 0.3s;

      &:hover {
        color: var(--el-color-primary);
      }
    }
  }
}

.search-form {
  margin-bottom: 20px;
}
</style>
