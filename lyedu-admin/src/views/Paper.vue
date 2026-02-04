<template>
  <div class="paper-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>试卷管理</span>
          <el-button type="primary" @click="handleAdd">新增试卷</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="试卷名称" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadList">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="paperList" v-loading="loading" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="试卷名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="totalScore" label="总分" width="80" />
        <el-table-column prop="passScore" label="及格分" width="90" />
        <el-table-column prop="durationMinutes" label="时长(分钟)" width="110" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
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
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadList"
        @current-change="loadList"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="680px">
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="试卷名称" prop="title">
          <el-input v-model="form.title" placeholder="试卷名称" />
        </el-form-item>
        <el-form-item label="总分" prop="totalScore">
          <span class="total-score-text">{{ computedTotalScore }} 分</span>
          <span class="total-score-tip">（根据题目分值自动计算）</span>
        </el-form-item>
        <el-form-item label="及格分" prop="passScore">
          <el-input-number v-model="form.passScore" :min="0" :max="1000" />
        </el-form-item>
        <el-form-item label="时长(分钟)" prop="durationMinutes">
          <el-input-number v-model="form.durationMinutes" :min="1" :max="300" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="题目">
          <div class="question-list-actions">
            <el-button type="primary" size="small" @click="openQuestionPicker">添加题目</el-button>
          </div>
          <el-table :data="form.questions" border size="small" max-height="280">
            <el-table-column type="index" label="#" width="50" />
            <el-table-column prop="title" label="题干" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">{{ questionTitleMap[row.questionId] || row.questionId }}</template>
            </el-table-column>
            <el-table-column label="分值" width="100">
              <template #default="{ row, $index }">
                <el-input-number v-model="form.questions[$index].score" :min="1" :max="100" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ row, $index }">
                <el-button type="danger" link size="small" @click="removeQuestion($index)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="questionPickerVisible" title="选择题目" width="720px">
      <el-form :inline="true">
        <el-form-item>
          <el-input v-model="pickerKeyword" placeholder="题干关键词" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadPickerQuestions">搜索</el-button>
        </el-form-item>
      </el-form>
      <el-table
        ref="pickerTableRef"
        :data="pickerQuestionList"
        border
        max-height="360"
        @selection-change="pickerSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="type" label="题型" width="80">
          <template #default="{ row }">{{ typeLabel(row.type) }}</template>
        </el-table-column>
        <el-table-column prop="title" label="题干" min-width="200" show-overflow-tooltip />
        <el-table-column prop="score" label="分值" width="70" />
      </el-table>
      <template #footer>
        <el-button @click="questionPickerVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmPickQuestions">确定添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  getPaperPage,
  getPaperById,
  getPaperQuestions,
  createPaper,
  updatePaper,
  deletePaper,
  type Paper,
  type PaperQuestionItem
} from '@/api/paper'
import { getQuestionPage, type Question } from '@/api/question'

const typeLabels: Record<string, string> = {
  single: '单选',
  multi: '多选',
  judge: '判断',
  fill: '填空',
  short: '简答'
}
function typeLabel(type: string) {
  return typeLabels[type] || type
}

const loading = ref(false)
const paperList = ref<Paper[]>([])
const formRef = ref<FormInstance>()
const dialogVisible = ref(false)
const dialogTitle = ref('新增试卷')
const editId = ref<number | null>(null)
const questionTitleMap = ref<Record<number, string>>({})

const searchForm = reactive({ keyword: '' })
const pagination = reactive({ page: 1, size: 10, total: 0 })

const form = reactive({
  title: '',
  totalScore: 100,
  passScore: 60,
  durationMinutes: 60,
  status: 1,
  questions: [] as (PaperQuestionItem & { title?: string })[]
})

const formRules: FormRules = {
  title: [{ required: true, message: '请输入试卷名称', trigger: 'blur' }]
}

/** 根据当前题目列表的分值自动计算总分 */
const computedTotalScore = computed(() =>
  form.questions.reduce((sum, q) => sum + (q.score ?? 10), 0)
)

const questionPickerVisible = ref(false)
const pickerKeyword = ref('')
const pickerQuestionList = ref<Question[]>([])
const pickerSelected = ref<Question[]>([])
const pickerTableRef = ref()

async function loadList() {
  loading.value = true
  try {
    const res = await getPaperPage({
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword || undefined
    })
    paperList.value = res?.records ?? []
    pagination.total = res?.total ?? 0
  } catch (_e) {
    paperList.value = []
  } finally {
    loading.value = false
  }
}

function handleReset() {
  searchForm.keyword = ''
  pagination.page = 1
  loadList()
}

function handleAdd() {
  editId.value = null
  dialogTitle.value = '新增试卷'
  form.title = ''
  form.totalScore = 100
  form.passScore = 60
  form.durationMinutes = 60
  form.status = 1
  form.questions = []
  questionTitleMap.value = {}
  dialogVisible.value = true
}

async function handleEdit(row: Paper) {
  editId.value = row.id
  dialogTitle.value = '编辑试卷'
  try {
    const p = await getPaperById(row.id)
    form.title = p.title ?? ''
    form.totalScore = p.totalScore ?? 100
    form.passScore = p.passScore ?? 60
    form.durationMinutes = p.durationMinutes ?? 60
    form.status = p.status ?? 1
    const items = await getPaperQuestions(row.id)
    form.questions = (items ?? []).map((x) => ({
      questionId: x.questionId,
      score: x.score ?? 10,
      sort: x.sort ?? 0
    }))
    const map: Record<number, string> = {}
    items?.forEach((x) => {
      if (x.question?.title) map[x.questionId] = x.question.title
    })
    questionTitleMap.value = map
  } catch (_e) {
    ElMessage.error('获取详情失败')
    return
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      const payload = {
        title: form.title.trim(),
        totalScore: form.totalScore,
        passScore: form.passScore,
        durationMinutes: form.durationMinutes,
        status: form.status,
        questions: form.questions.map((q, i) => ({
          questionId: q.questionId,
          score: q.score ?? 10,
          sort: i
        }))
      }
      if (editId.value != null) {
        await updatePaper(editId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createPaper(payload)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      loadList()
    } catch (_e) {}
  })
}

function handleDelete(row: Paper) {
  ElMessageBox.confirm(`确定删除试卷「${row.title}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deletePaper(row.id)
      ElMessage.success('删除成功')
      loadList()
    } catch (_e) {}
  }).catch(() => {})
}

function removeQuestion(index: number) {
  form.questions.splice(index, 1)
}

function openQuestionPicker() {
  pickerKeyword.value = ''
  pickerQuestionList.value = []
  pickerSelected.value = []
  loadPickerQuestions()
  questionPickerVisible.value = true
}

async function loadPickerQuestions() {
  try {
    const res = await getQuestionPage({
      page: 1,
      size: 200,
      keyword: pickerKeyword.value || undefined
    })
    pickerQuestionList.value = res?.records ?? []
  } catch (_e) {
    pickerQuestionList.value = []
  }
}

function pickerSelectionChange(rows: Question[]) {
  pickerSelected.value = rows
}

function confirmPickQuestions() {
  const existingIds = new Set(form.questions.map((q) => q.questionId))
  for (const q of pickerSelected.value) {
    if (existingIds.has(q.id)) continue
    existingIds.add(q.id)
    form.questions.push({
      questionId: q.id,
      score: q.score ?? 10,
      sort: form.questions.length
    })
    questionTitleMap.value[q.id] = q.title ?? ''
  }
  questionPickerVisible.value = false
}

onMounted(loadList)
</script>

<style scoped lang="scss">
.paper-container .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.paper-container .search-form {
  margin-bottom: 16px;
}
.question-list-actions {
  margin-bottom: 8px;
}
.total-score-text {
  font-weight: 600;
  color: var(--el-color-primary);
  margin-right: 8px;
}
.total-score-tip {
  font-size: 12px;
  color: #909399;
}
</style>
