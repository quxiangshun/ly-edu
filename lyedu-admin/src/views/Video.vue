<template>
  <div class="video-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>视频管理</span>
          <el-button type="primary" @click="handleAdd">新增视频</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="课程ID">
          <el-input-number v-model="searchForm.courseId" :min="0" placeholder="请输入课程ID" clearable />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="请输入视频标题" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="videoList" v-loading="loading" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="courseId" label="课程ID" width="100" />
        <el-table-column prop="chapterId" label="章节ID" width="100" />
        <el-table-column prop="title" label="视频标题" />
        <el-table-column prop="url" label="视频地址" min-width="200">
          <template #default="{ row }">
            <el-link v-if="row.url" :href="row.url" target="_blank" type="primary">
              {{ row.url }}
            </el-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="时长（秒）" width="120" />
        <el-table-column prop="sort" label="排序" width="100" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
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

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="课程ID" prop="courseId">
          <el-input-number v-model="form.courseId" :min="1" placeholder="请输入课程ID" />
        </el-form-item>
        <el-form-item label="章节ID" prop="chapterId">
          <el-input-number v-model="form.chapterId" :min="0" placeholder="请输入章节ID（可选）" />
        </el-form-item>
        <el-form-item label="视频标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入视频标题" />
        </el-form-item>
        <el-form-item label="视频上传" prop="url">
          <chunk-upload
            accept="video/*"
            :chunk-size="5 * 1024 * 1024"
            @success="handleUploadSuccess"
            @error="handleUploadError"
          />
        </el-form-item>
        <el-form-item label="视频地址" prop="url">
          <el-input v-model="form.url" placeholder="视频上传成功后自动填充，或手动输入视频URL" />
        </el-form-item>
        <el-form-item label="时长（秒）" prop="duration">
          <el-input-number v-model="form.duration" :min="0" placeholder="请输入视频时长（秒）" />
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="form.sort" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import ChunkUpload from '@/components/ChunkUpload.vue'
import { getVideoPage, createVideo, updateVideo, deleteVideo, type Video } from '@/api/video'

const loading = ref(false)
const videoList = ref<Video[]>([])
const formRef = ref<FormInstance>()
const dialogVisible = ref(false)
const dialogTitle = ref('新增视频')
const isEdit = ref(false)

const searchForm = reactive({
  courseId: undefined,
  keyword: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const form = reactive<Partial<Video>>({
  courseId: undefined,
  chapterId: undefined,
  title: '',
  url: '',
  duration: 0,
  sort: 0
})

const rules: FormRules = {
  courseId: [{ required: true, message: '请输入课程ID', trigger: 'blur' }],
  title: [{ required: true, message: '请输入视频标题', trigger: 'blur' }],
  url: [{ required: true, message: '请上传视频或输入视频URL', trigger: 'blur' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      size: pagination.size
    }
    if (searchForm.courseId) {
      params.courseId = searchForm.courseId
    }
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }
    const res = await getVideoPage(params)
    videoList.value = res.records
    pagination.total = res.total
  } catch (e) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.courseId = undefined
  searchForm.keyword = ''
  handleSearch()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增视频'
  Object.assign(form, {
    courseId: undefined,
    chapterId: undefined,
    title: '',
    url: '',
    duration: 0,
    sort: 0
  })
  dialogVisible.value = true
}

const handleEdit = (row: Video) => {
  isEdit.value = true
  dialogTitle.value = '编辑视频'
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleDelete = async (row: Video) => {
  try {
    await ElMessageBox.confirm('确定要删除该视频吗？', '提示', {
      type: 'warning'
    })
    await deleteVideo(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // 用户取消或删除失败
  }
}

const handleUploadSuccess = (url: string) => {
  form.url = url
  ElMessage.success('视频上传成功！')
}

const handleUploadError = (error: string) => {
  ElMessage.error('视频上传失败：' + error)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  try {
    if (isEdit.value) {
      await updateVideo(form.id!, form)
      ElMessage.success('更新成功')
    } else {
      await createVideo(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || (isEdit.value ? '更新失败' : '创建失败'))
  }
}

const handleSizeChange = () => {
  loadData()
}

const handlePageChange = () => {
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.video-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}
</style>
