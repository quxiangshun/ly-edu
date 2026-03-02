<template>
  <div class="paper-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span>试卷管理</span>
            <el-tooltip content="查看本模块使用说明" placement="right">
              <el-icon class="card-help-icon" @click="openPageHelp('paper')">
                <QuestionFilled />
              </el-icon>
            </el-tooltip>
          </div>
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

      <el-table :data="paperList" v-loading="loading" border stripe :max-height="tableMaxHeight">
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px" :close-on-click-modal="false">
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
            <el-button type="primary" size="small" @click="openQuestionPicker">选择已有题目</el-button>
            <el-button size="small" @click="openImportFileDialog">上传试题</el-button>
            <el-button size="small" @click="openPasteJsonDialog">粘贴 JSON</el-button>
          </div>
          <el-table :data="form.questions" border stripe size="small" max-height="280">
            <el-table-column type="index" label="#" width="50" />
            <el-table-column label="来源" width="72">
              <template #default="{ row }">
                <el-tag v-if="row.questionId" type="info" size="small">已有</el-tag>
                <el-tag v-else type="success" size="small">新建</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="题干" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">{{ row.questionId ? (questionTitleMap[row.questionId] ?? row.questionId) : (row.title || '') }}</template>
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

    <el-dialog v-model="questionPickerVisible" title="选择题目" width="800px" :close-on-click-modal="false">
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
        stripe
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

    <el-dialog v-model="importFileDialogVisible" title="上传试题加入试卷" width="800px" :close-on-click-modal="false">
      <p class="import-tip">
        请先
        <el-dropdown trigger="click" @command="handleDownloadTemplateByType">
          <a href="javascript:;">下载模板</a>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="xlsx">Excel 模板</el-dropdown-item>
              <el-dropdown-item command="csv">CSV 模板</el-dropdown-item>
              <el-dropdown-item command="json">JSON 模板</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        ，再选择 .xlsx / .csv / .json 文件，解析预览后点击「添加至试卷」将题目加入当前试卷（保存试卷时与试卷一起创建）。
      </p>
      <el-upload
        ref="importFileUploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.csv,.json"
        :on-change="onImportFileChange"
        :on-exceed="() => ElMessage.warning('仅支持单文件')"
      >
        <el-button type="primary" size="small">选择文件</el-button>
      </el-upload>
      <div v-if="importFileLoading" class="import-preview-loading">正在解析…</div>
      <div v-else-if="importFilePreviewError" class="import-preview-error">{{ importFilePreviewError }}</div>
      <template v-else-if="importFilePreviewRows.length > 0">
        <p class="import-preview-title">共 {{ importFilePreviewRows.length }} 条，确认后点击「添加至试卷」。</p>
        <el-table :data="importFilePreviewRows" border size="small" max-height="220">
          <el-table-column prop="0" label="题型" width="80" />
          <el-table-column prop="1" label="题干" min-width="180" show-overflow-tooltip />
          <el-table-column prop="3" label="参考答案" width="88" show-overflow-tooltip />
          <el-table-column prop="4" label="分值" width="64" />
        </el-table>
        <el-button type="primary" size="small" @click="confirmAddImportFileToPaper" style="margin-top: 8px">
          添加至试卷
        </el-button>
      </template>
      <template #footer>
        <el-button @click="importFileDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="pasteJsonDialogVisible" title="粘贴 JSON 加入试卷" width="800px" :close-on-click-modal="false">
      <p class="import-tip">
        请先
        <el-dropdown trigger="click" @command="handleDownloadTemplateByType">
          <a href="javascript:;">下载模板</a>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="xlsx">Excel 模板</el-dropdown-item>
              <el-dropdown-item command="csv">CSV 模板</el-dropdown-item>
              <el-dropdown-item command="json">JSON 模板</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        ，再粘贴试题 JSON 数组，点击「添加至试卷」将题目加入当前试卷（保存试卷时与试卷一起创建）。
      </p>
      <el-input
        v-model="pasteJsonText"
        type="textarea"
        :rows="14"
        placeholder='[{"题型":"单选","题干":"题目？","选项(JSON)":"[\"A\",\"B\"]","参考答案":"A","分值":10,"解析":"","排序":0}]'
        class="import-json-textarea"
      />
      <el-button type="primary" size="small" :loading="pasteJsonLoading" @click="confirmAddPasteJsonToPaper" style="margin-top: 8px">
        添加至试卷
      </el-button>
      <template #footer>
        <el-button @click="pasteJsonDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import * as XLSX from 'xlsx'
import { QuestionFilled } from '@element-plus/icons-vue'
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
import { useHelp } from '@/hooks/useHelp'
import { useTableMaxHeight } from '@/hooks/useTableHeight'

const QUESTION_IMPORT_HEADERS = ['题型', '题干', '选项(JSON)', '参考答案', '分值', '解析', '排序']
const QUESTION_IMPORT_EXAMPLES = [
  ['单选', '以下哪项是 LyEdu 平台的主要功能？', '["A. 仅视频播放","B. 在线学习与考试","C. 仅文档管理","D. 仅聊天"]', 'B', 5, 'LyEdu 为企业培训平台，支持课程学习、考试、证书等完整学习流程。', 10],
  ['多选', '以下哪些属于 LyEdu 的典型功能？（多选）', '["A. 课程与章节","B. 试卷与考试","C. 证书与积分","D. 社交论坛"]', 'ABC', 10, '平台包含课程、考试、证书、积分等，暂无内置社交论坛。', 20],
  ['判断', '学员完成培训任务后可以自动获得证书。', '["正确","错误"]', 'T', 5, '任务可配置完成后颁发证书，由管理员在任务中设置。', 30],
  ['填空', 'LyEdu 中试题表名为 ly_____。（填一个单词）', '', 'question', 5, '试题表名为 ly_question。', 40],
  ['简答', '请简述 LyEdu 平台中「周期任务」的典型应用场景。', '', '用于新员工入职培训、定期安全考试、年度考核等需要按周期或一次性完成的学习与考核任务。', 10, '周期任务可配置闯关内容（课程/考试）、完成证书、指派部门等。', 50]
]
const TYPE_CN_TO_EN: Record<string, string> = {
  单选: 'single',
  多选: 'multi',
  判断: 'judge',
  填空: 'fill',
  简答: 'short'
}

const tableMaxHeight = useTableMaxHeight()
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

const { openPageHelp } = useHelp()

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

const importFileDialogVisible = ref(false)
const importFileUploadRef = ref()
const importFilePreviewRows = ref<string[][]>([])
const importFilePreviewError = ref('')
const importFileLoading = ref(false)
const importSelectedFile = ref<File | null>(null)

const pasteJsonDialogVisible = ref(false)
const pasteJsonText = ref('')
const pasteJsonLoading = ref(false)

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
      const questions = form.questions.map((q, i) => {
        const score = q.score ?? 10
        const sort = i
        if (q.questionId != null) {
          return { questionId: q.questionId, score, sort }
        }
        return {
          type: q.type ?? 'single',
          title: (q.title ?? '').trim(),
          options: q.options,
          answer: q.answer,
          score,
          analysis: q.analysis,
          sort
        }
      })
      const payload = {
        title: form.title.trim(),
        totalScore: form.totalScore,
        passScore: form.passScore,
        durationMinutes: form.durationMinutes,
        status: form.status,
        questions
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
  const existingIds = new Set(form.questions.map((q) => q.questionId).filter((id): id is number => id != null))
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

function parseCsvLine(line: string): string[] {
  const out: string[] = []
  let i = 0
  while (i < line.length) {
    if (line[i] === '"') {
      let cell = ''
      i++
      while (i < line.length) {
        if (line[i] === '"') {
          i++
          if (line[i] === '"') { cell += '"'; i++ } else break
        } else { cell += line[i]; i++ }
      }
      out.push(cell)
    } else {
      let cell = ''
      while (i < line.length && line[i] !== ',') { cell += line[i]; i++ }
      out.push(cell.trim())
      if (line[i] === ',') i++
    }
  }
  return out
}

async function parseFileForPreview(file: File): Promise<{ rows: string[][] } | { error: string }> {
  const fn = file.name.toLowerCase()
  try {
    if (fn.endsWith('.xlsx')) {
      const buf = await file.arrayBuffer()
      const wb = XLSX.read(buf, { type: 'array' })
      const sheet = wb.Sheets[wb.SheetNames[0]]
      if (!sheet) return { error: '文件为空' }
      const data = XLSX.utils.sheet_to_json<string[]>(sheet, { header: 1 }) as string[][]
      if (!data.length) return { error: '文件为空' }
      const rows = data.slice(1).filter((row) => row && row.some((c) => c != null && String(c).trim() !== ''))
      const normalized = rows.map((row) => {
        const r = [...(row || [])]
        while (r.length < 7) r.push('')
        return r.slice(0, 7).map((c) => (c != null ? String(c).trim() : ''))
      })
      return { rows: normalized }
    }
    if (fn.endsWith('.csv')) {
      const text = await file.text()
      const lines = text.split(/\r?\n/).filter((l) => l.trim())
      if (lines.length < 2) return { error: '文件为空或仅有表头' }
      const rows = lines.slice(1).map((line) => {
        const arr = parseCsvLine(line).map((s) => (s != null ? String(s).trim() : ''))
        if (arr.length > 7) {
          const merged = [
            arr[0],
            arr[1],
            arr.slice(2, -4).join(','),
            arr[arr.length - 4],
            arr[arr.length - 3],
            arr[arr.length - 2],
            arr[arr.length - 1]
          ]
          return merged
        }
        while (arr.length < 7) arr.push('')
        return arr.slice(0, 7)
      }).filter((row) => row.some((c) => c !== ''))
      return { rows }
    }
    if (fn.endsWith('.json')) {
      const text = await file.text()
      const data = JSON.parse(text)
      if (!Array.isArray(data)) return { error: 'JSON 根节点须为数组' }
      const keys = ['题型', '题干', '选项(JSON)', '参考答案', '分值', '解析', '排序']
      const enKeys = ['type', 'title', 'options', 'answer', 'score', 'analysis', 'sort']
      const rows = data.map((item: Record<string, unknown>) => {
        const row: string[] = []
        keys.forEach((k, i) => {
          const v = item[k] ?? item[enKeys[i]]
          if (v == null) row.push('')
          else if (typeof v === 'object') row.push(JSON.stringify(v))
          else row.push(String(v).trim())
        })
        while (row.length < 7) row.push('')
        return row.slice(0, 7)
      })
      return { rows }
    }
    return { error: '不支持的文件格式' }
  } catch (e: any) {
    return { error: e?.message || '解析失败' }
  }
}

function rowToPaperQuestionItem(row: string[]): PaperQuestionItem & { title?: string } {
  const typeCn = (row[0] || '').trim()
  const typeEn = TYPE_CN_TO_EN[typeCn] || 'single'
  const title = (row[1] || '').trim()
  const options = (row[2] || '').trim() || undefined
  const answer = (row[3] || '').trim() || undefined
  const score = parseInt(String(row[4] || '10'), 10) || 10
  const analysis = (row[5] || '').trim() || undefined
  const sort = parseInt(String(row[6] || '0'), 10) || 0
  return {
    type: typeEn,
    title,
    options: options || undefined,
    answer,
    score,
    analysis,
    sort
  }
}

function fitColWidths(rows: (string | number)[][]): { wch: number }[] {
  if (!rows.length) return []
  const colCount = Math.max(...rows.map((r) => r.length))
  const widths: number[] = new Array(colCount).fill(0)
  for (const row of rows) {
    for (let c = 0; c < row.length; c++) {
      const s = row[c] != null ? String(row[c]) : ''
      const len = [...s].reduce((acc, ch) => acc + (ch.charCodeAt(0) > 255 ? 2 : 1), 0)
      widths[c] = Math.max(widths[c], Math.min(len + 1, 80))
    }
  }
  return widths.map((w) => ({ wch: Math.max(w, 6) }))
}

function csvEscape(cell: string | number): string {
  const s = String(cell)
  if (/[",\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`
  return s
}

function handleDownloadTemplateByType(format: 'xlsx' | 'csv' | 'json') {
  if (format === 'xlsx') {
    const rows = [QUESTION_IMPORT_HEADERS, ...QUESTION_IMPORT_EXAMPLES]
    const ws = XLSX.utils.aoa_to_sheet(rows)
    ws['!cols'] = fitColWidths(rows)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '试题导入')
    XLSX.writeFile(wb, '试题上传模板.xlsx')
    return
  }
  if (format === 'csv') {
    const rows = [QUESTION_IMPORT_HEADERS, ...QUESTION_IMPORT_EXAMPLES]
    const line = (row: (string | number)[]) => row.map(csvEscape).join(',')
    const csvContent = '\uFEFF' + rows.map(line).join('\r\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '试题上传模板.csv'
    a.click()
    URL.revokeObjectURL(url)
    return
  }
  if (format === 'json') {
    const keys = QUESTION_IMPORT_HEADERS
    const items = QUESTION_IMPORT_EXAMPLES.map((row) => {
      const obj: Record<string, string | number> = {}
      keys.forEach((k, i) => { obj[k] = row[i] != null ? row[i] : '' })
      return obj
    })
    const jsonContent = JSON.stringify(items, null, 2)
    const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '试题上传模板.json'
    a.click()
    URL.revokeObjectURL(url)
  }
}

function openImportFileDialog() {
  importFilePreviewRows.value = []
  importFilePreviewError.value = ''
  importSelectedFile.value = null
  importFileUploadRef.value?.clearFiles?.()
  importFileDialogVisible.value = true
}

async function onImportFileChange(uploadFile: { raw?: File }) {
  const file = uploadFile?.raw
  if (!file) return
  importFilePreviewError.value = ''
  importFilePreviewRows.value = []
  importSelectedFile.value = file
  importFileLoading.value = true
  try {
    const result = await parseFileForPreview(file)
    if ('error' in result) {
      importFilePreviewError.value = result.error
    } else {
      importFilePreviewRows.value = result.rows
    }
  } finally {
    importFileLoading.value = false
  }
}

function confirmAddImportFileToPaper() {
  for (const row of importFilePreviewRows.value) {
    form.questions.push(rowToPaperQuestionItem(row))
  }
  ElMessage.success(`已添加 ${importFilePreviewRows.value.length} 道题至试卷`)
  importFilePreviewRows.value = []
  importFileDialogVisible.value = false
  importFileUploadRef.value?.clearFiles?.()
}

function openPasteJsonDialog() {
  pasteJsonText.value = ''
  pasteJsonDialogVisible.value = true
}

async function confirmAddPasteJsonToPaper() {
  const raw = pasteJsonText.value.trim()
  if (!raw) {
    ElMessage.warning('请先粘贴 JSON 数组')
    return
  }
  pasteJsonLoading.value = true
  try {
    const data = JSON.parse(raw) as Record<string, unknown>[]
    if (!Array.isArray(data)) {
      ElMessage.error('JSON 须为数组')
      return
    }
    const keys = ['题型', '题干', '选项(JSON)', '参考答案', '分值', '解析', '排序']
    const enKeys = ['type', 'title', 'options', 'answer', 'score', 'analysis', 'sort']
    let added = 0
    for (const item of data) {
      if (!item || typeof item !== 'object') continue
      const row = keys.map((k, i) => {
        const v = item[k] ?? item[enKeys[i]]
        if (v == null) return ''
        if (typeof v === 'object') return JSON.stringify(v)
        return String(v).trim()
      })
      while (row.length < 7) row.push('')
      const typeCn = (row[0] || '').trim()
      const typeEn = TYPE_CN_TO_EN[typeCn] || typeCn || 'single'
      const title = (row[1] || '').trim()
      if (!title) continue
      form.questions.push({
        type: typeEn,
        title,
        options: (row[2] || '').trim() || undefined,
        answer: (row[3] || '').trim() || undefined,
        score: parseInt(String(row[4] || '10'), 10) || 10,
        analysis: (row[5] || '').trim() || undefined,
        sort: parseInt(String(row[6] || '0'), 10) || 0
      })
      added++
    }
    ElMessage.success(`已添加 ${added} 道题至试卷`)
    pasteJsonDialogVisible.value = false
  } catch (e: any) {
    if (e?.message?.includes('JSON')) ElMessage.error('JSON 格式错误')
    else ElMessage.error(e?.message || '解析失败')
  } finally {
    pasteJsonLoading.value = false
  }
}

onMounted(loadList)
</script>

<style scoped lang="scss">
.paper-container {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.paper-container .card-header {
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

.import-tip {
  margin-bottom: 12px;
  font-size: 13px;
  color: var(--el-text-color-regular);
  a { color: var(--el-color-primary); }
}
.import-preview-loading {
  margin-top: 12px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
.import-preview-error {
  margin-top: 12px;
  color: var(--el-color-danger);
  font-size: 13px;
}
.import-preview-title {
  margin: 12px 0 8px;
  font-size: 13px;
  color: var(--el-text-color-regular);
}
.import-json-textarea {
  font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, monospace;
  font-size: 13px;
}
</style>
