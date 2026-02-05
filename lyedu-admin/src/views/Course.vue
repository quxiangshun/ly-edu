<template>
  <div class="course-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span>课程管理</span>
            <el-tooltip content="查看本模块使用说明" placement="right">
              <el-icon class="card-help-icon" @click="openPageHelp('course')">
                <QuestionFilled />
              </el-icon>
            </el-tooltip>
          </div>
          <el-button type="primary" @click="handleAdd">新增课程</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="请输入课程名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="courseList" v-loading="loading" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="课程名称" />
        <el-table-column prop="cover" label="封面">
          <template #default="{ row }">
            <el-image v-if="row.cover" :src="row.cover" style="width: 60px; height: 40px" fit="cover" />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="visibility" label="可见性" width="90">
          <template #default="{ row }">
            <el-tag :type="row.visibility === 1 ? 'success' : 'warning'">
              {{ row.visibility === 1 ? '公开' : '私有' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort" label="排序" width="100" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="handleChapters(row)">章节</el-button>
            <el-button type="primary" link @click="handleAttachments(row)">附件</el-button>
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

    <!-- 章节管理对话框 -->
    <el-dialog v-model="chapterDialogVisible" :title="`章节管理 - ${currentCourse?.title || ''}`" width="640px">
      <el-button type="primary" size="small" @click="handleAddChapter" style="margin-bottom: 12px">新增章节</el-button>
      <el-table :data="chapterList" border size="small">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="章节名称" />
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEditChapter(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDeleteChapter(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="chapterDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="chapterFormVisible" :title="chapterFormId ? '编辑章节' : '新增章节'" width="400px">
      <el-form :model="chapterForm" label-width="80px">
        <el-form-item label="章节名称">
          <el-input v-model="chapterForm.title" placeholder="章节名称（1-64字）" maxlength="64" show-word-limit />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="chapterForm.sort" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="chapterFormVisible = false">取消</el-button>
        <el-button type="primary" @click="submitChapter">确定</el-button>
      </template>
    </el-dialog>

    <!-- 附件管理对话框 -->
    <el-dialog v-model="attachmentDialogVisible" :title="`附件管理 - ${currentCourse?.title || ''}`" width="720px">
      <el-button type="primary" size="small" @click="handleAddAttachment" style="margin-bottom: 12px">新增附件</el-button>
      <el-table :data="attachmentList" border size="small">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="附件名称" />
        <el-table-column prop="type" label="类型" width="80" />
        <el-table-column prop="fileUrl" label="文件地址" min-width="180" show-overflow-tooltip />
        <el-table-column prop="sort" label="排序" width="70" />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button type="danger" link size="small" @click="handleDeleteAttachment(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="attachmentDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="attachmentFormVisible" title="新增附件" width="440px">
      <el-form :model="attachmentForm" label-width="90px">
        <el-form-item label="附件名称">
          <el-input v-model="attachmentForm.name" placeholder="附件名称" />
        </el-form-item>
        <el-form-item label="类型/扩展名">
          <el-input v-model="attachmentForm.type" placeholder="如 txt、pdf（可选）" />
        </el-form-item>
        <el-form-item label="文件地址">
          <el-input v-model="attachmentForm.fileUrl" placeholder="文件 URL" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="attachmentForm.sort" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="attachmentFormVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAttachment">确定</el-button>
      </template>
    </el-dialog>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="课程名称" prop="title">
          <el-input v-model="form.title" placeholder="请输入课程名称" />
        </el-form-item>
        <el-form-item label="课程封面" prop="cover">
          <el-input v-model="form.cover" placeholder="请输入封面URL或从图片库选择" class="cover-input">
            <template #append>
              <el-button @click="openImageSelect">从图片库选择</el-button>
            </template>
          </el-input>
          <el-image v-if="form.cover" :src="coverDisplayUrl" style="width: 120px; height: 80px; margin-top: 8px; border-radius: 4px" fit="cover" />
        </el-form-item>
        <el-form-item label="课程描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入课程描述" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">上架</el-radio>
            <el-radio :label="0">下架</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="必修/选修" prop="isRequired">
          <el-radio-group v-model="form.isRequired">
            <el-radio :label="0">选修</el-radio>
            <el-radio :label="1">必修</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="可见性" prop="visibility">
          <el-radio-group v-model="form.visibility">
            <el-radio :label="1">公开</el-radio>
            <el-radio :label="0">私有</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="form.visibility === 0" label="关联部门" prop="departmentIds">
          <el-tree-select
            v-model="form.departmentIds"
            :data="departmentTreeOptions"
            :props="{ label: 'name', value: 'id' }"
            placeholder="可多选关联部门"
            clearable
            check-strictly
            default-expand-all
            multiple
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="关联考试">
          <el-select
            v-model="selectedExamId"
            filterable
            clearable
            placeholder="可选择一场考试"
            style="width: 100%"
            :loading="examOptionsLoading"
          >
            <el-option v-for="e in examOptions" :key="e.id" :label="e.title" :value="e.id" />
          </el-select>
          <div class="form-tip">一门课程可关联一场考试；同一考试可被多门课程使用</div>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import { getCoursePage, createCourse, updateCourse, deleteCourse, getCourseExam, setCourseExam, type Course } from '@/api/course'
import { getDepartmentTree, type Department } from '@/api/department'
import {
  getChaptersByCourseId,
  createChapter,
  updateChapter,
  deleteChapter,
  type Chapter
} from '@/api/chapter'
import {
  getAttachmentsByCourseId,
  createAttachment,
  deleteAttachment,
  type CourseAttachment
} from '@/api/courseAttachment'
import { getImagePage, type ImageItem, type ImagePageResult } from '@/api/image'
import { getExamPage, type Exam } from '@/api/exam'
import { useHelp } from '@/hooks/useHelp'

function flattenDepartments(list: Department[]): Department[] {
  const out: Department[] = []
  function walk(items: Department[]) {
    for (const d of items) {
      out.push(d)
      if (d.children?.length) walk(d.children)
    }
  }
  walk(list)
  return out
}

const loading = ref(false)
const departmentTree = ref<Department[]>([])
const currentCourse = ref<Course | null>(null)
const examOptions = ref<Exam[]>([])
const examOptionsLoading = ref(false)
const selectedExamId = ref<number | null>(null)

const departmentTreeOptions = computed(() => departmentTree.value || [])

const departmentNameMap = computed(() => {
  const flat = flattenDepartments(departmentTree.value || [])
  const map = new Map<number, string>()
  flat.forEach((d) => map.set(d.id, d.name))
  return map
})
const chapterDialogVisible = ref(false)
const chapterList = ref<Chapter[]>([])
const chapterFormVisible = ref(false)
const chapterFormId = ref<number | null>(null)
const chapterForm = reactive({ title: '', sort: 0 })
const attachmentDialogVisible = ref(false)
const attachmentList = ref<CourseAttachment[]>([])
const attachmentFormVisible = ref(false)
const attachmentForm = reactive({ name: '', type: '', fileUrl: '', sort: 0 })
const courseList = ref<Course[]>([])
const formRef = ref<FormInstance>()
const dialogVisible = ref(false)
const dialogTitle = ref('新增课程')
const isEdit = ref(false)
const { openPageHelp } = useHelp()

const searchForm = reactive({
  keyword: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const form = reactive<Partial<Course>>({
  title: '',
  cover: '',
  description: '',
  status: 1,
  sort: 0,
  isRequired: 0,
  visibility: 1,
  departmentIds: []
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  departmentIds: [
    {
      validator: (_rule: unknown, value: unknown, callback: (err?: Error) => void) => {
        if (form.visibility === 0 && (!Array.isArray(value) || value.length === 0)) {
          callback(new Error('私有课程请至少选择一个关联部门'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

const imageSelectVisible = ref(false)
const imageKeyword = ref('')
const imageSelectList = ref<ImageItem[]>([])
const imageListLoading = ref(false)
const imageSelectPage = ref(1)
const imageSelectSize = ref(12)
const imageSelectTotal = ref(0)

const coverDisplayUrl = computed(() => {
  const u = form.cover
  if (!u) return ''
  return u.startsWith('http') ? u : window.location.origin + u
})

function imageItemUrl(item: ImageItem) {
  const u = item.url
  if (!u) return ''
  return u.startsWith('http') ? u : window.location.origin + u
}

function openImageSelect() {
  imageSelectVisible.value = true
  imageSelectPage.value = 1
  loadImageList()
}

async function loadImageList() {
  imageListLoading.value = true
  try {
    const res = await getImagePage({
      page: imageSelectPage.value,
      size: imageSelectSize.value,
      keyword: imageKeyword.value || undefined
    })
    const data = (res as unknown as { data?: ImagePageResult })?.data ?? res
    imageSelectList.value = data?.records ?? []
    imageSelectTotal.value = data?.total ?? 0
  } catch (_e) {
    imageSelectList.value = []
  } finally {
    imageListLoading.value = false
  }
}

function chooseCover(item: ImageItem) {
  form.cover = item.url || ''
  imageSelectVisible.value = false
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getCoursePage({
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword || undefined
    })
    courseList.value = res.records
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
  searchForm.keyword = ''
  handleSearch()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增课程'
  Object.assign(form, {
    title: '',
    cover: '',
    description: '',
    status: 1,
    sort: 0,
    isRequired: 0,
    visibility: 1,
    departmentIds: []
  })
  selectedExamId.value = null
  dialogVisible.value = true
}

const handleEdit = async (row: Course) => {
  isEdit.value = true
  dialogTitle.value = '编辑课程'
  Object.assign(form, row)
  selectedExamId.value = null
  dialogVisible.value = true
  examOptionsLoading.value = true
  try {
    const [examPage, cid] = await Promise.all([
      getExamPage({ page: 1, size: 200 }),
      getCourseExam(row.id)
    ])
    examOptions.value = examPage?.records || []
    selectedExamId.value = cid ?? null
  } catch {
    examOptions.value = []
    selectedExamId.value = null
  } finally {
    examOptionsLoading.value = false
  }
}

const handleDelete = async (row: Course) => {
  try {
    await ElMessageBox.confirm('确定要删除该课程吗？', '提示', {
      type: 'warning'
    })
    await deleteCourse(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // 用户取消或删除失败
  }
}

const handleChapters = async (row: Course) => {
  currentCourse.value = row
  chapterDialogVisible.value = true
  try {
    const list = await getChaptersByCourseId(row.id)
    chapterList.value = Array.isArray(list) ? list : []
  } catch (e) {
    ElMessage.error('加载章节失败')
    chapterList.value = []
  }
}

const handleAddChapter = () => {
  chapterFormId.value = null
  chapterForm.title = ''
  chapterForm.sort = chapterList.value.length
  chapterFormVisible.value = true
}

const handleEditChapter = (row: Chapter) => {
  chapterFormId.value = row.id
  chapterForm.title = row.title
  chapterForm.sort = row.sort
  chapterFormVisible.value = true
}

const handleDeleteChapter = async (row: Chapter) => {
  try {
    await ElMessageBox.confirm('确定删除该章节？', '提示', { type: 'warning' })
    await deleteChapter(row.id)
    ElMessage.success('删除成功')
    if (currentCourse.value) chapterList.value = await getChaptersByCourseId(currentCourse.value.id)
  } catch (e) {}
}

const submitChapter = async () => {
  if (!currentCourse.value) return
  if (!chapterForm.title?.trim()) {
    ElMessage.warning('请输入章节名称')
    return
  }
  try {
    if (chapterFormId.value) {
      await updateChapter(chapterFormId.value, { title: chapterForm.title.trim(), sort: chapterForm.sort })
      ElMessage.success('更新成功')
    } else {
      await createChapter({ courseId: currentCourse.value.id, title: chapterForm.title.trim(), sort: chapterForm.sort })
      ElMessage.success('新增成功')
    }
    chapterFormVisible.value = false
    const list = await getChaptersByCourseId(currentCourse.value.id)
    chapterList.value = Array.isArray(list) ? list : []
  } catch (e) {
    ElMessage.error(chapterFormId.value ? '更新失败' : '新增失败')
  }
}

const handleAttachments = async (row: Course) => {
  currentCourse.value = row
  attachmentDialogVisible.value = true
  try {
    const list = await getAttachmentsByCourseId(row.id)
    attachmentList.value = Array.isArray(list) ? list : []
  } catch (e) {
    ElMessage.error('加载附件失败')
    attachmentList.value = []
  }
}

const handleAddAttachment = () => {
  attachmentForm.name = ''
  attachmentForm.type = ''
  attachmentForm.fileUrl = ''
  attachmentForm.sort = attachmentList.value.length
  attachmentFormVisible.value = true
}

const handleDeleteAttachment = async (row: CourseAttachment) => {
  try {
    await ElMessageBox.confirm('确定删除该附件？', '提示', { type: 'warning' })
    await deleteAttachment(row.id)
    ElMessage.success('删除成功')
    if (currentCourse.value) {
      const list = await getAttachmentsByCourseId(currentCourse.value.id)
      attachmentList.value = Array.isArray(list) ? list : []
    }
  } catch (e) {}
}

const submitAttachment = async () => {
  if (!currentCourse.value) return
  if (!attachmentForm.name?.trim() || !attachmentForm.fileUrl?.trim()) {
    ElMessage.warning('请填写附件名称和文件地址')
    return
  }
  try {
    await createAttachment({
      courseId: currentCourse.value.id,
      name: attachmentForm.name.trim(),
      type: attachmentForm.type?.trim() || undefined,
      fileUrl: attachmentForm.fileUrl.trim(),
      sort: attachmentForm.sort
    })
    ElMessage.success('新增成功')
    attachmentFormVisible.value = false
    const list = await getAttachmentsByCourseId(currentCourse.value.id)
    attachmentList.value = Array.isArray(list) ? list : []
  } catch (e) {
    ElMessage.error('新增失败')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  try {
    if (isEdit.value) {
      await updateCourse(form.id!, form)
      await setCourseExam(form.id!, selectedExamId.value ?? null)
      ElMessage.success('更新成功')
    } else {
      await createCourse(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  }
}

const handleSizeChange = () => {
  loadData()
}

const handlePageChange = () => {
  loadData()
}

onMounted(async () => {
  try {
    departmentTree.value = await getDepartmentTree()
  } catch {
    departmentTree.value = []
  }
  loadData()
})
</script>

<style scoped lang="scss">
.course-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .card-header-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .card-help-icon {
    font-size: 16px;
    cursor: pointer;
    color: #909399;

    &:hover {
      color: var(--el-color-primary);
    }
  }
}

.search-form {
  margin-bottom: 20px;
}

.image-select-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  max-height: 360px;
  overflow-y: auto;
}

.image-select-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s;
  &:hover {
    border-color: var(--el-color-primary);
  }
  .select-thumb {
    width: 100%;
    height: 80px;
    display: block;
    background: #f5f7fa;
  }
  .select-name {
    display: block;
    padding: 6px 8px;
    font-size: 12px;
    color: #606266;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>
