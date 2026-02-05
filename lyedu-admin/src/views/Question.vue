<template>
  <div class="question-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span>试题管理</span>
            <el-tooltip content="查看本模块使用说明" placement="right">
              <el-icon class="card-help-icon" @click="openPageHelp('question')">
                <QuestionFilled />
              </el-icon>
            </el-tooltip>
          </div>
          <el-button type="primary" @click="handleAdd">新增试题</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="题干" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="题型">
          <el-select v-model="searchForm.type" placeholder="全部" clearable style="width: 120px">
            <el-option label="单选" value="single" />
            <el-option label="多选" value="multi" />
            <el-option label="判断" value="judge" />
            <el-option label="填空" value="fill" />
            <el-option label="简答" value="short" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadList">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="questionList" v-loading="loading" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="type" label="题型" width="90">
          <template #default="{ row }">{{ typeLabel(row.type) }}</template>
        </el-table-column>
        <el-table-column prop="title" label="题干" min-width="280" show-overflow-tooltip />
        <el-table-column prop="score" label="分值" width="80" />
        <el-table-column prop="sort" label="排序" width="80" />
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
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadList"
        @current-change="loadList"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="640px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px">
        <el-form-item label="题型" prop="type">
          <el-select v-model="form.type" placeholder="请选择题型" style="width: 100%">
            <el-option label="单选" value="single" />
            <el-option label="多选" value="multi" />
            <el-option label="判断" value="judge" />
            <el-option label="填空" value="fill" />
            <el-option label="简答" value="short" />
          </el-select>
        </el-form-item>
        <el-form-item label="题干" prop="title">
          <el-input v-model="form.title" type="textarea" :rows="3" placeholder="题目标题/题干" />
        </el-form-item>
        <el-form-item v-if="['single','multi','judge'].includes(form.type)" label="选项(JSON)" prop="options">
          <el-input v-model="form.options" type="textarea" :rows="2" placeholder='如 ["A选项","B选项","C选项","D选项"] 或 判断 ["正确","错误"]' />
        </el-form-item>
        <el-form-item label="参考答案" prop="answer">
          <el-input v-model="form.answer" placeholder="单选填A/B/C/D，多选填AB，判断填T/F，填空/简答填文本" />
        </el-form-item>
        <el-form-item label="分值" prop="score">
          <el-input-number v-model="form.score" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="解析" prop="analysis">
          <el-input v-model="form.analysis" type="textarea" :rows="2" placeholder="可选" />
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
import { QuestionFilled } from '@element-plus/icons-vue'
import {
  getQuestionPage,
  getQuestionById,
  createQuestion,
  updateQuestion,
  deleteQuestion,
  type Question
} from '@/api/question'
import { useHelp } from '@/hooks/useHelp'

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
const questionList = ref<Question[]>([])
const formRef = ref<FormInstance>()
const dialogVisible = ref(false)
const dialogTitle = ref('新增试题')
const editId = ref<number | null>(null)

const searchForm = reactive({ keyword: '', type: '' })
const pagination = reactive({ page: 1, size: 10, total: 0 })

const { openPageHelp } = useHelp()

const form = reactive({
  type: 'single',
  title: '',
  options: '',
  answer: '',
  score: 10,
  analysis: '',
  sort: 0
})

const rules: FormRules = {
  type: [{ required: true, message: '请选择题型', trigger: 'change' }],
  title: [{ required: true, message: '请输入题干', trigger: 'blur' }]
}

async function loadList() {
  loading.value = true
  try {
    const res = await getQuestionPage({
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword || undefined,
      type: searchForm.type || undefined
    })
    questionList.value = res?.records ?? []
    pagination.total = res?.total ?? 0
  } catch (_e) {
    questionList.value = []
  } finally {
    loading.value = false
  }
}

function handleReset() {
  searchForm.keyword = ''
  searchForm.type = ''
  pagination.page = 1
  loadList()
}

function handleAdd() {
  editId.value = null
  dialogTitle.value = '新增试题'
  form.type = 'single'
  form.title = ''
  form.options = ''
  form.answer = ''
  form.score = 10
  form.analysis = ''
  form.sort = 0
  dialogVisible.value = true
}

async function handleEdit(row: Question) {
  editId.value = row.id
  dialogTitle.value = '编辑试题'
  try {
    const q = await getQuestionById(row.id)
    form.type = q.type ?? 'single'
    form.title = q.title ?? ''
    form.options = q.options ?? ''
    form.answer = q.answer ?? ''
    form.score = q.score ?? 10
    form.analysis = q.analysis ?? ''
    form.sort = q.sort ?? 0
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
        type: form.type,
        title: form.title.trim(),
        options: form.options.trim() || undefined,
        answer: form.answer.trim() || undefined,
        score: form.score,
        analysis: form.analysis.trim() || undefined,
        sort: form.sort
      }
      if (editId.value != null) {
        await updateQuestion(editId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createQuestion(payload)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      loadList()
    } catch (_e) {}
  })
}

function handleDelete(row: Question) {
  ElMessageBox.confirm(`确定删除该试题吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteQuestion(row.id)
      ElMessage.success('删除成功')
      loadList()
    } catch (_e) {}
  }).catch(() => {})
}

onMounted(loadList)
</script>

<style scoped lang="scss">
.question-container .card-header {
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
.question-container .search-form {
  margin-bottom: 16px;
}
</style>
