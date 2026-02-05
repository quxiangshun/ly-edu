<template>
  <div class="exam-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span>考试管理</span>
            <el-tooltip content="查看本模块使用说明" placement="right">
              <el-icon class="card-help-icon" @click="openPageHelp('exam')">
                <QuestionFilled />
              </el-icon>
            </el-tooltip>
          </div>
          <el-button type="primary" @click="handleAdd">新增考试</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="考试名称" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadList">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="examList" v-loading="loading" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="考试名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="paperId" label="试卷ID" width="90" />
        <el-table-column prop="startTime" label="开始时间" width="160">
          <template #default="{ row }">{{ row.startTime ? row.startTime.replace('T', ' ') : '-' }}</template>
        </el-table-column>
        <el-table-column prop="endTime" label="结束时间" width="160">
          <template #default="{ row }">{{ row.endTime ? row.endTime.replace('T', ' ') : '-' }}</template>
        </el-table-column>
        <el-table-column prop="visibility" label="可见性" width="90">
          <template #default="{ row }">
            <el-tag :type="row.visibility === 1 ? 'success' : 'warning'">
              {{ row.visibility === 1 ? '公开' : '私有' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">{{ row.status === 1 ? '上架' : '下架' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="handleRecords(row)">成绩</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadList"
        @current-change="loadList"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="考试名称" prop="title">
          <el-input v-model="form.title" placeholder="考试名称" />
        </el-form-item>
        <el-form-item label="试卷" prop="paperId">
          <el-select v-model="form.paperId" placeholder="请选择试卷" style="width: 100%" filterable>
            <el-option
              v-for="p in paperOptions"
              :key="p.id"
              :label="p.title"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间" prop="startTime">
          <el-date-picker
            v-model="form.startTime"
            type="datetime"
            value-format="YYYY-MM-DDTHH:mm:ss"
            placeholder="可选"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间" prop="endTime">
          <el-date-picker
            v-model="form.endTime"
            type="datetime"
            value-format="YYYY-MM-DDTHH:mm:ss"
            placeholder="可选"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="时长(分钟)" prop="durationMinutes">
          <el-input-number v-model="form.durationMinutes" :min="1" :max="300" placeholder="可选，取试卷默认" />
        </el-form-item>
        <el-form-item label="及格分" prop="passScore">
          <el-input-number v-model="form.passScore" :min="0" :max="1000" placeholder="可选" />
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
            placeholder="可多选"
            clearable
            check-strictly
            default-expand-all
            multiple
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">上架</el-radio>
            <el-radio :label="0">下架</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="recordsDialogVisible" :title="`成绩 - ${currentExam?.title || ''}`" width="720px">
      <el-table :data="recordList" border size="small">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="userId" label="用户ID" width="90" />
        <el-table-column prop="score" label="得分" width="80" />
        <el-table-column prop="passed" label="及格" width="80">
          <template #default="{ row }">
            <el-tag :type="row.passed === 1 ? 'success' : 'danger'">{{ row.passed === 1 ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="submitTime" label="交卷时间" width="170">
          <template #default="{ row }">{{ row.submitTime ? row.submitTime.replace('T', ' ') : '-' }}</template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="recordsDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import {
  getExamPage,
  getExamByIdAdmin,
  createExam,
  updateExam,
  deleteExam,
  getExamRecords,
  type Exam,
  type ExamRecord
} from '@/api/exam'
import { getPaperPage, type Paper } from '@/api/paper'
import { getDepartmentTree, type Department } from '@/api/department'
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
const departmentTreeOptions = computed(() => departmentTree.value || [])
const departmentNameMap = computed(() => {
  const flat = flattenDepartments(departmentTree.value || [])
  const map = new Map<number, string>()
  flat.forEach((d) => map.set(d.id, d.name))
  return map
})

const paperOptions = ref<Paper[]>([])
const examList = ref<Exam[]>([])
const formRef = ref<FormInstance>()
const dialogVisible = ref(false)
const dialogTitle = ref('新增考试')
const editId = ref<number | null>(null)
const recordsDialogVisible = ref(false)
const currentExam = ref<Exam | null>(null)
const recordList = ref<ExamRecord[]>([])

const { openPageHelp } = useHelp()

const searchForm = reactive({ keyword: '' })
const pagination = reactive({ page: 1, size: 10, total: 0 })

const form = reactive({
  title: '',
  paperId: 0,
  startTime: '',
  endTime: '',
  durationMinutes: undefined as number | undefined,
  passScore: undefined as number | undefined,
  visibility: 1,
  status: 1,
  departmentIds: [] as number[]
})

const formRules: FormRules = {
  title: [{ required: true, message: '请输入考试名称', trigger: 'blur' }],
  paperId: [{ required: true, message: '请选择试卷', trigger: 'change' }]
}

async function loadList() {
  loading.value = true
  try {
    const res = await getExamPage({
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword || undefined
    })
    examList.value = res?.records ?? []
    pagination.total = res?.total ?? 0
  } catch (_e) {
    examList.value = []
  } finally {
    loading.value = false
  }
}

function handleReset() {
  searchForm.keyword = ''
  pagination.page = 1
  loadList()
}

async function handleAdd() {
  editId.value = null
  dialogTitle.value = '新增考试'
  form.title = ''
  form.paperId = 0
  form.startTime = ''
  form.endTime = ''
  form.durationMinutes = undefined
  form.passScore = undefined
  form.visibility = 1
  form.status = 1
  form.departmentIds = []
  if (paperOptions.value.length === 0) {
    try {
      const res = await getPaperPage({ page: 1, size: 500 })
      paperOptions.value = res?.records ?? []
    } catch (_e) {
      paperOptions.value = []
    }
  }
  dialogVisible.value = true
}

async function handleEdit(row: Exam) {
  editId.value = row.id
  dialogTitle.value = '编辑考试'
  try {
    const e = await getExamByIdAdmin(row.id)
    form.title = e.title ?? ''
    form.paperId = e.paperId ?? 0
    form.startTime = e.startTime ?? ''
    form.endTime = e.endTime ?? ''
    form.durationMinutes = e.durationMinutes
    form.passScore = e.passScore
    form.visibility = e.visibility ?? 1
    form.status = e.status ?? 1
    form.departmentIds = Array.isArray(e.departmentIds) ? [...e.departmentIds] : []
    if (paperOptions.value.length === 0) {
      const res = await getPaperPage({ page: 1, size: 500 })
      paperOptions.value = res?.records ?? []
    }
  } catch (_e) {
    ElMessage.error('获取详情失败')
    return
  }
  dialogVisible.value = true
}

async function handleRecords(row: Exam) {
  currentExam.value = row
  try {
    const list = await getExamRecords(row.id)
    recordList.value = list ?? []
  } catch (_e) {
    recordList.value = []
  }
  recordsDialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      const payload = {
        title: form.title.trim(),
        paperId: form.paperId,
        startTime: form.startTime || undefined,
        endTime: form.endTime || undefined,
        durationMinutes: form.durationMinutes,
        passScore: form.passScore,
        visibility: form.visibility,
        status: form.status,
        departmentIds: form.visibility === 0 ? form.departmentIds : undefined
      }
      if (editId.value != null) {
        await updateExam(editId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createExam(payload)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      loadList()
    } catch (_e) {}
  })
}

function handleDelete(row: Exam) {
  ElMessageBox.confirm(`确定删除考试「${row.title}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteExam(row.id)
      ElMessage.success('删除成功')
      loadList()
    } catch (_e) {}
  }).catch(() => {})
}

onMounted(() => {
  loadList()
  getDepartmentTree().then((data) => {
    departmentTree.value = data ?? []
  }).catch(() => {
    departmentTree.value = []
  })
})
</script>

<style scoped lang="scss">
.exam-container .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.exam-container .search-form {
  margin-bottom: 16px;
}
</style>
