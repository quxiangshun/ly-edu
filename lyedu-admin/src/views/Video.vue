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
        <el-form-item label="课程">
          <el-select
            v-model="searchForm.courseId"
            filterable
            clearable
            placeholder="搜索选择课程"
            style="width: 240px"
            :loading="courseSearchLoading"
            remote
            :remote-method="searchCourseOptions"
            @focus="searchCourseOptions('')"
          >
            <el-option
              v-for="c in courseOptions"
              :key="c.id"
              :label="c.title"
              :value="c.id"
            />
          </el-select>
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
        <el-table-column prop="courseName" label="课程名称" min-width="120" show-overflow-tooltip />
        <el-table-column prop="chapterName" label="章节名称" min-width="120" show-overflow-tooltip />
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px" @opened="onDialogOpened">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="课程" prop="courseId">
          <el-select
            v-model="form.courseId"
            filterable
            clearable
            placeholder="搜索选择课程"
            style="width: 100%"
            :loading="courseSearchLoading"
            remote
            :remote-method="searchCourseOptions"
            @change="onCourseChange"
          >
            <el-option
              v-for="c in courseOptions"
              :key="c.id"
              :label="c.title"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="章节" prop="chapterId">
          <el-select
            v-model="form.chapterId"
            clearable
            placeholder="先选择课程后可选章节"
            style="width: 100%"
            :loading="chapterLoading"
            :disabled="!form.courseId"
          >
            <el-option label="无章节" :value="0" />
            <el-option
              v-for="ch in chapterOptions"
              :key="ch.value"
              :label="ch.label"
              :value="ch.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="视频标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入视频标题" />
        </el-form-item>
        <el-form-item label="视频上传" prop="url">
          <chunk-upload
            accept="video/*"
            :chunk-size="10 * 1024 * 1024"
            @success="handleUploadSuccess"
            @error="handleUploadError"
            @file-select="onVideoFileSelect"
          />
        </el-form-item>
        <el-form-item label="视频地址" prop="url">
          <el-input v-model="form.url" placeholder="视频上传成功后自动填充，或手动输入视频URL" />
        </el-form-item>
        <el-form-item label="时长（秒）" prop="duration">
          <el-input-number v-model="form.duration" :min="0" :disabled="durationAutoFilled" placeholder="选择视频后自动获取，或手动输入" />
          <span v-if="durationAutoFilled" class="duration-tip">已自动获取（不可修改）</span>
        </el-form-item>
        <video ref="videoEl" style="display: none" preload="metadata" />
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
import { getCoursePage, getCourseById, type Course } from '@/api/course'
import { getChaptersByCourseId } from '@/api/chapter'

const loading = ref(false)
const videoList = ref<Video[]>([])
const formRef = ref<FormInstance>()
const dialogVisible = ref(false)
const dialogTitle = ref('新增视频')
const isEdit = ref(false)
const courseOptions = ref<Course[]>([])
const chapterOptions = ref<{ label: string; value: number }[]>([])
const courseSearchLoading = ref(false)
const chapterLoading = ref(false)
const videoEl = ref<HTMLVideoElement | null>(null)
const durationAutoFilled = ref(false)

const searchForm = reactive<{ courseId?: number; keyword: string }>({
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
  courseId: [{ required: true, message: '请选择课程', trigger: 'change' }],
  title: [{ required: true, message: '请输入视频标题', trigger: 'blur' }],
  url: [{ required: true, message: '请上传视频或输入视频URL', trigger: 'blur' }]
}

const searchCourseOptions = async (query: string) => {
  courseSearchLoading.value = true
  try {
    const res = await getCoursePage({ page: 1, size: 50, keyword: query || undefined })
    courseOptions.value = res.records || []
  } catch {
    courseOptions.value = []
  } finally {
    courseSearchLoading.value = false
  }
}

const loadChapterOptions = async (courseId: number | undefined) => {
  if (!courseId) {
    chapterOptions.value = []
    return
  }
  chapterLoading.value = true
  try {
    const list = await getChaptersByCourseId(courseId)
    chapterOptions.value = (list || []).map((c) => ({ label: c.title, value: c.id }))
  } catch {
    chapterOptions.value = []
  } finally {
    chapterLoading.value = false
  }
}

const onCourseChange = () => {
  form.chapterId = 0
  loadChapterOptions(form.courseId)
}

const onDialogOpened = async () => {
  await searchCourseOptions('')
  if (form.courseId) {
    const inList = courseOptions.value.some((c) => c.id === form.courseId)
    if (!inList) {
      try {
        const course = await getCourseById(form.courseId)
        if (course) courseOptions.value = [course, ...courseOptions.value]
      } catch {
        // ignore
      }
    }
    await loadChapterOptions(form.courseId)
  } else {
    chapterOptions.value = []
  }
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
  durationAutoFilled.value = false
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
  const courseId = row.courseId ?? (row as any).course_id
  const chapterId = row.chapterId ?? (row as any).chapter_id ?? 0
  Object.assign(form, {
    ...row,
    courseId,
    chapterId: chapterId ?? 0
  })
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

const onVideoFileSelect = (file: File) => {
  durationAutoFilled.value = false
  form.duration = 0
  if (!file.type.startsWith('video/')) return
  const url = URL.createObjectURL(file)
  const video = videoEl.value
  if (!video) {
    URL.revokeObjectURL(url)
    return
  }
  const onLoaded = () => {
    const d = Math.round(video.duration)
    if (d > 0 && isFinite(d)) {
      form.duration = d
      durationAutoFilled.value = true
    }
    URL.revokeObjectURL(url)
    video.removeEventListener('loadedmetadata', onLoaded)
    video.removeEventListener('error', onErr)
    video.src = ''
  }
  const onErr = () => {
    URL.revokeObjectURL(url)
    video.removeEventListener('loadedmetadata', onLoaded)
    video.removeEventListener('error', onErr)
    video.src = ''
  }
  video.addEventListener('loadedmetadata', onLoaded)
  video.addEventListener('error', onErr)
  video.src = url
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
  const payload = {
    ...form,
    chapterId: form.chapterId === 0 ? undefined : form.chapterId
  }
  try {
    if (isEdit.value) {
      await updateVideo(form.id!, payload)
      ElMessage.success('更新成功')
    } else {
      await createVideo(payload)
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

.duration-tip {
  margin-left: 8px;
  font-size: 12px;
  color: var(--el-color-success);
}
</style>
